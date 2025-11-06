from __future__ import annotations


import argparse

import json

import os

import random

import statistics as stats

import sys

import time

from dataclasses import asdict, dataclass

from typing import Any, Dict, List, Tuple




HERE = os.path.dirname(__file__)

if HERE not in sys.path:

    sys.path.insert(0, HERE)




PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")

if PACMAN_REPO not in sys.path:

    sys.path.insert(0, PACMAN_REPO)




import layout as layout_module  

from pacman import ClassicGameRules  

import textDisplay  

from ghostAgents import RandomGhost, DirectionalGhost  




from custom_agents import SaveLoadApproximateQAgent

from training import models_dir as backend_models_dir



@dataclass

class TrainConfig:

    layout: str

    ghost: str

    episodes: int = 4000

    num_ghosts: int = 4

    timeout: int = 30

    seed: int | None = None

    epsilon: float = 0.1

    alpha: float = 0.2

    gamma: float = 0.8

    extractor: str = "SimpleExtractor"



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



def _compute_alpha_conv(scores: List[float], window: int) -> float | None:

    if len(scores) < 2 * window:

        return None

    last = scores[-window:]

    prev = scores[-2*window:-window]

    return abs(stats.fmean(last) - stats.fmean(prev)) / float(window)



def train(cfg: TrainConfig) -> Dict[str, Any]:

    if cfg.seed is not None:

        random.seed(cfg.seed)


    lay = _resolve_layout(cfg.layout)

    GhostCls = _lookup_ghost(cfg.ghost)


    rules = ClassicGameRules(cfg.timeout)

    display = textDisplay.NullGraphics()


    models_path = backend_models_dir()

    model_name = f"approx-{cfg.layout}-{cfg.ghost}-{cfg.episodes}ep"

    model_path = os.path.join(models_path, f"{model_name}.json")


    

    train_out_dir = os.path.join(HERE, "outcomes", "train")

    os.makedirs(train_out_dir, exist_ok=True)

    train_json = os.path.join(train_out_dir, f"{cfg.layout}-{cfg.ghost}-{cfg.episodes}ep.train.json")


    

    pacman = SaveLoadApproximateQAgent(

        savePath=model_path,

        extractor=cfg.extractor,

        epsilon=cfg.epsilon,

        alpha=cfg.alpha,

        gamma=cfg.gamma,

        numTraining=cfg.episodes,

    )


    scores: List[float] = []

    wins = 0

    losses = 0


    t0 = time.time()

    for _ in range(cfg.episodes):

        ghosts = [GhostCls(i + 1) for i in range(cfg.num_ghosts)]

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

    t1 = time.time()


    

    pacman.save_weights(model_path)


    

    window = min(100, max(10, cfg.episodes // 40))

    alpha_conv = _compute_alpha_conv(scores, window)

    mean = stats.fmean(scores) if scores else 0.0

    std = stats.pstdev(scores) if len(scores) > 1 else 0.0


    payload = {

        "layout": cfg.layout,

        "ghost": cfg.ghost,

        "episodes": cfg.episodes,

        "numGhosts": cfg.num_ghosts,

        "timeout": cfg.timeout,

        "seed": cfg.seed,

        "epsilon": cfg.epsilon,

        "alpha": cfg.alpha,

        "gamma": cfg.gamma,

        "extractor": cfg.extractor,

        "modelPath": model_path,

        "trainTimeSec": t1 - t0,

        "scores": scores,

        "wins": wins,

        "losses": losses,

        "metrics": {

            "mean_score": mean,

            "std_score": std,

            "win_rate": wins / max(1, len(scores)),

            "loss_rate": losses / max(1, len(scores)),

            "alpha_conv": alpha_conv,

        },

    }


    with open(train_json, "w", encoding="utf-8") as f:

        json.dump(payload, f, indent=2)


    print(f"[TRAIN DONE] layout={cfg.layout} ghost={cfg.ghost} episodes={cfg.episodes} saved={model_path}")

    print(f"[TRAIN JSON] {train_json}")

    return payload



def parse_args(argv: List[str]) -> argparse.Namespace:

    p = argparse.ArgumentParser(description="Train a single Pacman model and save training metrics JSON.")

    p.add_argument("--layout", required=True, help="Layout name, e.g. originalClassic")

    p.add_argument("--ghost", required=True, choices=["DirectionalGhost", "RandomGhost"], help="Ghost agent type")

    p.add_argument("--episodes", type=int, default=4000, help="Training episodes (default 4000)")

    p.add_argument("--num-ghosts", type=int, default=4, help="Number of ghosts (default 4)")

    p.add_argument("--timeout", type=int, default=30, help="Game timeout (default 30)")

    p.add_argument("--seed", type=int, default=None, help="Random seed (optional)")

    p.add_argument("--epsilon", type=float, default=0.1, help="Exploration rate (default 0.1)")

    p.add_argument("--alpha", type=float, default=0.2, help="Learning rate (default 0.2)")

    p.add_argument("--gamma", type=float, default=0.8, help="Discount factor (default 0.8)")

    p.add_argument("--extractor", type=str, default="SimpleExtractor", help="Feature extractor (default SimpleExtractor)")

    return p.parse_args(argv)



def main(argv: List[str]) -> None:

    args = parse_args(argv)

    cfg = TrainConfig(

        layout=args.layout,

        ghost=args.ghost,

        episodes=args.episodes,

        num_ghosts=args.num_ghosts,

        timeout=args.timeout,

        seed=args.seed,

        epsilon=args.epsilon,

        alpha=args.alpha,

        gamma=args.gamma,

        extractor=args.extractor,

    )

    train(cfg)



if __name__ == "__main__":

    from typing import List

    main(sys.argv[1:])


