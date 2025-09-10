#!/usr/bin/env python3
import os
import sys
import json
import time
import random
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple

# Ensure backend module path
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Ensure Pacman repo path
PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")
if PACMAN_REPO not in sys.path:
    sys.path.insert(0, PACMAN_REPO)

# Pacman imports for evaluation
import layout as layout_module  # type: ignore
from pacman import ClassicGameRules  # type: ignore
import textDisplay  # type: ignore
from ghostAgents import RandomGhost, DirectionalGhost  # type: ignore

from custom_agents import SaveLoadApproximateQAgent
from training import train_approx_agent, models_dir


@dataclass
class HPOConfig:
    epsilon: float
    alpha: float
    gamma: float
    episodes: int


def _lookup_ghost(name: str):
    if name == "DirectionalGhost":
        return DirectionalGhost
    if name == "RandomGhost":
        return RandomGhost
    return RandomGhost


def _eval_model(layout_name: str, model_path: str, ghost_agent: str, num_ghosts: int, episodes: int, seed: int | None, timeout: int = 30) -> Dict[str, Any]:
    """Evaluate a saved model for a fixed number of episodes; return score stats."""
    if seed is not None:
        random.seed(seed)
    layout_path = os.path.join(PACMAN_REPO, 'layouts', f'{layout_name}.lay')
    lay = layout_module.tryToLoad(layout_path)
    if lay is None:
        lay = layout_module.getLayout(layout_name)
    if lay is None:
        raise ValueError(f"Layout not found: {layout_name}")
    GhostCls = _lookup_ghost(ghost_agent)

    rules = ClassicGameRules(timeout)
    display = textDisplay.NullGraphics()

    scores: List[float] = []
    wins = 0
    losses = 0

    for ep in range(episodes):
        # Fresh agent per evaluation episode to avoid side-effects
        pacman = SaveLoadApproximateQAgent(loadPath=model_path, extractor='SimpleExtractor', epsilon=0.0, alpha=0.0, gamma=0.8)
        ghosts = [GhostCls(i + 1) for i in range(num_ghosts)]
        game = rules.newGame(lay, pacman, ghosts, display, quiet=True, catchExceptions=False)
        for agent in game.agents:
            if hasattr(agent, 'registerInitialState'):
                agent.registerInitialState(game.state.deepCopy())
        game.run()
        s = game.state.getScore()
        scores.append(float(s))
        if game.state.isWin():
            wins += 1
        if game.state.isLose():
            losses += 1
    avg = sum(scores) / max(1, len(scores))
    return {"avgScore": avg, "wins": wins, "losses": losses, "scores": scores}


def _cfg_key(cfg: HPOConfig) -> str:
    return f"eps{cfg.epsilon}-a{cfg.alpha}-g{cfg.gamma}-ep{cfg.episodes}"


