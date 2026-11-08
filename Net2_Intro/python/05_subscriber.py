# 실습 5 (대시보드 역할) : MQTT 로 Subscribe 한다
#   사용:  .\run.cmd 05_subscriber.py                      (factory/# 전체, 20초 동안)
#          .\run.cmd 05_subscriber.py "factory/line1/+/temperature"
#          .\run.cmd 05_subscriber.py "factory/#" --seconds 60
#   토픽 필터:  +  한 단계 와일드카드,   #  나머지 전부
import argparse
import threading

import paho.mqtt.client as mqtt

ap = argparse.ArgumentParser()
ap.add_argument("topic", nargs="?", default="factory/#")
ap.add_argument("--host", default="mosquitto")
ap.add_argument("--seconds", type=float, default=20)
ap.add_argument("--qos", type=int, default=0, choices=[0, 1, 2])
args = ap.parse_args()


def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe(args.topic, qos=args.qos)
    print(f"브로커에 연결되었다. 구독: '{args.topic}' (QoS {args.qos}), {args.seconds:.0f}초 동안 기다린다\n", flush=True)


def on_message(client, userdata, msg):
    tag = " [retained]" if msg.retain else ""
    print(f"  {msg.topic}  (QoS {msg.qos}){tag}  {msg.payload.decode()}", flush=True)


c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dashboard-1")
c.on_connect, c.on_message = on_connect, on_message
c.connect(args.host, 1883, keepalive=30)
threading.Timer(args.seconds, c.disconnect).start()
c.loop_forever()
print("\n구독을 마친다.")

# 해 보라
#  1) 구독하는 창을 두 개 띄우고 05_publisher.py 를 한 번 실행하면 두 창 모두 받는가?
#  2) 토픽 필터를 "factory/line1/+/temperature", "factory/#", "factory/line2/#" 로 바꿔 보라
