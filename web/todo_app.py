import streamlit as st
import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "todo_data.json")

def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Todo 앱", page_icon="🗒️")
st.title("간단한 Todo 앱")

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

with st.form("add_task"):
    new_task = st.text_input("새 할 일")
    add = st.form_submit_button("추가")
    if add and new_task.strip():
        st.session_state.tasks.append({"text": new_task.strip(), "done": False})
        save_tasks(st.session_state.tasks)
        st.experimental_rerun()

st.write("### 할 일 목록")
if not st.session_state.tasks:
    st.info("할 일이 없습니다. 새 할 일을 추가하세요.")

for idx, task in enumerate(list(st.session_state.tasks)):
    cols = st.columns([0.85, 0.15])
    checked = cols[0].checkbox(task.get("text", ""), value=task.get("done", False), key=f"chk_{idx}")
    if checked != task.get("done", False):
        st.session_state.tasks[idx]["done"] = checked
        save_tasks(st.session_state.tasks)
    if cols[1].button("삭제", key=f"del_{idx}"):
        st.session_state.tasks.pop(idx)
        save_tasks(st.session_state.tasks)
        st.experimental_rerun()

if st.button("완료된 항목 모두 제거"):
    st.session_state.tasks = [t for t in st.session_state.tasks if not t.get("done", False)]
    save_tasks(st.session_state.tasks)
    st.experimental_rerun()