def hpo_search(
    layout: str,
    ghost_agent: str = "DirectionalGhost",
    num_ghosts: int = 4,
    coarse_episodes: int = 300,
    coarse_seeds: int = 3,
    test_episodes: int = 20,
    final_episodes: int = 1500,
    final_seeds: int = 5,
    final_test_episodes: int = 50,
    timeout: int = 30,
) -> Dict[str, Any]:
    os.makedirs(models_dir(), exist_ok=True)

    # Grid
    epsilons = [0.05, 0.1, 0.2]
    alphas = [0.1, 0.2, 0.3]
    gammas = [0.8, 0.9]

    coarse_results: Dict[str, Any] = {}

    # Coarse search over grid
    for eps in epsilons:
        for a in alphas:
            for g in gammas:
                cfg = HPOConfig(epsilon=eps, alpha=a, gamma=g, episodes=coarse_episodes)
                key = _cfg_key(cfg)
                print(f"[HPO] Coarse train cfg={key}")
                sys.stdout.flush()
                seed_avgs: List[float] = []
                seed_paths: List[str] = []
                for sd in range(coarse_seeds):
                    model_name = f"hpo-{layout}-{key}-seed{sd}"
                    res = train_approx_agent(
                        layout_name=layout,
                        ghost_agent=ghost_agent,
                        num_ghosts=num_ghosts,
                        episodes=coarse_episodes,
                        agent_args={"epsilon": eps, "alpha": a, "gamma": g, "extractor": "SimpleExtractor", "numTraining": coarse_episodes},
                        seed=sd,
                        timeout=timeout,
                        model_name=model_name,
                    )
                    model_path = res["modelPath"]
                    eval_res = _eval_model(layout, model_path, ghost_agent, num_ghosts, test_episodes, seed=sd, timeout=timeout)
                    seed_avgs.append(eval_res["avgScore"])
                    seed_paths.append(model_path)
                    coarse_results.setdefault(key, {"cfg": asdict(cfg), "seeds": []})
                    coarse_results[key]["seeds"].append({
                        "seed": sd,
                        "modelPath": model_path,
                        "eval": eval_res,
                    })
                mean_avg = sum(seed_avgs) / max(1, len(seed_avgs))
                coarse_results[key]["meanAvgScore"] = mean_avg
                print(f"[HPO] Coarse cfg={key} meanAvg={mean_avg:.2f}")
                sys.stdout.flush()

    # Choose best coarse config
    best_key = max(coarse_results.keys(), key=lambda k: coarse_results[k]["meanAvgScore"]) if coarse_results else None
    if best_key is None:
        raise RuntimeError("No coarse results obtained")
    best_cfg_dict = coarse_results[best_key]["cfg"]
    print(f"[HPO] Best coarse cfg={best_key} meanAvg={coarse_results[best_key]['meanAvgScore']:.2f}")
    sys.stdout.flush()

    # Final training on best config with more episodes and seeds
    final_cfg = HPOConfig(epsilon=best_cfg_dict["epsilon"], alpha=best_cfg_dict["alpha"], gamma=best_cfg_dict["gamma"], episodes=final_episodes)
    final_key = _cfg_key(final_cfg)
    final_results: Dict[str, Any] = {"cfg": asdict(final_cfg), "seeds": []}

    top_seed_avg = -1e9
    top_model_path = None

    for sd in range(final_seeds):
        model_name = f"best-{layout}-{final_key}-seed{sd}"
        res = train_approx_agent(
            layout_name=layout,
            ghost_agent=ghost_agent,
            num_ghosts=num_ghosts,
            episodes=final_episodes,
            agent_args={"epsilon": final_cfg.epsilon, "alpha": final_cfg.alpha, "gamma": final_cfg.gamma, "extractor": "SimpleExtractor", "numTraining": final_episodes},
            seed=sd,
            timeout=timeout,
            model_name=model_name,
        )
        model_path = res["modelPath"]
        eval_res = _eval_model(layout, model_path, ghost_agent, num_ghosts, final_test_episodes, seed=sd, timeout=timeout)
        final_results["seeds"].append({"seed": sd, "modelPath": model_path, "eval": eval_res})
        if eval_res["avgScore"] > top_seed_avg:
            top_seed_avg = eval_res["avgScore"]
            top_model_path = model_path
        print(f"[HPO] Final cfg seed={sd} avg={eval_res['avgScore']:.2f}")
        sys.stdout.flush()

    # Promote the best seed model to a standard alias for the layout
    best_alias = os.path.join(models_dir(), f"best-{layout}.json")
    if top_model_path and os.path.exists(top_model_path):
        try:
            # Copy contents
            with open(top_model_path, 'r') as src, open(best_alias, 'w') as dst:
                dst.write(src.read())
        except Exception:
            pass

    result = {
        "layout": layout,
        "ghostAgent": ghost_agent,
        "numGhosts": num_ghosts,
        "coarse": coarse_results,
        "bestCoarseKey": best_key,
        "final": final_results,
        "bestModelPath": best_alias if os.path.exists(best_alias) else top_model_path,
    }

    out_path = os.path.join(HERE, f"hpo_results_{layout}.json")
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"[HPO] Complete. Results: {out_path}. Best model: {result['bestModelPath']}")
    return result


def main():
    layout = os.environ.get("HPO_LAYOUT", "originalClassic")
    ghost_agent = os.environ.get("HPO_GHOST_AGENT", "DirectionalGhost")
    num_ghosts = int(os.environ.get("HPO_NUM_GHOSTS", "4"))

    coarse_episodes = int(os.environ.get("HPO_COARSE_EPISODES", "6000"))
    coarse_seeds = int(os.environ.get("HPO_COARSE_SEEDS", "3"))
    test_episodes = int(os.environ.get("HPO_TEST_EPISODES", "200"))

    final_episodes = int(os.environ.get("HPO_FINAL_EPISODES", "12000"))
    final_seeds = int(os.environ.get("HPO_FINAL_SEEDS", "5"))
    final_test_episodes = int(os.environ.get("HPO_FINAL_TEST_EPISODES", "150"))

    timeout = int(os.environ.get("HPO_TIMEOUT", "100"))

    t0 = time.time()
    res = hpo_search(
        layout=layout,
        ghost_agent=ghost_agent,
        num_ghosts=num_ghosts,
        coarse_episodes=coarse_episodes,
        coarse_seeds=coarse_seeds,
        test_episodes=test_episodes,
        final_episodes=final_episodes,
        final_seeds=final_seeds,
        final_test_episodes=final_test_episodes,
        timeout=timeout,
    )
    print(f"[HPO] Took {time.time()-t0:.1f}s")


if __name__ == '__main__':
    main()
