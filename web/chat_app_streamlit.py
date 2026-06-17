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
    max_chars = st.number_input("입력 길이 제한", min_value=50, max_value=2000, value=500, step=50)
    if st.button("대화 초기화"):
        st.session_state.clear()
        st.experimental_rerun()

    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
    st.metric("누적 토큰(근사)", int(st.session_state.total_tokens))

if "messages" not in st.session_state:
    st.session_state.messages = []

def render_messages():
    for m in st.session_state.messages:
        role = m.get("role")
        content = m.get("content")
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
        else:
            with st.chat_message("assistant"):
                st.write(content)

if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 무엇이든 물어보세요 😊"})

render_messages()

llm = ChatOpenAI(model=MODEL, temperature=temperature)

input_col, send_col = st.columns([8,1])
with input_col:
    user_input = st.text_area("", placeholder="메시지를 입력하세요 (Shift+Enter 줄바꿈)")
with send_col:
    send = st.button("전송")

if send and user_input:
    if len(user_input) > max_chars:
        st.warning(f"입력은 {max_chars}자 이내로 해주세요.")
    else:
        # 사용자 메시지 추가 및 렌더
        st.session_state.messages.append({"role": "user", "content": user_input})
        render_messages()

        # LangChain 메시지로 변환
        msgs = [SystemMessage(content=PERSONAS[persona])]
        for m in st.session_state.messages:
            cls = HumanMessage if m["role"] == "user" else AIMessage
            msgs.append(cls(content=m["content"]))

        # 스트리밍 응답
        assistant_placeholder = st.empty()
        answer = ""
        try:
            for chunk in llm.stream(msgs):
                text = chunk.content or ""
                answer += text
                with assistant_placeholder.container():
                    st.chat_message("assistant").write(answer)
        except Exception as e:
            answer = "죄송합니다. 일시적인 오류가 발생했어요."
            assistant_placeholder.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        # 근사 토큰 비용(단순 근사)
        st.session_state.total_tokens += len(user_input) + len(answer)
        render_messages()
