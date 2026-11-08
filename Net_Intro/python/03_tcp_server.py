# 실습 3 (서버) : TCP 서버 - 연결을 맺고, 흐르는 "바이트 스트림"을 받는다
#   compose.yaml 의 tcp-server 서비스로 자동 실행된다. 로그 보기: docker compose logs tcp-server
import socket
import time

PORT = 9000

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)          # SOCK_STREAM = TCP
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", PORT))
srv.listen()
print(f"TCP 서버 시작: 포트 {PORT} 에서 연결을 기다린다", flush=True)

while True:
    conn, addr = srv.accept()                                    # 3-way handshake 가 끝나면 여기서 반환
    print(f"\n[연결] {addr[0]}:{addr[1]} 와 연결되었다", flush=True)
    time.sleep(1)                                                # 일부러 늦게 읽는다 (그 사이 데이터가 쌓인다)
    calls, total = 0, b""
    while True:
        data = conn.recv(1024)                                   # 쌓인 만큼 한꺼번에 읽는다
        if not data:                                             # 빈 값 = 상대가 연결을 닫았다 (FIN)
            break
        calls += 1
        total += data
        print(f"  recv #{calls}: {len(data)} 바이트 -> {data!r}", flush=True)
    conn.sendall(f"서버가 받은 글자: {total.decode()}".encode())
    conn.close()
    print(f"[종료] recv 를 {calls}번 호출해서 총 {len(total)} 바이트를 받았다", flush=True)
