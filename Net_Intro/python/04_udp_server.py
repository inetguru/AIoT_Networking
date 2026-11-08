# 실습 4 (서버) : UDP 서버 - 연결 없이 "편지(데이터그램)"가 한 통씩 도착한다
#   compose.yaml 의 udp-server 서비스로 자동 실행된다. 로그 보기: docker compose logs udp-server
import socket

PORT = 9001

srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # SOCK_DGRAM = UDP
srv.bind(("0.0.0.0", PORT))
print(f"UDP 서버 시작: 포트 {PORT} (listen/accept 없음 - 연결이라는 개념이 없다)", flush=True)

n = 0
while True:
    data, addr = srv.recvfrom(1024)                              # 한 번 호출 = 데이터그램 한 개
    n += 1
    print(f"datagram #{n} from {addr[0]}:{addr[1]}: {len(data)} 바이트 -> {data!r}", flush=True)
