# 실습 6 (클라이언트 2) : OPC UA Subscription - 값이 바뀔 때 서버가 알려 준다 (Pub/Sub 과 닮은 방식)
#   사용:  .\run.cmd 06_opcua_subscribe.py
import asyncio
import logging
import time

from asyncua import Client

logging.getLogger("asyncua").setLevel(logging.ERROR)

URL = "opc.tcp://opcua:4840/factory/"
t0 = time.time()


class Handler:
    def datachange_notification(self, node, val, data):
        print(f"  [{time.time() - t0:4.1f}초] 알림: Temperature = {val}", flush=True)


async def main():
    async with Client(URL) as client:
        temp = await client.nodes.objects.get_child(["2:Factory", "2:Line1", "2:Temp01", "2:Temperature"])
        sub = await client.create_subscription(500, Handler())     # 서버가 0.5초마다 변화를 확인해 알려 준다
        await sub.subscribe_data_change(temp)
        print("Temperature 변화를 구독했다. 10초 동안 서버가 보내는 알림을 받는다\n")
        await asyncio.sleep(10)
        await sub.delete()


asyncio.run(main())

# 해 보라
#  1) 06_opcua_client.py 의 Read(물어보기)와 이 Subscription(알려 받기)의 차이는?
#  2) MQTT 의 Subscribe 와 OPC UA 의 Subscription 은 같은 구조일까? 다른 점은? (브로커가 있는가?)
