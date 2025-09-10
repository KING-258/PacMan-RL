# Pacman Web

This project wraps your existing Berkeley Pacman RL code with a Flask REST API and a React (Vite) frontend.

- Backend: `/home/king/Projects/pacman-web/backend`
- Frontend: `/home/king/Projects/pacman-web/frontend`
- Uses the repo at `/home/king/Pacman-ReinforcementLearning` directly (not modified).

## Backend (Flask)

1) Create a virtualenv and install deps:

python3 -m venv /home/king/Projects/pacman-web/backend/venv
source /home/king/Projects/pacman-web/backend/venv/bin/activate
pip install -r /home/king/Projects/pacman-web/backend/requirements.txt

2) Run the API (default port 5001):

python /home/king/Projects/pacman-web/backend/app.py
# or
python /home/king/Projects/pacman-web/backend/server.py

3) Endpoints:
- POST http://localhost:5001/api/reset
  Body JSON (optional):
  { "layout": "originalClassic", "pacmanAgent": "GreedyAgent" | "PacmanQAgent" | "ApproximateQAgent" | "SaveLoadApproximateQAgent", "ghostAgent": "DirectionalGhost" | "RandomGhost", "numGhosts": 4, "numTraining": 0, "modelPath": "/abs/path/to/model.json", "agentArgs": {"epsilon": 0.05, "alpha": 0.2, "gamma": 0.8, "extractor": "SimpleExtractor"} }
- POST http://localhost:5001/api/step
  Body JSON: { "steps": 1 }
- GET  http://localhost:5001/api/layouts
- GET  http://localhost:5001/api/models
- GET  http://localhost:5001/api/meta
- GET  http://localhost:5001/api/state
- POST http://localhost:5001/api/train
  Body JSON: { "layout": "originalClassic", "ghostAgent": "DirectionalGhost", "numGhosts": 4, "episodes": 200, "agentArgs": {"epsilon": 0.1, "alpha": 0.2, "gamma": 0.8, "extractor": "SimpleExtractor"}, "modelName": "my-model" }

Notes:
- Training uses an Approximate Q-Agent with SimpleExtractor so weights can be persisted as JSON.
- If `modelPath` is set on reset, the backend automatically uses the persisted agent with epsilon=0 and alpha=0 to run a deterministic policy.

## Frontend (React + Vite)

1) Install deps:

cd /home/king/Projects/pacman-web/frontend
npm install

2) Start dev server:

npm run dev

3) Open the shown localhost URL (default http://localhost:5173).

The frontend assumes the backend on http://localhost:5001 and will:
- Reset to `originalClassic` + DirectionalGhost + GreedyAgent on load
- Render walls, food, capsules, Pacman and ghosts
- Step or auto-run the simulation
- Let you choose a trained model from the server and run with it

If your Pacman repo lives somewhere else, export PACMAN_REPO before starting the backend:

export PACMAN_REPO=/path/to/Pacman-ReinforcementLearning
python /home/king/Projects/pacman-web/backend/app.py

