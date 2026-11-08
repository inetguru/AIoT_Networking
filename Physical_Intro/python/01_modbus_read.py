# 실습 1 : Modbus TCP 로 PLC 의 센서 값을 읽고 쓴다
#   사용:  .\run.cmd 01_modbus_read.py
import os

from pymodbus.client import ModbusTcpClient

c = ModbusTcpClient(os.environ.get("PLC_HOST", "plc"), port=int(os.environ.get("PLC_PORT", "5020")))
c.connect()
UNIT = 1                                            # 장치 번호 (Modbus 에서 "누구에게 묻는가")

print("=== 1) 읽기 : 네 종류의 '데이터 영역'과 기능 코드(Function Code)")
r = c.read_input_registers(0, count=2, device_id=UNIT)
print(f"  FC04 Input Register    주소 0~1  -> 원래 값 {r.registers}   (센서: 온도 x10)")
print(f"       온도1 = {r.registers[0] / 10:.1f} ℃   온도2 = {r.registers[1] / 10:.1f} ℃   ← 정수를 10으로 나눠 사람이 읽는 값으로")
r = c.read_holding_registers(0, count=1, device_id=UNIT)
print(f"  FC03 Holding Register  주소 0    -> 원래 값 {r.registers}   (설정 온도 x10 = {r.registers[0] / 10:.1f} ℃)")
r = c.read_coils(0, count=2, device_id=UNIT)
print(f"  FC01 Coil              주소 0~1  -> {r.bits[:2]}   (히터, 긴급 냉각 : 켜짐/꺼짐 비트)")
r = c.read_discrete_inputs(0, count=1, device_id=UNIT)
print(f"  FC02 Discrete Input    주소 0    -> {r.bits[:1]}   (과열 경보 : 읽기 전용 비트)")

print("\n=== 2) 쓰기 : 설정 온도를 27.0 ℃ 로 바꾼다 (FC06, 레지스터 하나 쓰기)")
c.write_register(0, 270, device_id=UNIT)
r = c.read_holding_registers(0, count=1, device_id=UNIT)
print(f"  다시 읽어 보면 -> {r.registers[0] / 10:.1f} ℃")
c.write_register(0, 250, device_id=UNIT)             # 원래대로
print("  (원래 값 25.0 ℃ 로 되돌렸다)")

print("\n=== 3) 없는 주소를 읽으면?")
r = c.read_input_registers(9999, count=1, device_id=UNIT)
print(f"  결과: {r}")
print("  -> 오류도 약속된 '예외 코드'로 돌아온다 (Modbus 예외 코드 02 = 잘못된 주소)")
c.close()

# 해 보라
#  1) 온도가 왜 235 같은 정수로 오는가?  (레지스터 하나 = 16비트 정수.  소수는 약속한 배율로 표현한다)
#  2) Input Register 와 Holding Register 의 차이는?  Input 에 쓰기를 시도하면 어떻게 되는가?
#  3) 이 값에는 "단위"도 "이름"도 없다.  '주소 0 이 온도다'라는 것을 어디에서 알 수 있는가?
