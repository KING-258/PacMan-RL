#!/usr/bin/env python3
"""
compute_metrics_single.py

Compose final metrics for a given layout/ghost pair by reading the training and
evaluation JSONs and writing a consolidated per-pair metrics JSON.

Inputs (inferred by default):
- backend/outcomes/train/{layout}-{ghost}-{episodes}ep.train.json
- backend/outcomes/eval/{layout}-{ghost}-{episodes}ep.eval_{eval_episodes}.json

Output (per pair):
- backend/outcomes/metrics/{layout}-{ghost}-{episodes}ep.metrics.json

Example:
  python backend/compute_metrics_single.py --layout originalClassic --ghost DirectionalGhost \
    --episodes 4000 --eval-episodes 200
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

HERE = os.path.dirname(__file__)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def compute(layout: str, ghost: str, episodes: int, eval_episodes: int) -> Dict[str, Any]:
    train_json = os.path.join(HERE, "outcomes", "train", f"{layout}-{ghost}-{episodes}ep.train.json")
    eval_json = os.path.join(HERE, "outcomes", "eval", f"{layout}-{ghost}-{episodes}ep.eval_{eval_episodes}.json")

    t = load_json(train_json)
    e = load_json(eval_json)

    # Compose final per-pair metrics
    result: Dict[str, Any] = {
        "layout": layout,
        "ghost": ghost,
        "episodes": episodes,
        "eval_episodes": eval_episodes,
        "modelPath": t.get("modelPath") or e.get("modelPath"),
        "training": {
            "wins": t.get("wins"),
            "losses": t.get("losses"),
            "metrics": t.get("metrics"),  # includes alpha_conv, mean/std, win/loss rate over training
        },
        "evaluation": {
            "wins": e.get("wins"),
            "losses": e.get("losses"),
            "metrics": e.get("metrics"),  # includes mean/std (policy_stability), win/loss rate
        },
    }

    out_json = os.path.join(HERE, "outcomes", "metrics", f"{layout}-{ghost}-{episodes}ep.metrics.json")
    write_json(out_json, result)
    print(f"[METRICS DONE] {layout} + {ghost} -> {out_json}")
    return result


def parse_args(argv):
    p = argparse.ArgumentParser(description="Compose per-pair metrics JSON from training and evaluation logs.")
    p.add_argument("--layout", required=True)
    p.add_argument("--ghost", required=True, choices=["DirectionalGhost", "RandomGhost"])
    p.add_argument("--episodes", type=int, default=4000)
    p.add_argument("--eval-episodes", type=int, default=200)
    return p.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    compute(args.layout, args.ghost, args.episodes, args.eval_episodes)


if __name__ == "__main__":
    main(sys.argv[1:])

