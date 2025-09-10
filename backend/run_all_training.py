#!/usr/bin/env python3
import os
import sys
import time
from typing import List

# Make sure backend package path is available for relative imports
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# PACMAN_REPO path
PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")
LAYOUTS_DIR = os.path.join(PACMAN_REPO, "layouts")

# Config
EPISODES = int(os.environ.get("TRAIN_EPISODES", "100"))
GHOST_AGENT = os.environ.get("TRAIN_GHOST_AGENT", "DirectionalGhost")
NUM_GHOSTS = int(os.environ.get("TRAIN_NUM_GHOSTS", "4"))
TIMEOUT = int(os.environ.get("TRAIN_TIMEOUT", "30"))

from training import train_approx_agent, models_dir


def list_layouts() -> List[str]:
    names: List[str] = []
    for f in os.listdir(LAYOUTS_DIR):
        if f.endswith('.lay'):
            base = os.path.splitext(f)[0]
            names.append(base)
    names.sort()
    return names


def main():
    os.makedirs(models_dir(), exist_ok=True)
    layouts = list_layouts()
    print(f"Found {len(layouts)} layouts. Starting training...")
    sys.stdout.flush()
    results = []
    for name in layouts:
        print(f"[TRAIN] layout={name} episodes={EPISODES} ghost={GHOST_AGENT} numGhosts={NUM_GHOSTS}")
        sys.stdout.flush()
        try:
            res = train_approx_agent(
                layout_name=name,
                ghost_agent=GHOST_AGENT,
                num_ghosts=NUM_GHOSTS,
                episodes=EPISODES,
                timeout=TIMEOUT,
                model_name=f"approx-{name}-{EPISODES}ep",
            )
            print(f"[DONE] layout={name} saved={res.get('modelPath')}")
            results.append(res)
        except Exception as e:
            print(f"[ERROR] layout={name} err={e}")
        sys.stdout.flush()
    # Write a completion flag
    done_path = os.path.join(HERE, 'train_all.done')
    with open(done_path, 'w') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S'))
    print(f"ALL_TRAINING_COMPLETE wrote {done_path}")
    sys.stdout.flush()


if __name__ == '__main__':
    main()
