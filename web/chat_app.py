from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os

load_dotenv()

app = Flask(__name__, template_folder="templates")
CORS(app)

PERSONAS = {
    "친절한 도우미": "당신은 친절한 AI 어시스턴트입니다. 모르면 '확인 필요'라고만 답하세요.",
    "엄격한 사서": "당신은 매우 격식 있는 사서입니다. 짧고 단정하게 답합니다.",
    "친근한 친구": "당신은 친근한 동네 친구입니다. 반말로 편하게 답합니다.",
}

MODEL = os.getenv("MODEL", "gpt-4o-mini")


def build_msgs(system_text, history):
    msgs = [SystemMessage(content=system_text)]
    for m in history:
        cls = HumanMessage if m.get("role") == "user" else AIMessage
        msgs.append(cls(content=m.get("content", "")))
    return msgs


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat_api():
    payload = request.get_json() or {}
    history = payload.get("messages", [])
    persona = payload.get("persona", "친절한 도우미")
    temperature = float(payload.get("temperature", 0.3))

    system_text = PERSONAS.get(persona, PERSONAS["친절한 도우미"])
    llm = ChatOpenAI(model=MODEL, temperature=temperature)

    msgs = build_msgs(system_text, history)
    try:
        resp = llm.invoke(msgs)
        answer = resp.content
    except Exception as e:
        answer = f"Error: {e}"

    return jsonify({"reply": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8502)))
