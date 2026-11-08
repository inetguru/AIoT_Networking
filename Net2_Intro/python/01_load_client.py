# 실습 1 (클라이언트) : 손님 N명이 "동시에" 몰려오면 세 서버는 어떻게 다를까?
#   사용:  .\run.cmd 01_load_client.py                  (기다리는 일(IO) 10건)
#          .\run.cmd 01_load_client.py --work cpu       (계산하는 일(CPU) 10건)
#          .\run.cmd 01_load_client.py --n 20
import argparse
import socket
import threading
import time

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=10, help="동시에 요청하는 손님 수")
ap.add_argument("--work", choices=["io", "cpu"], default="io")
args = ap.parse_args()

SERVERS = [("blocking", "srv-blocking", 9100),
           ("threaded", "srv-threaded", 9101),
           ("async", "srv-async", 9102)]


def one(host, port, results, i, t0):
    s = socket.create_connection((host, port), timeout=120)
    s.sendall((args.work.upper() + "\n").encode())
    s.recv(100)
    s.close()
    results[i] = time.perf_counter() - t0          # 이 손님이 응답을 받기까지 걸린 시간


what = "기다리는 일 (1건 = 1초 기다림)" if args.work == "io" else "계산하는 일 (1건 = 약 0.5초 계산)"
print(f"손님 {args.n}명이 동시에 요청한다 — 일의 종류: {what}\n")
print(f"{'서버':10s} {'전체 소요':>9s} {'가장 빠른 응답':>14s} {'가장 늦은 응답':>14s}")
for name, host, port in SERVERS:
    results = [0.0] * args.n
    t0 = time.perf_counter()
    threads = [threading.Thread(target=one, args=(host, port, results, i, t0)) for i in range(args.n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = time.perf_counter() - t0
    print(f"{name:10s} {total:8.1f}초 {min(results):13.1f}초 {max(results):13.1f}초")
    time.sleep(0.5)

# 해 보라
#  1) 기다리는 일(IO)에서 blocking 은 왜 N초가 걸리는가? threaded 와 async 는 왜 약 1초인가?
#  2) --work cpu 로 바꾸면 세 서버의 결과가 비슷해진다. 왜일까? (async 는 "기다림"이 없을 때 무엇을 할 수 있는가)
#  3) async 서버는 스레드를 하나도 만들지 않았다. 그런데도 1초에 끝난 비결은?
#  4) 센서 1000개가 1초에 한 번씩 값을 보내는 서버라면 어떤 방식이 적합할까?
