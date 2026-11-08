# 실습 6 (클라이언트 1) : OPC UA - 주소 공간을 "탐색(Browse)"하고 값을 "읽고(Read)" "쓴다(Write)"
#   사용:  .\run.cmd 06_opcua_client.py
import asyncio
import logging

from asyncua import Client

logging.getLogger("asyncua").setLevel(logging.ERROR)     # 세션 시간 조정 경고를 숨긴다

URL = "opc.tcp://opcua:4840/factory/"


async def browse(node, depth=0):
    for child in await node.get_children():
        name = (await child.read_browse_name()).Name
        cls = await child.read_node_class()
        if cls.name == "Variable":
            value = await child.read_value()
            print(f"{'  ' * depth}- {name} = {value!r}   (변수)")
        else:
            print(f"{'  ' * depth}+ {name}   (객체)")
            await browse(child, depth + 1)


async def main():
    async with Client(URL) as client:
        print(f"연결됨: {URL}\n")
        print("=== 1) Browse : 서버가 가진 것을 트리로 탐색")
        factory = await client.nodes.objects.get_child(["2:Factory"])
        print("+ Factory   (객체)")
        await browse(factory, 1)

        print("\n=== 2) Read : 값 읽기 (클라이언트가 직접 요청)")
        temp = await client.nodes.objects.get_child(["2:Factory", "2:Line1", "2:Temp01", "2:Temperature"])
        for _ in range(3):
            print("  Temperature =", await temp.read_value())
            await asyncio.sleep(1)

        print("\n=== 3) Write : 값 쓰기 (쓰기 가능한 변수만)")
        sp = await client.nodes.objects.get_child(["2:Factory", "2:Line1", "2:Temp01", "2:Setpoint"])
        print("  Setpoint(이전) =", await sp.read_value())
        await sp.write_value(26.5)
        print("  Setpoint(이후) =", await sp.read_value())
        await sp.write_value(25.0)

        print("\n=== 4) 쓰기 불가능한 변수에 쓰면?")
        try:
            await temp.write_value(99.0)
            print("  (써졌다)")
        except Exception as e:
            print("  거부됨:", type(e).__name__)


asyncio.run(main())

# 해 보라
#  1) OPC UA 의 주소 공간은 폴더 구조와 비슷하다. MQTT 의 토픽(factory/line1/temp01/temperature)과 비교해 보라
#  2) Read 는 "클라이언트가 물어보는" 방식이다. 값이 바뀔 때만 알려 받으려면? (06_opcua_subscribe.py)
