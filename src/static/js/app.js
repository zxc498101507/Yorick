// 快取 DOM 元素
const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoCategory = document.getElementById('todo-category');
const todoList = document.getElementById('todo-list');
const emptyState = document.getElementById('empty-state');
const todoCountEl = document.getElementById('todo-count');
const completedCountEl = document.getElementById('completed-count');
const clearCompletedBtn = document.getElementById('clear-completed-btn');
const filterTabs = document.querySelectorAll('.filter-tab');
const currentTimeEl = document.getElementById('current-time');

// 目前的篩選狀態 ('all', 'active', 'completed')
let currentFilter = 'all';
// 全域任務資料快取
let todos = [];

/**
 * 更新頂部導覽列的時間顯示
 */
function updateClock() {
  const now = new Date();
  const options = { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit', 
    hour12: false 
  };
  currentTimeEl.textContent = now.toLocaleString('zh-Hant', options);
}

/**
 * 從 Flask 後端 API 獲取所有任務資料
 */
async function fetchTodos() {
  try {
    const response = await fetch('/api/todos');
    if (!response.ok) {
      throw new Error('無法取得任務資料');
    }
    todos = await response.json();
    render();
  } catch (error) {
    console.error('API Error:', error);
  }
}

/**
 * 發送 POST 請求向後端新增一個任務
 */
async function addTodo(title, category) {
  try {
    const response = await fetch('/api/todos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, category }),
    });
    
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.error || '新增任務失敗');
    }
    
    // 重新載入數據並繪製
    await fetchTodos();
  } catch (error) {
    alert(error.message);
  }
}

/**
 * 發送 PUT 請求切換任務的狀態
 */
async function toggleTodo(id) {
  try {
    const response = await fetch(`/api/todos/${id}`, {
      method: 'PUT',
    });
    if (!response.ok) {
      throw new Error('更新任務狀態失敗');
    }
    await fetchTodos();
  } catch (error) {
    console.error('API Error:', error);
  }
}

/**
 * 發送 DELETE 請求刪除特定任務
 */
async function deleteTodo(id) {
  try {
    const response = await fetch(`/api/todos/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('刪除任務失敗');
    }
    await fetchTodos();
  } catch (error) {
    console.error('API Error:', error);
  }
}

/**
 * 發送 POST 請求清除所有已完成的任務
 */
async function clearCompleted() {
  try {
    const response = await fetch('/api/todos/clear_completed', {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('清除已完成任務失敗');
    }
    await fetchTodos();
  } catch (error) {
    console.error('API Error:', error);
  }
}

/**
 * 核心渲染函式 - 依據狀態重新繪製 UI
 */
function render() {
  // 1. 計算並更新側邊欄統計數值
  const activeCount = todos.filter(t => !t.completed).length;
  const completedCount = todos.filter(t => t.completed).length;
  
  todoCountEl.textContent = activeCount;
  completedCountEl.textContent = completedCount;

  // 2. 依據篩選條件過濾任務
  let filteredTodos = todos;
  if (currentFilter === 'active') {
    filteredTodos = todos.filter(t => !t.completed);
  } else if (currentFilter === 'completed') {
    filteredTodos = todos.filter(t => t.completed);
  }

  // 3. 處理空狀態 UI 顯示
  if (filteredTodos.length === 0) {
    todoList.classList.add('hidden');
    emptyState.classList.remove('hidden');
  } else {
    todoList.classList.remove('hidden');
    emptyState.classList.add('hidden');
  }

  // 4. 清除現有清單並重新渲染
  todoList.innerHTML = '';
  
  filteredTodos.forEach(todo => {
    const li = document.createElement('li');
    li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
    li.dataset.id = todo.id;

    const catClass = todo.category.toLowerCase();

    li.innerHTML = `
      <div class="todo-left">
        <label class="checkbox-container">
          <input type="checkbox" class="todo-toggle" ${todo.completed ? 'checked' : ''}>
          <span class="checkmark"></span>
        </label>
        <div class="todo-details">
          <span class="todo-title">${escapeHTML(todo.title)}</span>
          <span class="cat-badge category-${catClass}">${todo.category}</span>
        </div>
      </div>
      <button class="btn-delete" title="刪除任務">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
      </button>
    `;
    
    todoList.appendChild(li);
  });
}

/**
 * 防止 XSS 攻擊的 HTML 跳脫函式
 */
function escapeHTML(str) {
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}

// ==========================================
// 事件監聽與處理
// ==========================================

// 表單提交：新增任務
todoForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = todoInput.value.trim();
  const category = todoCategory.value;

  if (title) {
    await addTodo(title, category);
    todoInput.value = '';
  }
});

// 清單區區塊：使用事件代理監聽切換與刪除
todoList.addEventListener('click', async (e) => {
  const todoItem = e.target.closest('.todo-item');
  if (!todoItem) return;
  const id = todoItem.dataset.id;

  // 點擊核取方塊切換狀態
  if (e.target.classList.contains('todo-toggle')) {
    await toggleTodo(id);
  }
  
  // 點擊刪除按鈕
  if (e.target.closest('.btn-delete')) {
    await deleteTodo(id);
  }
});

// 篩選頁籤切換
filterTabs.forEach(tab => {
  tab.addEventListener('click', (e) => {
    filterTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentFilter = tab.dataset.filter;
    render();
  });
});

// 清除已完成任務
clearCompletedBtn.addEventListener('click', async () => {
  await clearCompleted();
});

// ==========================================
// 初始化應用程式
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // 從 Flask API 拉取第一手任務數據
  fetchTodos();
  
  // 啟動實時時鐘
  updateClock();
  setInterval(updateClock, 1000);
});
