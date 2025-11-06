# Pacman Web

- Backend: `PacMan-RL/backend`
- Frontend: `PacMan-RL/frontend`
- Uses the repo [PacmanRL](https://github.com/KING-258/PacMan-RL)

## Backend (Flask)

1) Create a virtualenv and install deps:

python3 -m venv /home/king/Projects/pacman-web/backend/venv
source /home/king/Projects/pacman-web/backend/venv/bin/activate
pip install -r /home/king/Projects/pacman-web/backend/requirements.txt

2) Run the API (default port 5000):

cd backend
python app.py

3) Endpoints:
- POST http://localhost:5000/api/reset
  Body JSON (optional):
  { "layout": "originalClassic", "pacmanAgent": "GreedyAgent" | "PacmanQAgent" | "ApproximateQAgent" | "SaveLoadApproximateQAgent", "ghostAgent": "DirectionalGhost" | "RandomGhost", "numGhosts": 4, "numTraining": 0, "modelPath": "/abs/path/to/model.json", "agentArgs": {"epsilon": 0.05, "alpha": 0.2, "gamma": 0.8, "extractor": "SimpleExtractor"} }
- POST http://localhost:5000/api/step
  Body JSON: { "steps": 1 }
- GET  http://localhost:5000/api/layouts
- GET  http://localhost:5000/api/models
- GET  http://localhost:5000/api/meta
- GET  http://localhost:5000/api/state
- POST http://localhost:5000/api/train
  Body JSON: { "layout": "originalClassic", "ghostAgent": "DirectionalGhost", "numGhosts": 4, "episodes": 200, "agentArgs": {"epsilon": 0.1, "alpha": 0.2, "gamma": 0.8, "extractor": "SimpleExtractor"}, "modelName": "my-model" }

Notes:
- Training uses an Approxima## Maps (Layouts)

Layouts are loaded from your Pacman repository's `layouts/` folder (PACMAN_REPO). You can list the available layouts via the API:

- GET /api/layouts

Common layouts used and tested here:
- originalClassic — Baseline, balanced maze suitable for initial training and demos
- minimaxClassic — Longer corridors and junctions that amplify adversarial pressure
- trickyClassic — Deceptive turns and chokepoints; higher difficulty under exploration
- capsuleClassic — Emphasizes power-capsule timing and ghost scare windows
- contestClassic — Contest-style challenge map
- mediumClassic — Medium-sized classic variant
- mediumGrid — Medium grid-like layout with regular structure
- openClassic — More open corridors with fewer tight traps
- powerClassic — More power pellets; tests offensive timing
- smallClassic — Compact classic layout for quick iterations
- smallGrid — Small grid variant for fast tests
- testClassic — Minimal test map for sanity checks
- trappedClassic — Traps and dead-ends that punish greedy routes

Notes:
- The exact set depends on the contents of PACMAN_REPO/layouts. Adding a `.lay` file there makes it available automatically.
- Layout names are case-sensitive and referenced without the `.lay` extension.

## Training and Models (Quick Reference)

- Algorithms: Q-Learning (off-policy) and SARSA (on-policy), both in JSON Approx and Torch Approx variants
- Defaults (scripts): episodes=4000, timeout=30, numGhosts=4 (unless overridden)
- Torch Approx: `--device cpu|cuda` (auto-select if omitted), `--hash-dim 4096` by default, `--algo qlearning|sarsa`
- Models directory: `backend/models/` (JSON for Approx; `.pt` for Torch; DQN ghost under subfolder)
- Metrics: Per-episode scores plus summary (mean_score, std_score, win_rate, loss_rate, simple convergence heuristic)

Example Torch SARSA command:

```
python3 backend/train_single_torch.py \
  --layout originalClassic --ghost DirectionalGhost \
  --episodes 4000 --timeout 30 --device cuda --algo sarsa
```

## Public Archive Notes

- Attribution: This project integrates the UC Berkeley AI Pac-Man Projects environment. Layouts and core engine remain their work; this repository adds a REST API, a web UI, and training utilities.
- Reproducibility: Models and logs are stored locally. Use fixed seeds and consistent episodes for fair comparisons.
- Extensibility: Add new layouts to PACMAN_REPO/layouts; add new agents by extending the backend agents and wiring them in `/api/meta`, `/api/reset`, and training utilities.te Q-Agent with SimpleExtractor so weights can be persisted as JSON.
- If `modelPath` is set on reset, the backend automatically uses the persisted agent with epsilon=0 and alpha=0 to run a deterministic policy.

## Frontend (React + Vite)

1) Install deps:

cd frontend
npm install

2) Start dev server:

npm run dev

3) Open the shown localhost URL (default http://localhost:5173).

The frontend assumes the backend on http://localhost:5000 and will:
- Reset to `originalClassic` + DirectionalGhost + GreedyAgent on load
- Render walls, food, capsules, Pacman and ghosts
- Step or auto-run the simulation
- Let you choose a trained model from the server and run with it

## Maps (Layouts)

Layouts are loaded from your Pacman repository's `layouts/` folder (PACMAN_REPO). You can list the available layouts via the API:

- GET /api/layouts

Common layouts used and tested here:
- originalClassic — Baseline, balanced maze suitable for initial training and demos
- minimaxClassic — Longer corridors and junctions that amplify adversarial pressure
- trickyClassic — Deceptive turns and chokepoints; higher difficulty under exploration
- capsuleClassic — Emphasizes power-capsule timing and ghost scare windows
- contestClassic — Contest-style challenge map
- mediumClassic — Medium-sized classic variant
- mediumGrid — Medium grid-like layout with regular structure
- openClassic — More open corridors with fewer tight traps
- powerClassic — More power pellets; tests offensive timing
- smallClassic — Compact classic layout for quick iterations
- smallGrid — Small grid variant for fast tests
- testClassic — Minimal test map for sanity checks
- trappedClassic — Traps and dead-ends that punish greedy routes

Notes:
- The exact set depends on the contents of PACMAN_REPO/layouts. Adding a `.lay` file there makes it available automatically.
- Layout names are case-sensitive and referenced without the `.lay` extension.

## Training and Models (Quick Reference)

- Algorithms: Q-Learning (off-policy) and SARSA (on-policy), both in JSON Approx and Torch Approx variants
- Defaults (scripts): episodes=4000, timeout=30, numGhosts=4 (unless overridden)
- Torch Approx: `--device cpu|cuda` (auto-select if omitted), `--hash-dim 4096` by default, `--algo qlearning|sarsa`
- Models directory: `backend/models/` (JSON for Approx; `.pt` for Torch; DQN ghost under subfolder)
- Metrics: Per-episode scores plus summary (mean_score, std_score, win_rate, loss_rate, simple convergence heuristic)

Example Torch SARSA command:

```
python3 backend/train_single_torch.py \
  --layout originalClassic --ghost DirectionalGhost \
  --episodes 4000 --timeout 30 --device cuda --algo sarsa
```

## Public Archive Notes

- Attribution: This project integrates the UC Berkeley AI Pac-Man Projects environment. Layouts and core engine remain their work; this repository adds a REST API, a web UI, and training utilities.
- Reproducibility: Models and logs are stored locally. Use fixed seeds and consistent episodes for fair comparisons.
- Extensibility: Add new layouts to PACMAN_REPO/layouts; add new agents by extending the backend agents and wiring them in `/api/meta`, `/api/reset`, and training utilities.