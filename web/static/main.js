const apiRoot = '/api/tasks';

async function fetchTasks() {
  const res = await fetch(apiRoot);
  return res.json();
}

function el(tag, cls) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  return e;
}

async function render() {
  const list = document.getElementById('tasks');
  list.innerHTML = '';
  const tasks = await fetchTasks();
  tasks.forEach(t => {
    const li = el('li', 'task');
    const chk = el('input');
    chk.type = 'checkbox';
    chk.checked = t.done;
    chk.addEventListener('change', async () => {
      await fetch(`${apiRoot}/${t.id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({done: chk.checked})
      });
      render();
    });

    const span = el('span');
    span.textContent = t.text;
    if (t.done) span.classList.add('done');

    const del = el('button', 'delete');
    del.textContent = '삭제';
    del.addEventListener('click', async () => {
      await fetch(`${apiRoot}/${t.id}`, {method: 'DELETE'});
      render();
    });

    li.appendChild(chk);
    li.appendChild(span);
    li.appendChild(del);
    list.appendChild(li);
  });
}

document.getElementById('addForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = document.getElementById('newTask');
  const text = input.value.trim();
  if (!text) return;
  await fetch(apiRoot, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text})});
  input.value = '';
  render();
});

document.getElementById('clearCompleted').addEventListener('click', async () => {
  await fetch('/api/clear_completed', {method: 'POST'});
  render();
});

render();
