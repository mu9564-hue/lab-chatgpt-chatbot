from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os

load_dotenv()

PERSONAS = {
    "친절한 도우미": "당신은 친절한 AI 어시스턴트입니다. 모르면 '확인 필요'라고만 답하세요.",
    "엄격한 사서": "당신은 매우 격식 있는 사서입니다. 짧고 단정하게 답합니다.",
    "친근한 친구": "당신은 친근한 동네 친구입니다. 반말로 편하게 답합니다.",
}

MODEL = os.getenv("MODEL", "gpt-4o-mini")

st.set_page_config(page_title="Streamlit Chat App", page_icon="💬")
st.title("Streamlit Chat App 💬")

with st.sidebar:
    persona = st.selectbox("페르소나", list(PERSONAS.keys()))
    temperature = st.slider("temperature", 0.0, 1.0, 0.3, 0.1)
    if st.button("대화 초기화"):
        st.session_state.clear()
        st.experimental_rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.chat_message("assistant").write("안녕하세요! 무엇이든 물어보세요 😊")

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

llm = ChatOpenAI(model=MODEL, temperature=temperature)

user_input = st.chat_input("메시지")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    msgs = [SystemMessage(content=PERSONAS[persona])]
    for m in st.session_state.messages:
        cls = HumanMessage if m["role"] == "user" else AIMessage
        msgs.append(cls(content=m["content"]))

    with st.chat_message("assistant"):
        try:
            def gen():
                for chunk in llm.stream(msgs):
                    yield chunk.content or ""
            answer = st.write_stream(gen())
        except Exception:
            answer = "죄송합니다. 일시적인 오류가 발생했어요. 잠시 후 다시 시도해 주세요."
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
