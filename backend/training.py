import os
import sys
import random
from typing import Any, Dict, Optional

# Ensure Pacman repo is available
PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")
if PACMAN_REPO not in sys.path:
    sys.path.insert(0, PACMAN_REPO)

# Pacman imports
import layout as layout_module  # type: ignore
from pacman import ClassicGameRules  # type: ignore
import textDisplay  # type: ignore
from ghostAgents import RandomGhost, DirectionalGhost  # type: ignore

# Local agent wrapper
from custom_agents import SaveLoadApproximateQAgent


def _lookup_ghost(name: str):
    if name == "DirectionalGhost":
        return DirectionalGhost
    if name == "RandomGhost":
        return RandomGhost
    return RandomGhost


def models_dir() -> str:
    here = os.path.dirname(__file__)
    mdir = os.path.join(here, "models")
    os.makedirs(mdir, exist_ok=True)
    return mdir


def train_approx_agent(
    *,
    layout_name: str = "originalClassic",
    ghost_agent: str = "DirectionalGhost",
    num_ghosts: int = 4,
    episodes: int = 100,
    agent_args: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None,
    timeout: int = 30,
    model_name: Optional[str] = None,
    save_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Train a SaveLoadApproximateQAgent for N episodes and persist weights.

    Returns a summary dict with the saved model path and params used.
    """
    if seed is not None:
        random.seed(seed)

    # Resolve layout
    layout_path = os.path.join(PACMAN_REPO, 'layouts', f'{layout_name}.lay')
    lay = layout_module.tryToLoad(layout_path)
    if lay is None:
        lay = layout_module.getLayout(layout_name)
    if lay is None:
        raise ValueError(f"Layout not found: {layout_name}")

    # Resolve model path
    if not save_path:
        mdir = models_dir()
        fname = (model_name or f"approx-{layout_name}-{episodes}ep").replace("/", "_")
        save_path = os.path.join(mdir, f"{fname}.json")

    # Agent args defaults suitable for Approximate + SimpleExtractor
    aargs: Dict[str, Any] = dict(agent_args or {})
    aargs.setdefault("epsilon", 0.1)
    aargs.setdefault("alpha", 0.2)
    aargs.setdefault("gamma", 0.8)
    aargs.setdefault("numTraining", episodes)

    # Instantiate a single pacman agent reused across episodes
    pacman = SaveLoadApproximateQAgent(savePath=save_path, extractor=aargs.pop("extractor", "SimpleExtractor"), **aargs)

    GhostCls = _lookup_ghost(ghost_agent)

    rules = ClassicGameRules(timeout)
    display = textDisplay.NullGraphics()

    # Run episodes
    for _ in range(episodes):
        ghosts = [GhostCls(i + 1) for i in range(num_ghosts)]
        game = rules.newGame(lay, pacman, ghosts, display, quiet=True, catchExceptions=False)
        # Initialize agents for the new game
        for agent in game.agents:
            if hasattr(agent, "registerInitialState"):
                agent.registerInitialState(game.state.deepCopy())
        # Run to completion
        game.run()

    # Ensure weights are saved (final() already saves at the last episode)
    pacman.save_weights(save_path)

    return {
        "ok": True,
        "modelPath": save_path,
        "episodes": episodes,
        "layout": layout_name,
        "ghostAgent": ghost_agent,
        "numGhosts": num_ghosts,
    }
