# 실습 1 (서버) : 같은 일을 "서로 다른 방식"으로 처리하는 세 가지 서버
#   blocking : 한 번에 한 손님만 받는다 (앞 손님이 끝날 때까지 뒤 손님은 기다린다)
#   threaded : 손님마다 직원을 한 명씩 붙인다 (스레드)
#   async    : 직원 한 명이 "기다리는 동안" 다른 손님을 돌본다 (Non-Blocking, 이벤트 루프)
#   compose.yaml 의 srv-blocking / srv-threaded / srv-async 서비스로 자동 실행된다.
#
# 손님의 요청은 두 종류다.
#   IO  : 센서의 응답을 1초 "기다리는" 일 (CPU는 놀고 있다)
#   CPU : 0.5초 동안 "계산하는" 일 (CPU가 계속 일한다)
import asyncio
import socket
import sys
import threading
import time

MODE, PORT = sys.argv[1], int(sys.argv[2])


def work(n):
    s = 0
    for i in range(n):
        s += i * i
    return s


def calibrate(target=0.5):
    """이 컴퓨터에서 계산 작업이 약 0.5초 걸리도록 반복 횟수를 맞춘다."""
    n = 200_000
    while True:
        t0 = time.perf_counter()
        work(n)
        dt = time.perf_counter() - t0
        if dt >= 0.1:
            return int(n * target / dt)
        n *= 2


N = calibrate()
REPLY = b"temp=23.5\n"


def job(kind):
    if kind == "IO":
        time.sleep(1.0)            # 응답을 "기다린다" (Blocking)
    else:
        work(N)                    # 실제로 "계산한다"
    return REPLY


def log(kind, t0):
    print(f"[{MODE}] {kind} 요청 처리 완료 ({time.perf_counter() - t0:.2f}초)", flush=True)


# ---------------------------------------------------------------- blocking
def serve_blocking():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen(128)
    print(f"[blocking] 포트 {PORT} : 한 번에 한 연결씩 처리한다 (계산 1회 = {N:,}번 반복)", flush=True)
    while True:
        conn, _ = srv.accept()
        t0 = time.perf_counter()
        kind = conn.makefile().readline().strip()
        conn.sendall(job(kind))
        conn.close()
        log(kind, t0)


# ---------------------------------------------------------------- threaded
def handle_thread(conn):
    t0 = time.perf_counter()
    kind = conn.makefile().readline().strip()
    conn.sendall(job(kind))
    conn.close()
    log(kind, t0)


def serve_threaded():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen(128)
    print(f"[threaded] 포트 {PORT} : 연결마다 스레드를 만든다 (계산 1회 = {N:,}번 반복)", flush=True)
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=handle_thread, args=(conn,), daemon=True).start()


# ---------------------------------------------------------------- async
async def handle_async(reader, writer):
    t0 = time.perf_counter()
    kind = (await reader.readline()).decode().strip()
    if kind == "IO":
        await asyncio.sleep(1.0)   # 기다리는 동안 이벤트 루프는 다른 연결을 처리한다 (Non-Blocking)
    else:
        work(N)                    # 계산은 이벤트 루프를 붙잡는다 (다른 연결이 멈춘다)
    writer.write(REPLY)
    await writer.drain()
    writer.close()
    log(kind, t0)


async def serve_async():
    server = await asyncio.start_server(handle_async, "0.0.0.0", PORT, backlog=128)
    print(f"[async] 포트 {PORT} : 하나의 이벤트 루프로 모든 연결을 처리한다 (계산 1회 = {N:,}번 반복)", flush=True)
    async with server:
        await server.serve_forever()


if MODE == "blocking":
    serve_blocking()
elif MODE == "threaded":
    serve_threaded()
elif MODE == "async":
    asyncio.run(serve_async())
else:
    sys.exit("사용법: 01_servers.py blocking|threaded|async PORT")
