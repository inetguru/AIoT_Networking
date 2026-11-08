# 실습 2 : HTTP는 "글자"일 뿐이다 - 소켓으로 HTTP 요청을 손으로 보내 보기
#   requests 같은 라이브러리 없이, TCP 연결에 글자를 직접 써서 보낸다.
import socket

HOST, PORT = "web", 4000
PATH = "/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst?dataType=JSON&nx=98&ny=76"

# HTTP 요청 = 줄 단위 글자. 줄 끝은 \r\n, 헤더가 끝나면 빈 줄 하나
request = (
    f"GET {PATH} HTTP/1.1\r\n"
    f"Host: {HOST}:{PORT}\r\n"
    "Connection: close\r\n"
    "\r\n"
)
print("=== 우리가 보내는 글자 ===")
print(request.replace("\r\n", "\\r\\n\n"))

s = socket.create_connection((HOST, PORT), timeout=5)    # TCP 연결 (3-way handshake)
s.sendall(request.encode())                              # 글자를 바이트로 바꿔 전송
chunks = []
while True:
    data = s.recv(4096)                                  # 서버가 연결을 닫을 때까지 받는다
    if not data:
        break
    chunks.append(data)
s.close()
response = b"".join(chunks).decode()

head, _, body = response.partition("\r\n\r\n")
print("=== 서버가 보낸 글자 (헤더) ===")
print(head)
print("\n=== 서버가 보낸 글자 (본문) ===")
print(body[:300], "...")

# 참고: 본문 맨 앞의 숫자(예: 384)는 "이어서 오는 조각의 크기(16진수)"다. 응답 헤더의 Transfer-Encoding: chunked 때문이다.
#       (requests 같은 라이브러리는 이런 처리를 대신 해 준다)

# 해 보라
#  1) 요청의 첫 줄 "GET ... HTTP/1.1" 에서 어떤 부분이 Method, 어떤 부분이 URL 경로인가?
#  2) "Connection: close" 줄을 지우고 실행해 보라. 프로그램이 끝나지 않는다면 왜일까?
#  3) PATH 를 존재하지 않는 경로로 바꾸면 응답의 첫 줄(상태 줄)은 어떻게 바뀌는가?
