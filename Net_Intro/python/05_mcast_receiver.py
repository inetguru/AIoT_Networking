# 실습 5 (수신자) : Multicast 그룹에 "가입"하고 기다린다
#   compose.yaml 의 mcast-rx1, mcast-rx2 서비스로 자동 실행된다. 로그 보기: docker compose logs mcast-rx1
import os
import socket
import struct

GROUP, PORT = "224.1.1.1", 5007                                  # 224.0.0.0 ~ 239.255.255.255 = multicast 주소 대역
NAME = os.environ.get("NAME", socket.gethostname())

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", PORT))
mreq = struct.pack("4sl", socket.inet_aton(GROUP), socket.INADDR_ANY)
s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)   # "이 그룹 방송을 듣겠다" (가입)
print(f"[{NAME}] 그룹 {GROUP}:{PORT} 에 가입하고 기다린다", flush=True)

while True:
    data, addr = s.recvfrom(1024)
    print(f"[{NAME}] {addr[0]} 에서 받음: {data!r}", flush=True)
