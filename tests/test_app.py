import os
import json
import pytest
from src.app import app, TODO_FILE, save_todos

@pytest.fixture
def client():
    """
    設定 Flask 測試客戶端，並在測試期間隔離與備份真實數據檔案 todos.json。
    """
    app.config['TESTING'] = True
    
    # 備份原有的 todos.json 資料以避免測試污染真實數據
    backup_todos = None
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, 'r', encoding='utf-8') as f:
                backup_todos = json.load(f)
        except Exception:
            pass

    # 初始化測試用空任務清單
    save_todos([])

    # 建立 Flask 測試客戶端
    with app.test_client() as client:
        yield client

    # 測試完畢後還原備份的數據
    if backup_todos is not None:
        save_todos(backup_todos)
    elif os.path.exists(TODO_FILE):
        os.remove(TODO_FILE)

def test_index_route(client):
    """
    驗證首頁路由 (/) 是否能正常渲染
    """
    response = client.get('/')
    assert response.status_code == 200
    # 檢查頁面是否包含精美儀表板的關鍵字標記
    assert b'ANTIGRAVITY' in response.data
    assert b'Developer Task Board' in response.data

def test_get_todos_empty(client):
    """
    驗證初始化狀態下，GET /api/todos 是否回傳空的任務清單 []
    """
    response = client.get('/api/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 0

def test_add_todo_success(client):
    """
    驗證 POST /api/todos 新增任務的功能
    """
    response = client.post('/api/todos', json={
        'title': '編寫 Flask 單元測試',
        'category': 'Feature'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == '編寫 Flask 單元測試'
    assert data['category'] == 'Feature'
    assert data['completed'] is False
    assert 'id' in data

def test_add_todo_invalid_title(client):
    """
    驗證新增空標題任務時，應返回 400 錯誤與適當說明
    """
    # 測試空字串
    response = client.post('/api/todos', json={'title': ''})
    assert response.status_code == 400
    assert b'\xe4\xbb\xbb\xe5\x8b\x99\xe6\xa8\x99\xe9\xa1\x8c\xe4\xb8\x8d\xe8\x83\xbd\xe7\xb2\xba\xe7\xa9\xba' in response.data # "任務標題不能為空"

def test_toggle_todo_success(client):
    """
    驗證 PUT /api/todos/<id> 切換任務狀態的功能
    """
    # 先新增一個測試任務
    post_res = client.post('/api/todos', json={'title': '待切換任務'})
    todo = json.loads(post_res.data)
    todo_id = todo['id']

    # 執行第一次切換 (未完成 -> 已完成)
    put_res = client.put(f'/api/todos/{todo_id}')
    assert put_res.status_code == 200
    assert json.loads(put_res.data)['completed'] is True

    # 執行第二次切換 (已完成 -> 未完成)
    put_res2 = client.put(f'/api/todos/{todo_id}')
    assert put_res2.status_code == 200
    assert json.loads(put_res2.data)['completed'] is False

def test_delete_todo_success(client):
    """
    驗證 DELETE /api/todos/<id> 刪除任務的功能
    """
    # 先新增一個測試任務
    post_res = client.post('/api/todos', json={'title': '待刪除任務'})
    todo_id = json.loads(post_res.data)['id']

    # 刪除它
    delete_res = client.delete(f'/api/todos/{todo_id}')
    assert delete_res.status_code == 200
    assert json.loads(delete_res.data)['success'] is True

    # 再次獲取清單以確保已刪除
    get_res = client.get('/api/todos')
    assert len(json.loads(get_res.data)) == 0

def test_clear_completed_success(client):
    """
    驗證 POST /api/todos/clear_completed 清除已完成任務的功能
    """
    # 新增兩個測試任務
    t1 = json.loads(client.post('/api/todos', json={'title': '任務一'}).data)
    t2 = json.loads(client.post('/api/todos', json={'title': '任務二'}).data)

    # 將任務一設為完成
    client.put(f"/api/todos/{t1['id']}")

    # 清除所有已完成任務
    clear_res = client.post('/api/todos/clear_completed')
    assert clear_res.status_code == 200

    # 驗證清單中只剩任務二 (未完成)
    get_res = client.get('/api/todos')
    remaining = json.loads(get_res.data)
    assert len(remaining) == 1
    assert remaining[0]['id'] == t2['id']
