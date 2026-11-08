# 실습 3 (클라이언트) : TCP 로 센서 값 3개를 따로따로(send 3번) 보낸다
#   사용:  .\run.cmd 03_tcp_client.py            (기본 3개)
#          .\run.cmd 03_tcp_client.py --port 9999    (아무도 없는 포트에 연결해 보기)
import argparse
import socket

ap = argparse.ArgumentParser()
ap.add_argument("--host", default="tcp-server")
ap.add_argument("--port", type=int, default=9000)
ap.add_argument("messages", nargs="*", default=["temp=23.5;", "hum=55;", "press=1013;"])
args = ap.parse_args()

try:
    s = socket.create_connection((args.host, args.port), timeout=5)   # 연결 (3-way handshake)
except ConnectionRefusedError:
    raise SystemExit(f"연결 거부됨: {args.host}:{args.port} 에서 기다리는 프로그램이 없다 (TCP 는 상대가 없으면 바로 알 수 있다)")
print(f"연결됨: {args.host}:{args.port}")

for m in args.messages:
    s.sendall(m.encode())                                             # send 를 메시지마다 따로 호출
    print(f"  send: {m!r}")

s.shutdown(socket.SHUT_WR)                                            # "더 보낼 것 없다" (FIN)
print("서버 응답:", s.recv(1024).decode())
s.close()

# 해 보라
#  1) 클라이언트는 send 를 3번 했다. 서버 로그(docker compose logs tcp-server)에서 recv 는 몇 번이었나?
#  2) 그렇다면 TCP 는 메시지의 "경계"를 보존하는가? (Stream)
#  3) --port 9999 로 실행하면 어떻게 되는가?
