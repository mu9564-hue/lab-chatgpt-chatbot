from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import os
import json

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), "todo_data.json")

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_next_id(tasks):
    if not tasks:
        return 1
    return max(t.get("id", 0) for t in tasks) + 1

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    if not text:
        abort(400, 'text is required')
    tasks = load_tasks()
    task = {"id": get_next_id(tasks), "text": text, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def api_update_task(task_id):
    data = request.get_json() or {}
    tasks = load_tasks()
    for t in tasks:
        if t.get('id') == task_id:
            if 'text' in data:
                t['text'] = data.get('text', t['text'])
            if 'done' in data:
                t['done'] = bool(data.get('done'))
            save_tasks(tasks)
            return jsonify(t)
    abort(404)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    tasks = load_tasks()
    new = [t for t in tasks if t.get('id') != task_id]
    if len(new) == len(tasks):
        abort(404)
    save_tasks(new)
    return '', 204

@app.route('/api/clear_completed', methods=['POST'])
def api_clear_completed():
    tasks = load_tasks()
    tasks = [t for t in tasks if not t.get('done', False)]
    save_tasks(tasks)
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
