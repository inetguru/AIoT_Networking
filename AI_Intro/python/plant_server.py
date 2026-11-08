# "기존 시스템" 역할의 공장 설비 REST API (모의). AI Agent 가 도구로 부르고, MCP 서버가 감싸는 대상이다.
#   GET  /sensors                     센서 목록
#   GET  /sensors/{id}                센서 한 개의 현재 값
#   PUT  /sensors/{id}/setpoint       설정 온도 변경  (body: {"value": 25.0})  <- "쓰기" 동작
#   compose.yaml 의 plant 서비스로 자동 실행된다. 포트 8200.
import http.server
import json
import math
import re
import time

PORT = 8200
SENSORS = {
    "temp01": {"line": "Line1", "setpoint": 25.0, "phase": 0.0},
    "temp02": {"line": "Line2", "setpoint": 22.0, "phase": 1.7},
}


def current(sid):
    s = SENSORS[sid]
    # 설정 온도 근처에서 천천히 출렁이는 값 (설정 온도를 바꾸면 값도 따라 바뀐다)
    value = s["setpoint"] - 1.5 + 1.0 * math.sin(time.time() / 20 + s["phase"])
    return {"id": sid, "line": s["line"], "value": round(value, 1), "unit": "C", "setpoint": s["setpoint"]}


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/sensors":
            self._send({"sensors": [current(s) for s in SENSORS]})
        else:
            m = re.fullmatch(r"/sensors/(\w+)", self.path)
            if m and m.group(1) in SENSORS:
                self._send(current(m.group(1)))
            else:
                self._send({"error": "not found"}, 404)

    def do_PUT(self):
        m = re.fullmatch(r"/sensors/(\w+)/setpoint", self.path)
        if not (m and m.group(1) in SENSORS):
            return self._send({"error": "not found"}, 404)
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        value = float(data["value"])
        SENSORS[m.group(1)]["setpoint"] = value
        print(f"[plant] ★ 설정 온도 변경: {m.group(1)} -> {value}", flush=True)
        self._send(current(m.group(1)))

    def log_message(self, fmt, *args):
        print("[plant]", self.command, self.path, flush=True)


print(f"plant API 시작: 포트 {PORT}  (센서: {', '.join(SENSORS)})", flush=True)
http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
