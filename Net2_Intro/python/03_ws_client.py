# 실습 3 (클라이언트 3) : WebSocket - 양방향 연결을 유지한다
#   사용:  .\run.cmd 03_ws_client.py
import json
import time

from websockets.sync.client import connect

SECONDS = 10
print(f"ws://sensor:8765 에 연결해 {SECONDS}초 동안 서버가 보내는 값을 받는다\n")

t0 = time.time()
n, delays = 0, []
with connect("ws://sensor:8765") as ws:               # HTTP 로 시작해 "WebSocket 으로 바꾸자(Upgrade)" 하고 연결을 유지한다
    while time.time() - t0 < SECONDS:
        try:
            d = json.loads(ws.recv(timeout=3))
        except TimeoutError:
            continue
        delay = time.time() - d["t"]
        n += 1
        delays.append(delay)
        print(f"  [{time.time() - t0:4.1f}초] 새 값 {d['value']} (version {d['version']}) - 바뀐 지 {delay:.2f}초 뒤에 받았다")
    ws.send("hello from client")                      # 반대 방향(클라이언트 -> 서버)도 같은 연결로 보낼 수 있다
    print("\n  (클라이언트 -> 서버 방향으로도 같은 연결에 메시지를 보냈다)")

print(f"\n연결은 1개. 서버가 {n}번 밀어 주었다. 지연은 평균 {sum(delays[1:]) / max(1, len(delays) - 1):.2f}초")

# 해 보라
#  1) SSE(03_sse_client.py)와 WebSocket 의 차이는? (방향, 프로토콜)
#  2) capture.py ws 로 캡처해 "HTTP/1.1 101 Switching Protocols" 를 찾아보라
