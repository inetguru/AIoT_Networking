# 실습 6 (서버) : OPC UA 서버 - 설비의 "주소 공간"을 트리로 공개한다
#   Factory / Line1 / Temp01 / (Temperature, Unit, Status)
#   compose.yaml 의 opcua 서비스로 자동 실행된다. 포트 4840.
import asyncio

from asyncua import Server

ENDPOINT = "opc.tcp://0.0.0.0:4840/factory/"
NAMESPACE = "http://example.com/factory"


async def main():
    server = Server()
    await server.init()
    server.set_endpoint(ENDPOINT)
    server.set_server_name("Factory OPC UA Server")
    idx = await server.register_namespace(NAMESPACE)

    # 주소 공간(Address Space) : 폴더 같은 트리 구조
    factory = await server.nodes.objects.add_object(idx, "Factory")
    line1 = await factory.add_object(idx, "Line1")
    temp01 = await line1.add_object(idx, "Temp01")
    temperature = await temp01.add_variable(idx, "Temperature", 23.5)
    await temp01.add_variable(idx, "Unit", "C")
    status = await temp01.add_variable(idx, "Status", "Running")
    setpoint = await temp01.add_variable(idx, "Setpoint", 25.0)
    await setpoint.set_writable()                       # 클라이언트가 쓸 수 있는 값

    print(f"OPC UA 서버 시작: {ENDPOINT}", flush=True)
    async with server:
        n = 0
        while True:
            await asyncio.sleep(1)
            n += 1
            value = round(23.0 + (n % 6) * 0.5, 1)
            await temperature.write_value(value)         # 값이 바뀌면 구독 중인 클라이언트에게 알림이 간다
            if n % 5 == 0:
                print(f"[서버] Temperature = {value}", flush=True)


asyncio.run(main())
