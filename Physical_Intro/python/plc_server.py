# 가상 PLC (Modbus TCP 서버) - "공장 온도 센서 한 대"가 PLC의 레지스터에 들어 있다
#   주소는 0부터 (Modbus의 '프로토콜 주소').  값은 정수 16비트: 온도 23.5 ℃ → 235 (x10)
#     Input Register   (FC04, 읽기 전용) : 0 = 온도1(x10)   1 = 온도2(x10)
#     Holding Register (FC03/06/16, 읽기·쓰기) : 0 = 설정 온도(x10)   10 = 이상 발생 시험(1이면 온도 급상승)
#     Coil             (FC01/05, 비트 읽기·쓰기) : 0 = 히터   1 = 긴급 냉각
#     Discrete Input   (FC02, 비트 읽기 전용) : 0 = 과열 경보(30 ℃ 초과)
import asyncio
import math
import time

from pymodbus.server import ModbusTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice

N = 32


def bits():
    return [SimData(address=0, count=N, values=False, datatype=DataType.BITS)]


def regs(first=0):
    return [SimData(address=0, count=N, values=0, datatype=DataType.REGISTERS)]


# 장치 번호 1.  블록 순서: (코일, 이산 입력, 홀딩 레지스터, 입력 레지스터)  - pymodbus 3.16 의 SimDevice 방식
device = SimDevice(id=1, simdata=(bits(), bits(), regs(), regs()))
co = di = hr = ir = server = None                  # 서버는 이벤트 루프 안에서 만든다 (main 참고)


async def simulate():
    t_prev = time.time()
    temp = 23.5
    fault_logged = cool_logged = False
    while True:
        await asyncio.sleep(0.05)
        now = time.time(); dt = now - t_prev; t_prev = now
        setpoint = hr[0] / 10
        normal = setpoint - 1.5 + 0.4 * math.sin(now / 5)
        fault = hr[10] == 1
        cooling = co[1] == 1
        if cooling:
            temp += (normal - temp) * min(1.0, 2.5 * dt)             # 긴급 냉각: 빠르게 정상값으로
            if not cool_logged:
                print(f"★ 긴급 냉각 명령 수신 (온도 {temp:.1f} ℃)", flush=True); cool_logged = True
            if abs(temp - normal) < 0.5:                             # 식으면 이상 상태와 냉각을 끝낸다
                hr[10] = 0; co[1] = 0
                print("★ 온도가 정상으로 돌아왔다 (이상 상태 해제)", flush=True)
                fault_logged = cool_logged = False
        elif fault:
            temp += 3.0 * dt                                         # 이상: 초당 3 ℃ 상승
            if not fault_logged:
                print(f"★ 이상 발생: 온도가 올라가기 시작한다 (현재 {temp:.1f} ℃)", flush=True); fault_logged = True
        else:
            temp += (normal - temp) * min(1.0, 2.0 * dt)
        ir[0] = int(round(temp * 10)); ir[1] = int(round((temp - 1.5 + 0.2 * math.sin(now / 3)) * 10))
        di[0] = 1 if temp > 30 else 0


async def main():
    global co, di, hr, ir, server
    server = ModbusTcpServer(context=device, address=("0.0.0.0", 5020))
    _blk = server.context.devices[1].block      # 'c' 코일, 'd' 이산 입력, 'h' 홀딩, 'i' 입력 레지스터
    co, di, hr, ir = (_blk[k][2] for k in "cdhi")    # 각 블록의 값 목록 (서버 안에서 직접 읽고 쓴다)
    hr[0] = 250                                   # 설정 온도 25.0
    asyncio.create_task(simulate())
    print("가상 PLC (Modbus TCP) 시작: 0.0.0.0:5020, 장치 번호(unit id) 1", flush=True)
    await server.serve_forever()


asyncio.run(main())
