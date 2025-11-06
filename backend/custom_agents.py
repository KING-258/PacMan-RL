import os
import sys
import json
from typing import Optional

PACMAN_REPO = os.environ.get("PACMAN_REPO", "/home/king/Pacman-ReinforcementLearning")
if PACMAN_REPO not in sys.path:
    sys.path.insert(0, PACMAN_REPO)
import util  
from qlearningAgents import ApproximateQAgent  


class SaveLoadApproximateQAgent(ApproximateQAgent):
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

        

        if self._loadPath:

            self.load_weights(self._loadPath)


    

    def save_weights(self, path: Optional[str] = None) -> None:

        path = path or self._savePath

        if not path:

            return

        os.makedirs(os.path.dirname(path), exist_ok=True)

        

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

        

        self.weights = util.Counter()

        for k, v in data.items():

            self.weights[k] = float(v)


    

    def final(self, state):  

        

        super().final(state)

        

        if getattr(self, "episodesSoFar", 0) == getattr(self, "numTraining", -1):

            self.save_weights()

