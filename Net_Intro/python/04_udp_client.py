# 실습 4 (클라이언트) : UDP 로 센서 값 3개를 보낸다
#   사용:  .\run.cmd 04_udp_client.py
#          .\run.cmd 04_udp_client.py --port 9999    (아무도 없는 포트로 보내 보기)
import argparse
import socket

ap = argparse.ArgumentParser()
ap.add_argument("--host", default="udp-server")
ap.add_argument("--port", type=int, default=9001)
ap.add_argument("messages", nargs="*", default=["temp=23.5;", "hum=55;", "press=1013;"])
args = ap.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)             # 연결 과정(handshake)이 없다
for m in args.messages:
    s.sendto(m.encode(), (args.host, args.port))                 # 보내고 끝. 받았는지는 알 수 없다
    print(f"  sendto: {m!r}")
print("모두 보냈다. (상대가 있든 없든 오류 없이 끝난다)")

# 해 보라
#  1) 서버 로그(docker compose logs udp-server)에서 datagram 은 몇 개로 도착했는가? TCP 와 비교해 보라
#  2) --port 9999 로 실행하면 오류가 나는가? TCP(--port 9999)와 비교해 보라
#  3) 센서 값을 1초마다 보내는 장치라면, 한두 개가 사라져도 괜찮을까?
