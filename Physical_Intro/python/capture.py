# tcpdump 로 "내가 일으킨 통신"을 직접 캡처한다 (Net_Intro 의 capture.py 와 같은 방식)
#   사용:  .\run.cmd capture.py modbus     Modbus TCP : 12 바이트짜리 요청과 바이너리 응답
#          .\run.cmd capture.py gateway    게이트웨이 : Modbus 로 읽고 MQTT 로 내보내는 두 통신이 한 파일에
import os
import signal
import subprocess
import sys
import time

CAP_DIR = os.environ.get("CAP_DIR", "/captures")


def act_script(*cmd):
    return lambda: subprocess.run([sys.executable, *cmd], check=False, stdout=subprocess.DEVNULL)


SCENARIOS = {
    "modbus": dict(filt="tcp port 5020", action=act_script("02_modbus_raw.py"), find="",
                   title="Modbus TCP (바이너리, 인증·암호화 없음)",
                   tips=["mbtcp", "tcp.port == 5020", "패킷을 고른 뒤 아래 상세 창에서 'Modbus/TCP' 항목(전송 ID, 기능 코드, 레지스터 값)을 펼쳐 본다"]),
    "gateway": dict(filt="tcp port 5020 or tcp port 1883", action=act_script("04_gateway.py"), find="temp01",
                    title="게이트웨이 (Modbus 로 읽고 MQTT 로 내보낸다)",
                    tips=["mbtcp || mqtt", "mbtcp  (값만 오가는 쪽)", "mqtt  (토픽과 JSON 이 글자로 보이는 쪽)"]),
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
    print(f"\n=== 캡처 결과: 총 {len(lines)} 개 패킷 (앞 12개)")
    for ln in lines[:12]:
        print(" ", ln[:150])

    if name == "modbus":
        data_pkts = [ln for ln in lines if "length" in ln and not ln.rstrip().endswith("length 0")]
        print(f"\n=== 데이터가 실린 패킷 {len(data_pkts)} 개 중 첫 요청을 16진수로 (tcpdump -X)")
        hexdump = run(["tcpdump", "-nn", "-X", "-c", "6", "-r", path]).splitlines()
        shown = 0
        for i, ln in enumerate(hexdump):
            if "length 12" in ln and shown == 0:                      # 요청 12 바이트
                print("\n".join("  " + x for x in hexdump[i:i + 5]))
                shown = 1
        print("  -> 꼬리의 12 바이트가 실습 2 에서 손으로 만든 요청 그대로다 (00 01 00 00 00 06 01 04 00 00 00 02)")
    else:
        ascii_dump = run(["tcpdump", "-nn", "-A", "-r", path])
        found = sc["find"] in ascii_dump
        print(f"\n=== 패킷 안에서 '{sc['find']}' 글자를 찾았는가?  ->  {'찾았다 (MQTT 쪽은 글자로 보인다)' if found else '못 찾았다'}")

    print("\n=== Windows 에서 Wireshark 로 열어 보라")
    print(f"  파일: Physical_Intro\\captures\\live_{name}.pcap")
    print("  표시 필터 예:")
    for t in sc["tips"]:
        print("   -", t)


main()
