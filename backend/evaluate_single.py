#!/usr/bin/env python3
"""
evaluate_single.py

Evaluate a trained SaveLoadApproximateQAgent deterministically (epsilon=0, alpha=0)
over a number of episodes (default: 200) and write evaluation statistics to JSON.

Inputs:
- Model path inferred by layout/ghost/episodes naming, or provided via --model

Outputs:
- Evaluation log: backend/outcomes/eval/{layout}-{ghost}-{episodes}ep.eval_{eval_episodes}.json

Example:
  python backend/evaluate_single.py --layout originalClassic --ghost DirectionalGhost \
    --episodes 4000 --eval-episodes 200
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as stats
import sys
from typing import Any, Dict, List

# Paths
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# External Pacman repo
PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")
if PACMAN_REPO not in sys.path:
    sys.path.insert(0, PACMAN_REPO)

# Pacman imports
import layout as layout_module  # type: ignore
from pacman import ClassicGameRules  # type: ignore
import textDisplay  # type: ignore
from ghostAgents import RandomGhost, DirectionalGhost  # type: ignore

# Local imports
from custom_agents import SaveLoadApproximateQAgent
from training import models_dir as backend_models_dir


def _lookup_ghost(name: str):
    if name == "DirectionalGhost":
        return DirectionalGhost
    if name == "RandomGhost":
        return RandomGhost
    return RandomGhost


def _resolve_layout(layout_name: str):
    layout_path = os.path.join(PACMAN_REPO, 'layouts', f'{layout_name}.lay')
    lay = layout_module.tryToLoad(layout_path)
    if lay is None:
        lay = layout_module.getLayout(layout_name)
    if lay is None:
        raise ValueError(f"Layout not found: {layout_name}")
    return lay


def evaluate(layout: str, ghost: str, episodes: int, eval_episodes: int, num_ghosts: int, timeout: int, gamma: float, extractor: str, model_path: str | None) -> Dict[str, Any]:
    lay = _resolve_layout(layout)
    GhostCls = _lookup_ghost(ghost)

    rules = ClassicGameRules(timeout)
    display = textDisplay.NullGraphics()

    if not model_path:
        model_path = os.path.join(backend_models_dir(), f"approx-{layout}-{ghost}-{episodes}ep.json")

    scores: List[float] = []
    wins = 0
    losses = 0

    for _ in range(eval_episodes):
        pacman = SaveLoadApproximateQAgent(loadPath=model_path, extractor=extractor, epsilon=0.0, alpha=0.0, gamma=gamma)
        ghosts = [GhostCls(i + 1) for i in range(num_ghosts)]
        game = rules.newGame(lay, pacman, ghosts, display, quiet=True, catchExceptions=False)
        for agent in game.agents:
            if hasattr(agent, 'registerInitialState'):
                agent.registerInitialState(game.state.deepCopy())
        game.run()
        s = float(game.state.getScore())
        scores.append(s)
        if game.state.isWin():
            wins += 1
        elif game.state.isLose():
            losses += 1

    mean = stats.fmean(scores) if scores else 0.0
    std = stats.pstdev(scores) if len(scores) > 1 else 0.0

    payload = {
        "layout": layout,
        "ghost": ghost,
        "episodes": episodes,
        "eval_episodes": eval_episodes,
        "numGhosts": num_ghosts,
        "timeout": timeout,
        "gamma": gamma,
        "extractor": extractor,
        "modelPath": model_path,
        "scores": scores,
        "wins": wins,
        "losses": losses,
        "metrics": {
            "mean_score": mean,
            "std_score": std,
            "win_rate": wins / max(1, len(scores)),
            "loss_rate": losses / max(1, len(scores)),
            "policy_stability": std,
        },
    }

    eval_out_dir = os.path.join(HERE, "outcomes", "eval")
    os.makedirs(eval_out_dir, exist_ok=True)
    out_json = os.path.join(eval_out_dir, f"{layout}-{ghost}-{episodes}ep.eval_{eval_episodes}.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[EVAL DONE] layout={layout} ghost={ghost} eval_episodes={eval_episodes}")
    print(f"[EVAL JSON] {out_json}")
    return payload


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate a trained Pacman model and save evaluation metrics JSON.")
    p.add_argument("--layout", required=True)
    p.add_argument("--ghost", required=True, choices=["DirectionalGhost", "RandomGhost"])
    p.add_argument("--episodes", type=int, default=4000, help="Training episodes used for the model name (default 4000)")
    p.add_argument("--eval-episodes", type=int, default=200, help="Evaluation episodes (default 200)")
    p.add_argument("--num-ghosts", type=int, default=4)
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--gamma", type=float, default=0.8)
    p.add_argument("--extractor", type=str, default="SimpleExtractor")
    p.add_argument("--model", type=str, default=None, help="Explicit model path (optional)")
    return p.parse_args(argv)


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    evaluate(
        layout=args.layout,
        ghost=args.ghost,
        episodes=args.episodes,
        eval_episodes=args.eval_episodes,
        num_ghosts=args.num_ghosts,
        timeout=args.timeout,
        gamma=args.gamma,
        extractor=args.extractor,
        model_path=args.model,
    )


if __name__ == "__main__":
    from typing import List
    main(sys.argv[1:])

