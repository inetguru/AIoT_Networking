# 실습 5 : Last Will (유언) - 장치가 갑자기 죽으면 브로커가 대신 "offline" 이라고 알려 준다
#   사용:  .\run.cmd 05_lwt_demo.py
import time

import paho.mqtt.client as mqtt

HOST = "mosquitto"
STATUS = "factory/line1/temp01/status"
t0 = time.time()


def stamp():
    return f"[{time.time() - t0:4.1f}초]"


# 대시보드: 장치 상태를 구독한다
dash = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dash-lwt")
dash.on_connect = lambda c, u, f, rc, p: c.subscribe(STATUS, qos=1)
dash.on_message = lambda c, u, m: print(f"{stamp()} 대시보드가 받음: {m.topic} = {m.payload.decode()!r}  (retained={m.retain})", flush=True)
dash.connect(HOST, 1883)
dash.loop_start()
time.sleep(1)

# 센서: 접속할 때 "내가 갑자기 사라지면 이 메시지를 대신 발행해 달라"고 브로커에 맡긴다
dev = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="temp01-device")
dev.will_set(STATUS, payload="offline", qos=1, retain=True)
dev.connect(HOST, 1883, keepalive=5)
dev.loop_start()
dev.publish(STATUS, "online", qos=1, retain=True).wait_for_publish()
print(f"{stamp()} 센서가 접속하고 'online' 을 발행했다 (유언: 'offline' 을 브로커에 맡겨 둠)", flush=True)
time.sleep(2)

print(f"{stamp()} 센서가 갑자기 죽는다 (DISCONNECT 패킷 없이 연결이 끊김)", flush=True)
dev.loop_stop()
dev.socket().close()                                  # 정상 종료(DISCONNECT)를 하지 않고 소켓만 끊는다

time.sleep(4)
dash.loop_stop()
dash.disconnect()

# 정리: 남은 retained 상태 메시지 삭제
clean = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="lwt-clean")
clean.connect(HOST, 1883)
clean.loop_start()
clean.publish(STATUS, b"", retain=True).wait_for_publish()
clean.loop_stop()
clean.disconnect()

# 해 보라
#  1) 센서는 죽었는데 어떻게 "offline" 메시지가 나왔는가? 누가 발행했는가?
#  2) 폴링 방식이라면 센서가 죽은 것을 어떻게 알아챌 수 있을까?
