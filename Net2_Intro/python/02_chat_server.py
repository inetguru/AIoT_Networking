# 실습 2 (서버) : Stateless 서버와 Stateful 서버
#   /stateless : 요청에 "지금까지의 대화 전체"가 들어 있어야 한다. 서버는 아무것도 기억하지 않는다.
#   /stateful  : 서버가 세션별로 대화를 "기억한다". 요청에는 세션 번호와 새 문장만 보낸다.
#   (LLM API 가 대화 이력을 매번 보내야 하는 이유와 같은 구조다)
#   compose.yaml 의 chat 서비스로 자동 실행된다. 포트 9200.
import http.server
import json
import re

PORT = 9200
sessions = {}          # 세션 번호 -> 대화 목록  (Stateful 서버의 "기억")


def bot(messages):
    """아주 단순한 챗봇: '내 이름은 X' 를 기억하고 '내 이름이 뭐야?' 에 답한다."""
    name = None
    for m in messages:
        mo = re.search(r"내 이름은 (\S+)", m)
        if mo:
            name = mo.group(1)
    last = messages[-1]
    if "이름이 뭐" in last:
        return f"{name}님이라고 하셨어요." if name else "아직 이름을 듣지 못했어요."
    if "내 이름은" in last:
        return f"반가워요, {name}님!"
    return "네, 알겠습니다."


class Handler(http.server.BaseHTTPRequestHandler):
    def _reply(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path == "/stateless":
            msgs = data["messages"]
            print(f"[stateless] 받은 문장 {len(msgs)}개 -> 서버에 남기는 것: 없음", flush=True)
            self._reply({"answer": bot(msgs)})
        elif self.path == "/stateful":
            hist = sessions.setdefault(data["session"], [])
            hist.append(data["text"])
            print(f"[stateful] 세션 {data['session']}: 서버가 기억 중인 문장 {len(hist)}개", flush=True)
            self._reply({"answer": bot(hist)})
        elif self.path == "/restart":
            sessions.clear()
            print("[restart] 서버가 재시작된 것처럼 모든 세션을 잊었다", flush=True)
            self._reply({"ok": True})
        else:
            self._reply({"error": "not found"}, 404)

    def do_GET(self):
        if self.path == "/stats":
            self._reply({"sessions": len(sessions), "stored_messages": sum(len(v) for v in sessions.values())})
        else:
            self._reply({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        pass


print(f"챗봇 서버 시작: 포트 {PORT}  (/stateless, /stateful, /restart, /stats)", flush=True)
http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
