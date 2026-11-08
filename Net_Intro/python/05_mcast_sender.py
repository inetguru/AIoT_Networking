# 실습 5 (송신자) : 한 번 보내면, 그룹에 가입한 모두가 받는다 (1 : N)
#   사용:  .\run.cmd 05_mcast_sender.py
#   확인:  docker compose logs mcast-rx1 mcast-rx2
import socket

GROUP, PORT = "224.1.1.1", 5007

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)       # 라우터를 몇 번 넘어갈 수 있는가
for m in ("temp=23.5;", "hum=55;", "press=1013;"):
    s.sendto(m.encode(), (GROUP, PORT))                           # 받는 사람은 "그룹 주소" 하나
    print(f"  보냄 -> {GROUP}:{PORT} : {m!r}")

# 해 보라
#  1) mcast-rx1, mcast-rx2 가 모두 받았는가? (보낸 것은 한 번인데...)
#  2) Unicast 로 3명에게 보내려면 몇 번 보내야 할까? Multicast 의 장점은?
#  3) capture.py multicast 로 캡처하면 목적지 IP 와 목적지 MAC 이 어떻게 보이는가? (01:00:5e 로 시작)
