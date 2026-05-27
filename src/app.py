from flask import Flask, render_template, jsonify, request
import os
import json
import time
import random

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# 設定 JSON 數據持久化路徑
TODO_FILE = os.path.join(os.path.dirname(__file__), 'todos.json')

def load_todos():
    """
    從 todos.json 載入任務資料。
    如果檔案不存在或損毀，則初始化預設範例任務。
    """
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return get_default_todos()
    else:
        # 檔案不存在，寫入預設任務並回傳
        defaults = get_default_todos()
        save_todos(defaults)
        return defaults

def get_default_todos():
    """
    產生專案初次載入的範例數據
    """
    return [
        {
            'id': 'sample-1',
            'title': '理解並建立 Flask 後端專案結構',
            'category': 'Docs',
            'completed': False
        },
        {
            'id': 'sample-2',
            'title': '將前端與 Flask API 進行 Fetch 整合',
            'category': 'Feature',
            'completed': True
        },
        {
            'id': 'sample-3',
            'title': '編寫 pytest 後端單元測試用例',
            'category': 'General',
            'completed': False
        },
        {
            'id': 'sample-4',
            'title': '成功將 Flask 應用部署於 Port 19191',
            'category': 'Feature',
            'completed': False
        }
    ]

def save_todos(todos):
    """
    將任務列表序列化存入 todos.json
    """
    try:
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving file: {e}")

# ==========================================
# 路由定義 (Routes)
# ==========================================

@app.route('/')
def index():
    """
    首頁路由 - 渲染開發者儀表板模板
    """
    return render_template('index.html')

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """
    API 路由 - 獲取所有任務
    """
    return jsonify(load_todos())

@app.route('/api/todos', methods=['POST'])
def add_todo():
    """
    API 路由 - 新增一個任務
    """
    data = request.json
    if not data or 'title' not in data or not data['title'].strip():
        return jsonify({'error': '任務標題不能為空'}), 400
    
    todos = load_todos()
    new_todo = {
        'id': str(int(time.time() * 1000)) + str(random.randint(10, 99)),
        'title': data['title'].strip(),
        'category': data.get('category', 'General').strip(),
        'completed': False
    }
    todos.append(new_todo)
    save_todos(todos)
    return jsonify(new_todo), 201

@app.route('/api/todos/<todo_id>', methods=['PUT'])
def toggle_todo(todo_id):
    """
    API 路由 - 切換特定任務的完成狀態
    """
    todos = load_todos()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = not todo['completed']
            save_todos(todos)
            return jsonify(todo)
    return jsonify({'error': '找不到該任務'}), 404

@app.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """
    API 路由 - 刪除特定任務
    """
    todos = load_todos()
    initial_len = len(todos)
    todos = [t for t in todos if t['id'] != todo_id]
    if len(todos) < initial_len:
        save_todos(todos)
        return jsonify({'success': True})
    return jsonify({'error': '找不到該任務'}), 404

@app.route('/api/todos/clear_completed', methods=['POST'])
def clear_completed_todos():
    """
    API 路由 - 清除所有已完成的任務
    """
    todos = load_todos()
    todos = [t for t in todos if not t['completed']]
    save_todos(todos)
    return jsonify({'success': True})

# ==========================================
# 啟動設定
# ==========================================
if __name__ == '__main__':
    # 預設部署在 19191 Port，支援區域網路其他裝置存取
    app.run(host='0.0.0.0', port=19191, debug=True)
