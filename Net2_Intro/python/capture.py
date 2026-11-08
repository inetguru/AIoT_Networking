# tcpdump 로 "내가 일으킨 통신"을 직접 캡처한다 (Net_Intro 의 capture.py 와 같은 방식)
#   사용:  .\run.cmd capture.py mqtt      MQTT : CONNECT / SUBSCRIBE / PUBLISH 가 토픽과 값 그대로 보인다
#          .\run.cmd capture.py sse       SSE  : 열어 둔 HTTP 연결로 이벤트가 흘러온다
#          .\run.cmd capture.py ws        WebSocket : HTTP "101 Switching Protocols" 로 바뀌는 순간
#          .\run.cmd capture.py opcua     OPC UA : 글자가 아닌 "바이너리" 프로토콜
import os
import signal
import subprocess
import sys
import time

CAP_DIR = os.environ.get("CAP_DIR", "/captures")


def act_script(*cmd):
    return lambda: subprocess.run([sys.executable, *cmd], check=False)


def act_mqtt():
    # 구독자와 발행자를 함께 실행해서, 브로커를 거치는 양쪽 통신이 모두 캡처되게 한다
    sub = subprocess.Popen([sys.executable, "05_subscriber.py", "factory/#", "--seconds", "7"],
                           stdout=subprocess.DEVNULL)
    time.sleep(1.5)
    subprocess.run([sys.executable, "05_publisher.py", "--count", "3", "--interval", "1"], check=False)
    sub.wait()


SCENARIOS = {
    "mqtt": dict(filt="tcp port 1883", action=act_mqtt, find="temperature",
                 title="MQTT (Publish / Subscribe)",
                 tips=["mqtt", "mqtt.msgtype == 3  (PUBLISH)", "mqtt.topic contains \"temp01\"", "tcp.port == 1883"]),
    "sse": dict(filt="tcp port 8080", action=act_script("03_sse_client.py"), find="text/event-stream",
                title="SSE (HTTP 연결을 열어 두고 서버가 밀어 준다)",
                tips=["http", "tcp.port == 8080", "Follow -> TCP Stream 으로 'data: {...}' 줄이 이어지는 것을 본다"]),
    "ws": dict(filt="tcp port 8765", action=act_script("03_ws_client.py"), find="Switching Protocols",
               title="WebSocket (HTTP 로 시작해 Upgrade)",
               tips=["http  (Upgrade 요청과 101 응답)", "websocket", "tcp.port == 8765"]),
    "opcua": dict(filt="tcp port 4840", action=act_script("06_opcua_client.py"), find="Temperature",
                  title="OPC UA (바이너리 프로토콜)",
                  tips=["opcua", "tcp.port == 4840", "HEL / ACK / OPN / MSG 같은 바이너리 메시지 종류를 본다"]),
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
    first = p.stderr.readline()
    if "listening" not in first:
        print("  tcpdump 시작 실패:", first.strip())
        sys.exit(1)
    time.sleep(0.5)

    print("\n=== 통신을 일으킨다 (몇 초 걸린다)")
    sc["action"]()
    time.sleep(1)
    p.send_signal(signal.SIGINT)
    p.wait(timeout=5)

    lines = run(["tcpdump", "-nn", "-tt", "-r", path]).splitlines()
    print(f"\n=== 캡처 결과: 총 {len(lines)} 개 패킷 (앞 20개)")
    for ln in lines[:20]:
        print(" ", ln[:160])

    ascii_dump = run(["tcpdump", "-nn", "-A", "-r", path])
    found = sc["find"] in ascii_dump
    print(f"\n=== 패킷 안에서 '{sc['find']}' 글자를 찾았는가?  ->  {'찾았다 (글자로 보인다)' if found else '못 찾았다'}")
    print("\n=== Windows 에서 Wireshark 로 열어 보라")
    print(f"  파일: Net2_Intro\\captures\\live_{name}.pcap")
    print("  표시 필터 예:")
    for t in sc["tips"]:
        print("   -", t)


main()
