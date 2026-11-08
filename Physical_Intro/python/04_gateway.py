# 실습 4 : 게이트웨이 - Modbus(필드버스)로 읽어서 MQTT(IT 쪽)로 내보낸다
#   현장에는 Modbus/CAN 같은 '값만 오가는' 프로토콜이 있고, 위쪽 시스템(클라우드, AI)은 '이름과 단위가 있는' JSON/MQTT 를 쓴다.
#   그 사이를 이어 주는 것이 게이트웨이다.  하는 일: (1) 읽는다  (2) 의미를 붙인다(이름·배율·단위)  (3) 내보낸다
#   사용:  .\run.cmd 04_gateway.py
import json
import os
import threading
import time

import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient

TOPIC = "factory/line1/temp01"
received = []


def on_message(client, userdata, msg):
    received.append(msg)
    print(f"  [구독자] {msg.topic}  ({len(msg.payload)} 바이트)  {msg.payload.decode()}", flush=True)


sub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
sub.on_message = on_message
sub.connect(os.environ.get("MQTT_HOST", "mosquitto"))
sub.subscribe("factory/#")
sub.loop_start()

pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
pub.connect(os.environ.get("MQTT_HOST", "mosquitto"))
pub.loop_start()

plc = ModbusTcpClient(os.environ.get("PLC_HOST", "plc"), port=int(os.environ.get("PLC_PORT", "5020")))
plc.connect()

print("=== 게이트웨이: PLC(Modbus) 레지스터 → 의미를 붙여 → MQTT 토픽")
print("  레지스터 4개의 사연:  IR0 = 온도 x10 (℃)   (배율과 단위는 PLC 문서에만 있다)\n")
for k in range(5):
    r = plc.read_input_registers(0, count=1, device_id=1)
    raw = r.registers[0]
    doc = {"sensor": "temp01", "line": "Line1", "value": raw / 10, "unit": "C", "ts": round(time.time(), 1), "source": "modbus:plc/IR0"}
    payload = json.dumps(doc, ensure_ascii=False)
    print(f"[{k + 1}] Modbus 로 읽은 원래 값 {raw}  (응답 레지스터 2 바이트)  →  MQTT 로 {len(payload)} 바이트 발행")
    pub.publish(TOPIC, payload)
    time.sleep(1.0)

time.sleep(0.5)
sub.loop_stop(); pub.loop_stop(); plc.close()
print(f"\n구독자가 받은 메시지: {len(received)} 개")
print("  - 2 바이트짜리 값이 이름·단위·시각이 붙은 JSON 으로 바뀌었다 (크기는 커지지만 '의미'가 생겼다)")
print("  - 위쪽 시스템(대시보드, 클라우드 AI)은 Modbus 주소(IR0)를 몰라도 'factory/line1/temp01' 만 알면 된다")

# 해 보라
#  1) 같은 값이 Modbus 에서는 2 바이트였다. MQTT/JSON 은 몇 바이트인가?  왜 이렇게 늘렸는가?
#  2) 게이트웨이가 꺼지면 위쪽 시스템은 무엇을 알 수 있는가?  (이 코드에는 없다 — MQTT 의 Last Will 을 쓰면?)
#  3) 센서가 1000 개라면 게이트웨이는 어떤 문제를 만나는가?  (폴링 주기, 레지스터 묶음 읽기, 설정 관리)
