# tcpdump 로 "내가 일으킨 통신"을 직접 캡처한다 - 결과 파일(.pcap)은 Windows 의 Wireshark 로 열 수 있다
#   사용:  .\run.cmd capture.py http        HTTP  : 요청/응답 글자(센서 값)가 그대로 보인다
#          .\run.cmd capture.py https       HTTPS : TLS 로 암호화되어 값이 보이지 않는다
#          .\run.cmd capture.py tcp         TCP   : 3-way handshake, 데이터, 연결 종료
#          .\run.cmd capture.py udp         UDP   : handshake 없이 데이터그램만
#          .\run.cmd capture.py multicast   Multicast : 목적지가 그룹 주소(01:00:5e...)
import os
import signal
import subprocess
import sys
import time

CAP_DIR = os.environ.get("CAP_DIR", "/captures")


# ---------------------------------------------------------------- 시나리오별 "통신을 일으키는 동작"
def act_http():
    import requests
    r = requests.get("http://web:4000/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst",
                     params={"dataType": "JSON", "nx": 98, "ny": 76, "base_date": "20260101", "base_time": "1200"})
    print(f"  (클라이언트) HTTP {r.status_code}, 응답 {len(r.content)} 바이트")


def act_https():
    import requests
    import urllib3
    urllib3.disable_warnings()                                        # 자체 서명 인증서 경고 숨김
    r = requests.get("https://tls:8443/", verify=False)
    print(f"  (클라이언트) HTTPS {r.status_code}, 응답 본문: {r.text}   <- 클라이언트는 복호화해서 읽을 수 있다")


def act_script(name):
    return lambda: subprocess.run([sys.executable, name], check=False)


SCENARIOS = {
    "http": dict(
        filt="(tcp port 4000) or arp", action=act_http, find="T1H",
        title="HTTP (암호화 없음)",
        tips=["http", "tcp.flags.syn == 1", "오른쪽 클릭 -> Follow -> TCP Stream"]),
    "https": dict(
        filt="(tcp port 8443) or arp", action=act_https, find="temp-01",
        title="HTTPS (TLS 암호화)",
        tips=["tls", "tls.handshake.type == 1  (ClientHello)", "tcp.port == 8443"]),
    "tcp": dict(
        filt="(tcp port 9000) or arp", action=act_script("03_tcp_client.py"), find="temp=23.5",
        title="TCP (연결형, 바이트 스트림)",
        tips=["tcp.flags.syn == 1  (연결 시작)", "tcp.flags.fin == 1  (연결 종료)", "tcp.len > 0  (데이터가 든 패킷)"]),
    "udp": dict(
        filt="(udp port 9001) or arp", action=act_script("04_udp_client.py"), find="temp=23.5",
        title="UDP (비연결형, 데이터그램)",
        tips=["udp", "udp.port == 9001", "TCP 와 달리 SYN/ACK/FIN 이 없다"]),
    "multicast": dict(
        filt="(udp port 5007) or igmp or arp", action=act_script("05_mcast_sender.py"), find="temp=23.5",
        title="Multicast (1 : N)",
        tips=["ip.dst == 224.1.1.1", "eth.dst[0:3] == 01:00:5e  (multicast MAC)", "udp.port == 5007"]),
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SCENARIOS:
        print("사용법: capture.py <시나리오>   시나리오:", ", ".join(SCENARIOS))
        sys.exit(1)
    name = sys.argv[1]
    sc = SCENARIOS[name]
    os.makedirs(CAP_DIR, exist_ok=True)
    path = os.path.join(CAP_DIR, f"live_{name}.pcap")
    if os.path.exists(path):
        os.remove(path)

    print(f"=== 캡처 시작: {sc['title']}")
    print(f"  tcpdump -i eth0 -w live_{name}.pcap   필터: {sc['filt']}")
    p = subprocess.Popen(["tcpdump", "-i", "eth0", "-n", "-U", "-w", path, sc["filt"]],
                         stderr=subprocess.PIPE, text=True)
    first = p.stderr.readline()                                       # "listening on eth0 ..." 가 나오면 준비 완료
    if "listening" not in first:
        print("  tcpdump 시작 실패:", first.strip())
        sys.exit(1)
    time.sleep(0.5)

    print("\n=== 통신을 일으킨다")
    sc["action"]()
    time.sleep(1)                                                     # 마지막 패킷까지 기다린다
    p.send_signal(signal.SIGINT)
    p.wait(timeout=5)

    print("\n=== 캡처 결과 (tcpdump -nn -e -r : 시각 / MAC / IP.Port / TCP·UDP 정보)")
    lines = run(["tcpdump", "-nn", "-e", "-tt", "-r", path]).splitlines()
    for ln in lines[:30]:
        print(" ", ln[:170])
    if len(lines) > 30:
        print(f"  ... (이하 {len(lines) - 30}줄 생략)")
    print(f"\n  총 {len(lines)} 개 패킷이 {os.path.basename(path)} 에 저장되었다")

    ascii_dump = run(["tcpdump", "-nn", "-A", "-r", path])
    found = sc["find"] in ascii_dump
    print(f"\n=== 패킷 안에서 '{sc['find']}' 글자를 찾았는가?  ->  {'찾았다 (평문으로 보인다)' if found else '못 찾았다 (보이지 않는다)'}")
    if found:
        for ln in ascii_dump.splitlines():
            if sc["find"] in ln:
                print("  ", ln.strip()[:150])
                break

    print("\n=== Windows 에서 Wireshark 로 열어 보라")
    print(f"  파일: Net_Intro\\captures\\live_{name}.pcap  (더블클릭 또는 Wireshark 의 File > Open)")
    print("  표시 필터 예:")
    for t in sc["tips"]:
        print("   -", t)


main()
