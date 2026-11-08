# 실습 3-2 : 가상 CAN 버스 - 한 버스에 노드 셋, 모두가 모든 프레임을 듣는다
#   python-can 의 'virtual' 버스는 한 프로세스 안의 노드(스레드)끼리 연결된다 (실제 CAN 장치 없이 개념을 보여 준다)
#   사용:  .\run.cmd 03_can_bus.py
import struct
import sys
import threading
import time

import can

CHANNEL = "factory"
stop = threading.Event()
_lock = threading.Lock()


def say(msg):
    with _lock:                                    # 여러 스레드의 출력이 섞이지 않게 한다
        sys.stdout.write(msg + chr(10)); sys.stdout.flush()


def temp_ecu():
    """온도 센서 ECU: 0x100 번 메시지를 100 ms 마다 방송한다. 데이터: 온도 x10 (2바이트) + 상태 (1바이트)"""
    bus = can.Bus(interface="virtual", channel=CHANNEL)
    for k in range(8):
        t = 235 + k
        bus.send(can.Message(arbitration_id=0x100, data=struct.pack(">HB", t, 0), is_extended_id=False))
        time.sleep(0.1)
    time.sleep(0.3)
    stop.set()
    bus.shutdown()


def controller():
    """제어기: 0x100 만 듣는다 (필터). 온도가 24.0 ℃ 를 넘으면 0x200 번 '냉각' 명령을 방송한다"""
    bus = can.Bus(interface="virtual", channel=CHANNEL, can_filters=[{"can_id": 0x100, "can_mask": 0x7FF}])
    sent = False
    while not stop.is_set():
        m = bus.recv(timeout=0.2)
        if m is None:
            continue
        t10, status = struct.unpack(">HB", bytes(m.data[:3]))
        say(f"  [제어기] 0x{m.arbitration_id:03X} 수신: 온도 {t10 / 10:.1f} ℃")
        if t10 / 10 > 24.0 and not sent:
            bus.send(can.Message(arbitration_id=0x200, data=[1], is_extended_id=False))
            say("  [제어기] 24 ℃ 초과 → 0x200 '냉각 ON' 방송")
            sent = True
    bus.shutdown()


def logger():
    """로거: 필터 없이 버스의 모든 프레임을 기록한다 (진단 도구처럼)"""
    bus = can.Bus(interface="virtual", channel=CHANNEL)
    say("  [로거] 시작: 버스의 모든 프레임을 기록한다")
    seen = 0
    while not stop.is_set():
        m = bus.recv(timeout=0.2)
        if m is not None:
            seen += 1
            say(f"  [로거 {seen:2d}] ID=0x{m.arbitration_id:03X}  DLC={m.dlc}  데이터={bytes(m.data).hex(' ')}")
    bus.shutdown()


print("=== 한 버스(factory)에 노드 3개: 온도 센서 ECU / 제어기 / 로거")
threads = [threading.Thread(target=f) for f in (logger, controller)]
for t in threads:
    t.start()
time.sleep(0.3)
temp_ecu()
for t in threads:
    t.join()

print("\n=== 관찰")
print("  - 프레임에는 '보내는 노드의 주소'도 '받는 노드의 주소'도 없다. ID 는 '메시지의 종류'(0x100 = 온도, 0x200 = 냉각 명령)")
print("  - 로거는 모든 프레임을, 제어기는 필터로 0x100 만 받는다 (수신 쪽에서 고른다 = 방송 + 필터)")
print("  - 한 프레임의 데이터는 최대 8 바이트 (CAN FD 는 64). 짧고, 자주, 확실하게 — 자동차·로봇의 제어용")

# 해 보라
#  1) 로거가 본 프레임 중 제어기가 '무시한' 것은 어떤 것인가?
#  2) 온도 센서가 0x100 을 100 ms 마다 보낸다. 제어기가 한 번 놓치면(수신 실패) 어떻게 되는가?  (주기적 방송의 장점)
#  3) 같은 온도 값을 Modbus(요청-응답)와 CAN(방송)으로 전달할 때의 차이를 말해 보라
