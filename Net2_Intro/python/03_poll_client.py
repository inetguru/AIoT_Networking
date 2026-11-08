# 실습 3 (클라이언트 1) : Polling - "바뀌었나요?"를 계속 묻는다
#   사용:  .\run.cmd 03_poll_client.py            (0.5초마다 10초 동안)
#          .\run.cmd 03_poll_client.py --interval 2
import argparse
import time

import requests

ap = argparse.ArgumentParser()
ap.add_argument("--interval", type=float, default=0.5, help="몇 초마다 물어볼까")
ap.add_argument("--seconds", type=float, default=10)
args = ap.parse_args()

session = requests.Session()
last, requests_n, new_n, delays = None, 0, 0, []
end = time.time() + args.seconds
print(f"{args.interval}초마다 GET http://sensor:8080/temp 를 {args.seconds:.0f}초 동안 반복한다\n")
while time.time() < end:
    d = session.get("http://sensor:8080/temp", timeout=5).json()
    requests_n += 1
    if d["version"] != last:
        last = d["version"]
        new_n += 1
        delay = time.time() - d["t"]                 # 값이 바뀐 뒤 우리가 알게 되기까지
        delays.append(delay)
        print(f"  새 값 {d['value']} (version {d['version']}) - 바뀐 지 {delay:.2f}초 뒤에 알았다")
    time.sleep(args.interval)

print(f"\n요청 {requests_n}번 중 새 값은 {new_n}번 -> {requests_n - new_n}번은 '바뀐 게 없다'는 응답이었다 (낭비)")
print(f"변화를 알게 되기까지 평균 {sum(delays[1:]) / max(1, len(delays) - 1):.2f}초 걸렸다")

# 해 보라
#  1) --interval 2 와 --interval 0.1 로 바꿔 보라. 낭비되는 요청 수와 지연은 어떻게 달라지는가?
#  2) 센서 1000대를 0.1초마다 폴링하면 서버는 1초에 몇 번의 요청을 받는가?
