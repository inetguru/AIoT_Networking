# "설비 에이전트" - 다른 에이전트가 말을 걸 수 있는 에이전트 (A2A 의 핵심 아이디어를 단순화한 시연)
#   1) Agent Card : 이 에이전트가 누구이고 무엇을 할 수 있는지 적은 명함 (GET /.well-known/agent-card.json)
#   2) JSON-RPC 2.0 : 작업 요청(method "message/send")을 받아 답한다 (POST /)
#   ※ 실제 A2A 규격(a2a-project)은 이보다 훨씬 많은 기능(Task 상태, 스트리밍, 인증 등)이 있다. 구체적인 필드와 경로는
#      규격 버전에 따라 다를 수 있으므로 수업에서는 개념을 보여 주는 용도로만 쓴다.
#   compose.yaml 의 a2a-agent 서비스로 자동 실행된다. 포트 8300.
import http.server
import json
import os
import uuid

import requests

PORT = 8300
PLANT = os.environ.get("PLANT_URL", "http://plant:8200")
CARD = {
    "name": "설비 모니터링 에이전트",
    "description": "공장 온도 센서의 현재 값을 알려 준다 (읽기 전용).",
    "url": f"http://a2a-agent:{PORT}/",
    "version": "0.1",
    "capabilities": {"streaming": False},
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [{"id": "read-temperature", "name": "온도 조회",
                "description": "센서(temp01, temp02)의 현재 온도를 알려 준다.",
                "examples": ["temp01 온도 알려 줘", "모든 센서 온도"]}],
}


def handle_text(text):
    sensors = requests.get(f"{PLANT}/sensors", timeout=5).json()["sensors"]
    picked = [s for s in sensors if s["id"] in text.lower()] or sensors
    return " / ".join(f"{s['id']}({s['line']}): {s['value']}℃" for s in picked)


class Handler(http.server.BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/.well-known/agent-card.json", "/.well-known/agent.json"):
            self._json(CARD)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        rid = req.get("id")
        if req.get("method") != "message/send":
            return self._json({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}})
        parts = req["params"]["message"]["parts"]
        text = "".join(p.get("text", "") for p in parts)
        print(f"[a2a-agent] 받은 작업: {text!r}", flush=True)
        reply = handle_text(text)
        self._json({"jsonrpc": "2.0", "id": rid,
                    "result": {"kind": "message", "role": "agent", "messageId": str(uuid.uuid4()),
                               "parts": [{"kind": "text", "text": reply}]}})

    def log_message(self, fmt, *args):
        pass


print(f"설비 에이전트 시작: 포트 {PORT}  (Agent Card: /.well-known/agent-card.json)", flush=True)
http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
