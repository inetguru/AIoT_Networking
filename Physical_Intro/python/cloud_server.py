# 가상 "클라우드 AI" - 센서 값을 받아 이상 여부를 판단해 준다.
#   판단 능력은 있지만 멀리 있어서 응답이 늦다: 지연(기본 400 ms ± 100)은 시뮬레이션이다 (CLOUD_DELAY_MS 로 바꾼다)
#   POST /decide  {"temp": 27.3, "history": [...]}  ->  {"action": "cool" | "none", ...}
import json
import os
import random
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DELAY = float(os.environ.get("CLOUD_DELAY_MS", "400")) / 1000


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        time.sleep(max(0.0, random.gauss(DELAY, DELAY * 0.25)))          # 먼 거리·혼잡을 흉내 낸다
        hist = body.get("history", [])
        rising = len(hist) >= 3 and hist[-1] - hist[-3] > 0.6            # 이 정도면 (초당 3 ℃ 상승) 이상
        action = "cool" if (body.get("temp", 0) > 27.0 or rising) else "none"
        out = json.dumps({"action": action, "by": "cloud-ai"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


print(f"가상 클라우드 AI 시작: :8400  (응답 지연 약 {DELAY * 1000:.0f} ms, 시뮬레이션)", flush=True)
ThreadingHTTPServer(("0.0.0.0", 8400), H).serve_forever()
