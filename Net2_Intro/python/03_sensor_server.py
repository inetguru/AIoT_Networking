# 실습 3 (서버) : 센서 값이 2초마다 바뀐다. 이 변화를 클라이언트에게 알리는 세 가지 방법
#   HTTP 포트 8080 :  GET /temp    -> 지금 값 (Polling : 클라이언트가 계속 물어본다)
#                     GET /events  -> SSE (Server-Sent Events : 서버가 HTTP 연결을 열어 둔 채 밀어 준다)
#   WebSocket 포트 8765 : 양방향 연결을 유지하며 서버가 값을 밀어 준다
#   compose.yaml 의 sensor 서비스로 자동 실행된다.
import asyncio
import json
import time

from websockets.asyncio.server import broadcast, serve

state = {"value": 23.5, "version": 0, "t": time.time()}     # t = 값이 바뀐 시각 (지연 측정용)
sse_queues = set()
ws_conns = set()


async def updater():
    while True:
        await asyncio.sleep(2)
        state["version"] += 1
        state["value"] = round(23.5 + (state["version"] % 7) * 0.3, 1)
        state["t"] = time.time()
        msg = json.dumps(state)
        for q in list(sse_queues):
            q.put_nowait(msg)
        broadcast(ws_conns, msg)
        print(f"[변화] version={state['version']} value={state['value']}  (SSE {len(sse_queues)}명, WebSocket {len(ws_conns)}명에게 전달)", flush=True)


async def http_handler(reader, writer):
    request_line = (await reader.readline()).decode()
    while (await reader.readline()).strip():                 # 헤더는 읽고 버린다
        pass
    path = request_line.split(" ")[1] if " " in request_line else "/"
    if path == "/temp":
        body = json.dumps(state).encode()
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n"
                     + f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        await writer.drain()
    elif path == "/events":
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nCache-Control: no-cache\r\n"
                     b"Connection: keep-alive\r\n\r\n")
        q = asyncio.Queue()
        sse_queues.add(q)
        try:
            writer.write(f"data: {json.dumps(state)}\n\n".encode())   # 접속하자마자 현재 값
            await writer.drain()
            while True:
                writer.write(f"data: {await q.get()}\n\n".encode())  # 변화가 있을 때만 전송
                await writer.drain()
        except (ConnectionError, asyncio.CancelledError):
            pass
        finally:
            sse_queues.discard(q)
    else:
        writer.write(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
    writer.close()


async def ws_handler(ws):
    ws_conns.add(ws)
    try:
        await ws.send(json.dumps(state))
        await ws.wait_closed()
    finally:
        ws_conns.discard(ws)


async def main():
    http = await asyncio.start_server(http_handler, "0.0.0.0", 8080)
    print("센서 서버 시작: HTTP 8080 (/temp, /events), WebSocket 8765", flush=True)
    async with serve(ws_handler, "0.0.0.0", 8765), http:
        await updater()


asyncio.run(main())
