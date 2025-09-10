import os
import sys
import json
import random
from typing import Any, Dict, List

# Point to your existing Pacman repo (left untouched)
PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")
if PACMAN_REPO not in sys.path:
    sys.path.insert(0, PACMAN_REPO)

# Import Pacman engine pieces
import layout as layout_module
from pacman import ClassicGameRules
import textDisplay
import game as game_mod

# Agents
from pacmanAgents import GreedyAgent
from qlearningAgents import PacmanQAgent, ApproximateQAgent
from ghostAgents import RandomGhost, DirectionalGhost
# Local custom agent
try:
    from custom_agents import SaveLoadApproximateQAgent
except Exception:
    SaveLoadApproximateQAgent = None  # type: ignore


def grid_to_list(grid: game_mod.Grid) -> List[List[bool]]:
    width, height = grid.width, grid.height
    out = [[bool(grid[x][y]) for y in range(height)] for x in range(width)]
    return out


def state_to_json(state: 'game_mod.GameState') -> Dict[str, Any]:  # type: ignore[name-defined]
    food = state.getFood()
    walls = state.getWalls()
    capsules = state.getCapsules()
    pac = state.getPacmanState()
    ghosts = state.getGhostStates()

    return {
        "width": walls.width,
        "height": walls.height,
        "walls": grid_to_list(walls),
        "food": grid_to_list(food),
        "capsules": [[int(x), int(y)] for (x, y) in capsules],
        "pacman": {
            "pos": list(map(float, pac.getPosition())),
            "dir": pac.getDirection(),
        },
        "ghosts": [
            {
                "index": i + 1,
                "pos": list(map(float, g.getPosition())) if g.getPosition() is not None else None,
                "dir": g.getDirection(),
                "scaredTimer": int(g.scaredTimer),
            }
            for i, g in enumerate(ghosts)
        ],
        "score": state.getScore(),
        "isWin": state.isWin(),
        "isLose": state.isLose(),
        "legalPacmanActions": list(state.getLegalPacmanActions()),
        "_agentMoved": getattr(state.data, "_agentMoved", None),
    }


class PacmanService:
    """Wraps the Pacman engine and exposes step-wise control.

    We do not use Game.run(); instead we emulate one agent-time-step per call
    (roughly mirroring game.Game.run's inner loop) so the frontend can drive
    the simulation.
    """

    def __init__(self) -> None:
        self.rules: ClassicGameRules | None = None
        self.game: game_mod.Game | None = None
        self.agentIndex: int = 0
        self.final_called: bool = False

    def _lookup_pacman(self, name: str):
        if name == "GreedyAgent":
            return GreedyAgent
        if name == "PacmanQAgent":
            return PacmanQAgent
        if name == "ApproximateQAgent":
            return ApproximateQAgent
        if name == "SaveLoadApproximateQAgent" and SaveLoadApproximateQAgent is not None:
            return SaveLoadApproximateQAgent
        # default
        return GreedyAgent

    def _lookup_ghost(self, name: str):
        if name == "RandomGhost":
            return RandomGhost
        if name == "DirectionalGhost":
            return DirectionalGhost
        # default
        return RandomGhost

    def new_game(
        self,
        *,
        layout_name: str = "originalClassic",
        pacman_agent: str = "GreedyAgent",
        ghost_agent: str = "DirectionalGhost",
        num_ghosts: int = 4,
        num_training: int = 0,
        agent_args: Dict[str, Any] | None = None,
        seed: int | None = None,
        timeout: int = 30,
        model_path: str | None = None,
    ) -> Dict[str, Any]:
        if seed is not None:
            random.seed(seed)
        # Load layout explicitly from the original repo's layouts dir
        layout_path = os.path.join(PACMAN_REPO, 'layouts', f'{layout_name}.lay')
        layout = layout_module.tryToLoad(layout_path)
        if layout is None:
            # Fallback to the module's search if direct path fails
            layout = layout_module.getLayout(layout_name)
        if layout is None:
            raise ValueError(f"Layout not found: {layout_name}")

        PacClass = self._lookup_pacman(pacman_agent)
        GhostClass = self._lookup_ghost(ghost_agent)

        aargs = dict(agent_args or {})
        if num_training and "numTraining" not in aargs:
            aargs["numTraining"] = num_training

        # If a saved model is provided, force Approx agent with zero exploration/learning
        if model_path and SaveLoadApproximateQAgent is not None:
            PacClass = SaveLoadApproximateQAgent
            aargs.setdefault("epsilon", 0.0)
            aargs.setdefault("alpha", 0.0)
            aargs.setdefault("gamma", 0.8)
            # default to SimpleExtractor for compatibility
            aargs.setdefault("extractor", "SimpleExtractor")
            pacman = PacClass(loadPath=model_path, **aargs)  # type: ignore[call-arg]
        else:
            pacman = PacClass(**aargs)

        ghosts = [GhostClass(i + 1) for i in range(num_ghosts)]

        self.rules = ClassicGameRules(timeout)
        display = textDisplay.NullGraphics()
        game = self.rules.newGame(layout, pacman, ghosts, display, quiet=True, catchExceptions=False)
        self.game = game
        self.agentIndex = 0
        self.final_called = False

        # Call registerInitialState on agents (normally done inside Game.run)
        for i, agent in enumerate(game.agents):
            if hasattr(agent, "registerInitialState"):
                agent.registerInitialState(game.state.deepCopy())

        return state_to_json(self.game.state)

    def _maybe_final(self):
        assert self.game is not None
        if self.game.gameOver and not self.final_called:
            for idx, agent in enumerate(self.game.agents):
                if hasattr(agent, "final"):
                    agent.final(self.game.state)
            self.final_called = True

    def step(self, *, steps: int = 1) -> Dict[str, Any]:
        if self.game is None:
            raise RuntimeError("Game not initialized. Call new_game first.")

        for _ in range(max(1, steps)):
            if self.game.gameOver:
                break

            agent = self.game.agents[self.agentIndex]
            state = self.game.state

            # observation
            if hasattr(agent, "observationFunction"):
                observation = agent.observationFunction(state.deepCopy())
            else:
                observation = state.deepCopy()

            # action
            action = agent.getAction(observation)

            # apply transition
            self.game.state = state.generateSuccessor(self.agentIndex, action)

            # process terminal conditions
            assert self.rules is not None
            # process terminal conditions using the real Game object
            self.rules.process(self.game.state, self.game)

            # next agent
            self.agentIndex = (self.agentIndex + 1) % len(self.game.agents)

        self._maybe_final()
        return state_to_json(self.game.state)

    # these two methods are used by ClassicGameRules.process
    @property
    def state(self):
        assert self.game is not None
        return self.game.state

    @property
    def gameOver(self):
        assert self.game is not None
        return self.game.gameOver

