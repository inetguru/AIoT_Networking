# 실습 5 (센서 역할) : MQTT 로 온도 값을 Publish 한다
#   사용:  .\run.cmd 05_publisher.py                         (1초마다 10번)
#          .\run.cmd 05_publisher.py --qos 1 --count 5
#          .\run.cmd 05_publisher.py --topic factory/line2/temp02/temperature
#   Publisher 는 "누가 받는지" 모른다. 브로커(mosquitto)에게 토픽과 값만 맡긴다.
import argparse
import json
import time

import paho.mqtt.client as mqtt

ap = argparse.ArgumentParser()
ap.add_argument("--host", default="mosquitto")
ap.add_argument("--topic", default="factory/line1/temp01/temperature")
ap.add_argument("--count", type=int, default=10)
ap.add_argument("--interval", type=float, default=1.0)
ap.add_argument("--qos", type=int, default=0, choices=[0, 1, 2])
ap.add_argument("--retain", action="store_true", help="브로커가 마지막 값을 기억하게 한다")
args = ap.parse_args()

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sensor-temp01")
c.connect(args.host, 1883, keepalive=30)
c.loop_start()
print(f"브로커 {args.host}:1883 에 연결. 토픽 '{args.topic}' 로 {args.count}번 발행 (QoS {args.qos}, retain={args.retain})\n")

for i in range(args.count):
    value = round(23.0 + (i % 5) * 0.4, 1)
    payload = json.dumps({"value": value, "unit": "C", "seq": i})
    info = c.publish(args.topic, payload, qos=args.qos, retain=args.retain)
    info.wait_for_publish()
    print(f"  publish #{i}: {payload}")
    time.sleep(args.interval)

c.loop_stop()
c.disconnect()

# 해 보라
#  1) 다른 창에서 05_subscriber.py 를 먼저 실행해 두고 이 파일을 실행해 보라
#  2) --qos 0/1/2 로 바꾸면 무엇이 달라질까? (capture.py mqtt 로 패킷을 비교해 보라)
#  3) 이 코드 어디에도 "받는 쪽의 주소"가 없다. 왜 이것이 가능한가?
