from flask import Flask, request, jsonify
from flask_cors import CORS
from pacman_service import PacmanService, PACMAN_REPO, state_to_json
import os
import glob

# training utilities
from training import train_approx_agent

app = Flask(__name__)
CORS(app)

service = PacmanService()

@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.get_json(silent=True) or {}
    layout_name = data.get('layout', 'originalClassic')
    pacman_agent = data.get('pacmanAgent', 'GreedyAgent')
    ghost_agent = data.get('ghostAgent', 'DirectionalGhost')
    num_ghosts = int(data.get('numGhosts', 4))
    num_training = int(data.get('numTraining', 0))
    timeout = int(data.get('timeout', 30))
    seed = data.get('seed', None)
    agent_args = data.get('agentArgs', {})
    model_path = data.get('modelPath')

    state = service.new_game(
        layout_name=layout_name,
        pacman_agent=pacman_agent,
        ghost_agent=ghost_agent,
        num_ghosts=num_ghosts,
        num_training=num_training,
        agent_args=agent_args,
        seed=seed,
        timeout=timeout,
        model_path=model_path,
    )
    return jsonify({"ok": True, "state": state})

@app.route('/api/step', methods=['POST'])
def step():
    data = request.get_json(silent=True) or {}
    steps = int(data.get('steps', 1))
    state = service.step(steps=steps)
    return jsonify({"ok": True, "state": state})

@app.route('/api/state', methods=['GET'])
def get_state():
    if service.game is None:
        return jsonify({"ok": False, "error": "No game initialized"}), 400
    return jsonify({"ok": True, "state": state_to_json(service.game.state)})

# Helper listings for UI
@app.route('/api/layouts', methods=['GET'])
def list_layouts():
    layouts_dir = os.path.join(PACMAN_REPO, 'layouts')
    names = []
    for f in os.listdir(layouts_dir):
        if f.endswith('.lay'):
            names.append(os.path.splitext(f)[0])
    names.sort()
    return jsonify({"ok": True, "layouts": names})

@app.route('/api/models', methods=['GET'])
def list_models():
    mdir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(mdir, exist_ok=True)
    files = sorted([os.path.basename(p) for p in glob.glob(os.path.join(mdir, '*.json'))])
    return jsonify({"ok": True, "models": files, "dir": mdir})

@app.route('/api/train', methods=['POST'])
def train():
    data = request.get_json(silent=True) or {}
    layout_name = data.get('layout', 'originalClassic')
    ghost_agent = data.get('ghostAgent', 'DirectionalGhost')
    num_ghosts = int(data.get('numGhosts', 4))
    episodes = int(data.get('episodes', 100))
    agent_args = data.get('agentArgs', {})
    seed = data.get('seed')
    timeout = int(data.get('timeout', 30))
    model_name = data.get('modelName')
    save_path = data.get('savePath')

    result = train_approx_agent(
        layout_name=layout_name,
        ghost_agent=ghost_agent,
        num_ghosts=num_ghosts,
        episodes=episodes,
        agent_args=agent_args,
        seed=seed,
        timeout=timeout,
        model_name=model_name,
        save_path=save_path,
    )
    return jsonify(result)

@app.route('/api/meta', methods=['GET'])
def meta():
    return jsonify({
        "ok": True,
        "pacmanAgents": ["GreedyAgent", "PacmanQAgent", "ApproximateQAgent", "SaveLoadApproximateQAgent"],
        "ghostAgents": ["DirectionalGhost", "RandomGhost"],
        "extractors": ["SimpleExtractor", "IdentityExtractor"],
        "repoPath": PACMAN_REPO,
    })

if __name__ == '__main__':
    # FLASK_RUN_PORT or default 5001
    port = int(os.environ.get('PORT', os.environ.get('FLASK_RUN_PORT', 5001)))
    app.run(host='0.0.0.0', port=port, debug=False)

