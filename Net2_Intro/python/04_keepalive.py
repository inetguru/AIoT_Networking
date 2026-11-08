# 실습 4 : HTTP/1.0 방식(요청마다 연결) vs HTTP/1.1 Keep-Alive(연결 재사용) - tcpdump 로 "연결 개수"를 센다
#   사용:  .\run.cmd 04_keepalive.py
import signal
import subprocess
import time

import requests

URL = "http://web:4000/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?dataType=JSON&nx=98&ny=76"
N = 5


def count_connections(action):
    """action 을 실행하는 동안 tcpdump 로 SYN(연결 시작) 패킷 수를 센다."""
    pcap = "/tmp/keepalive.pcap"
    p = subprocess.Popen(["tcpdump", "-i", "eth0", "-n", "-U", "-w", pcap, "tcp port 4000"],
                         stderr=subprocess.PIPE, text=True)
    p.stderr.readline()                               # "listening on eth0" 가 나오면 준비 완료
    time.sleep(0.5)
    t0 = time.perf_counter()
    action()
    elapsed = time.perf_counter() - t0
    time.sleep(0.5)
    p.send_signal(signal.SIGINT)
    p.wait(timeout=5)
    out = subprocess.run(["tcpdump", "-nn", "-r", pcap], capture_output=True, text=True).stdout
    syn = sum(1 for ln in out.splitlines() if "Flags [S]," in ln)
    return syn, elapsed


def new_connection_each_time():
    for _ in range(N):
        requests.get(URL, timeout=5)                  # 호출할 때마다 새 연결을 만들고 닫는다


def reuse_connection():
    with requests.Session() as s:                     # 한 연결을 계속 쓴다 (Keep-Alive)
        for _ in range(N):
            s.get(URL, timeout=5)


print(f"같은 서버에 HTTP 요청을 {N}번 보낸다. tcpdump 로 TCP 연결 시작(SYN)이 몇 번인지 센다.\n")
a, ta = count_connections(new_connection_each_time)
b, tb = count_connections(reuse_connection)
print(f"  요청마다 새 연결 (HTTP/1.0 방식)    : TCP 연결 {a}번,  {ta * 1000:6.1f} ms")
print(f"  연결 재사용     (HTTP/1.1 Keep-Alive): TCP 연결 {b}번,  {tb * 1000:6.1f} ms")
print("\n연결을 맺을 때마다 3-way handshake 가 필요하다. 재사용하면 그 비용이 한 번뿐이다.")

# 해 보라
#  1) 요청 횟수 N 을 50 으로 늘리면 두 방식의 차이는 어떻게 될까?
#  2) 브라우저가 한 서버에 연결을 6개씩 여는 이유(HTTP/1.1 의 한계)와, HTTP/2 가 연결 1개로 해결하는 방법을 생각해 보라
