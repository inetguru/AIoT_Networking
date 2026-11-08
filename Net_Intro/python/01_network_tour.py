# 실습 1 : 통신에 필요한 "주소"들을 내 눈으로 확인하기
#   도메인 이름 -> IP 주소 -> Port 번호 -> MAC 주소  (응용 / 네트워크 / 전송 / 링크 계층)
import socket
import subprocess


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


print("=== 1) 나 자신 (이 컨테이너)")
print("  호스트 이름 :", socket.gethostname())
print("  MAC 주소    :", open("/sys/class/net/eth0/address").read().strip(), "  (링크 계층: 같은 네트워크 안에서 장치를 구분)")
print("  IP 주소     :", sh("ip -4 -o addr show eth0 | awk '{print $4}'"), "  (네트워크 계층: 인터넷에서 컴퓨터를 구분)")
print("  기본 게이트웨이:", sh("ip route | awk '/default/ {print $3}'"))

print("\n=== 2) 이름 -> 주소 (DNS) : 'web' 은 사람이 읽는 이름, 통신은 IP 주소로 한다")
for name in ("web", "tcp-server"):
    try:
        print(f"  {name:12s} ->", socket.gethostbyname(name))
    except OSError as e:
        print(f"  {name:12s} -> 찾을 수 없음 ({e})")

print("\n=== 3) 연결해 보기: web 서버(포트 4000)에 TCP 연결")
s = socket.create_connection(("web", 4000), timeout=5)
me, peer = s.getsockname(), s.getpeername()
print(f"  내 쪽   : {me[0]}:{me[1]}   <- Port 는 운영체제가 임시로 정해 준 큰 번호")
print(f"  서버 쪽 : {peer[0]}:{peer[1]}   <- 서버 프로그램이 기다리는 약속된 번호")
mac = sh(f"ip neigh show {peer[0]} | awk '{{print $5}}'")
print(f"  서버의 MAC 주소 : {mac}   (같은 네트워크라 ARP 로 알아낸 값)")
s.close()

print("\n=== 4) 정리 : 한 번의 통신에 필요한 주소")
print("  응용 계층  도메인 이름   web")
print(f"  전송 계층  Port          {me[1]} -> {peer[1]}")
print(f"  네트워크   IP 주소       {me[0]} -> {peer[0]}")
print(f"  링크 계층  MAC 주소      (내 MAC) -> {mac}")

# 해 보라
#  1) .\run.cmd 01_network_tour.py 를 두 번 실행해 보라. 내 쪽 Port 번호는 같은가, 다른가? 서버 쪽 Port 는?
#  2) 위 표를 슬라이드의 "통신에 필요한 주소들" 표와 비교해 보라
