# 실습 5 : Retained 메시지 - 늦게 접속한 구독자도 "마지막 값"을 바로 받는다
#   사용:  .\run.cmd 05_retain_demo.py
import time

import paho.mqtt.client as mqtt

HOST = "mosquitto"
T_LIVE = "factory/demo/temp/live"          # 일반 메시지
T_LAST = "factory/demo/temp/last"          # retained 메시지


def make(cid):
    return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=cid)


# 1) 센서가 값을 두 가지 방식으로 발행하고 떠난다 (구독자는 아직 아무도 없다)
pub = make("demo-sensor")
pub.connect(HOST, 1883)
pub.loop_start()
pub.publish(T_LIVE, "23.5", retain=False).wait_for_publish()
pub.publish(T_LAST, "23.5", retain=True).wait_for_publish()
pub.loop_stop()
pub.disconnect()
print("1) 센서가 두 토픽에 23.5 를 발행하고 떠났다")
print(f"   - {T_LIVE}  : 일반 (retain=False)")
print(f"   - {T_LAST}  : retained (retain=True)")
time.sleep(1)

# 2) 그 뒤에 구독자가 접속한다
got = []
sub = make("demo-late-subscriber")
sub.on_connect = lambda c, u, f, rc, p: c.subscribe("factory/demo/temp/#")
sub.on_message = lambda c, u, m: got.append((m.topic, m.payload.decode(), m.retain))
sub.connect(HOST, 1883)
sub.loop_start()
print("\n2) 한참 뒤에 구독자가 접속해 'factory/demo/temp/#' 를 구독했다 (2초 기다림)")
time.sleep(2)
sub.loop_stop()
sub.disconnect()

for topic, payload, retained in got:
    print(f"   받음: {topic} = {payload}  (retained={retained})")
if not any(t == T_LIVE for t, _, _ in got):
    print(f"   {T_LIVE} 는 받지 못했다 (지나간 일반 메시지는 사라진다)")

# 3) 정리: 남아 있는 retained 메시지를 지운다 (빈 메시지를 retain 으로 발행)
clean = make("demo-clean")
clean.connect(HOST, 1883)
clean.loop_start()
clean.publish(T_LAST, b"", retain=True).wait_for_publish()
clean.loop_stop()
clean.disconnect()

# 해 보라
#  1) 센서가 5분에 한 번만 값을 보내는데 대시보드를 방금 켰다면 retained 가 왜 유용할까?
#  2) retained 로 "장치 상태(online/offline)"를 발행하면 어떤 장점이 있을까? (05_lwt_demo.py)
