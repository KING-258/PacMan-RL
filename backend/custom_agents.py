import os
import sys
import json
from typing import Optional

# Ensure Pacman repo is on path
PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")
if PACMAN_REPO not in sys.path:
    sys.path.insert(0, PACMAN_REPO)

# Pacman imports
import util  # type: ignore
from qlearningAgents import ApproximateQAgent  # type: ignore


class SaveLoadApproximateQAgent(ApproximateQAgent):
    """
    Approximate Q-learning agent that can save/load weights to/from JSON.

    Notes:
    - Defaults to SimpleExtractor to avoid un-serializable state keys.
    - If loadPath is given and exists, weights are loaded at init.
    - If savePath is provided, weights are saved when training completes
      (episodesSoFar == numTraining) in final().
    """

    def __init__(
        self,
        *,
        savePath: Optional[str] = None,
        loadPath: Optional[str] = None,
        extractor: str = "SimpleExtractor",
        **args,
    ) -> None:
        self._savePath = savePath
        self._loadPath = loadPath
        super().__init__(extractor=extractor, **args)
        # If a load path is provided, hydrate weights
        if self._loadPath:
            self.load_weights(self._loadPath)

    # ----- Persistence helpers -----
    def save_weights(self, path: Optional[str] = None) -> None:
        path = path or self._savePath
        if not path:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # util.Counter behaves like dict
        payload = {str(k): float(v) for k, v in self.weights.items()}
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, path)

    def load_weights(self, path: str) -> None:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # reset weights then load
        self.weights = util.Counter()
        for k, v in data.items():
            self.weights[k] = float(v)

    # ----- Lifecycle overrides -----
    def final(self, state):  # type: ignore[override]
        # Call parent's final() which handles episode tracking
        super().final(state)
        # If we just completed training, persist weights
        if getattr(self, "episodesSoFar", 0) == getattr(self, "numTraining", -1):
            self.save_weights()
