# 실습 3 (클라이언트 2) : SSE - HTTP 연결을 한 번 열어 두면 서버가 변화를 밀어 준다
#   사용:  .\run.cmd 03_sse_client.py
import time

import requests

SECONDS = 10
print(f"GET http://sensor:8080/events 를 한 번 요청하고, {SECONDS}초 동안 서버가 보내는 것을 읽는다\n")

t0 = time.time()
n, delays = 0, []
with requests.get("http://sensor:8080/events", stream=True, timeout=(3, 15)) as r:
    r.encoding = "utf-8"                              # SSE 응답에는 문자 집합 표시가 없어 직접 지정한다
    print("  응답 헤더 Content-Type:", r.headers["Content-Type"])
    import json
    # chunk_size=1 : 기본값(512바이트)이면 그만큼 모일 때까지 기다려서, 2초마다 오는 작은 이벤트가 한참 뒤에야 보인다
    for line in r.iter_lines(decode_unicode=True, chunk_size=1):
        if not line.startswith("data: "):
            continue
        d = json.loads(line[6:])
        delay = time.time() - d["t"]
        n += 1
        delays.append(delay)
        note = "접속 직후의 현재 값" if n == 1 else f"바뀐 지 {delay:.2f}초 뒤에 받았다"
        print(f"  [{time.time() - t0:4.1f}초] 값 {d['value']} (version {d['version']}) - {note}")
        if time.time() - t0 > SECONDS:
            break

print(f"\nHTTP 요청은 단 1번. 서버가 필요할 때만 {n}번 보내 주었다 (낭비되는 요청 없음)")
print(f"지연은 평균 {sum(delays[1:]) / max(1, len(delays) - 1):.2f}초 (접속 직후의 첫 값은 제외)")

# 해 보라
#  1) 폴링(03_poll_client.py)과 요청 횟수, 지연을 비교해 보라
#  2) SSE 는 서버 -> 클라이언트 한 방향이다. 클라이언트가 서버에 명령을 보내려면 어떻게 해야 할까?
