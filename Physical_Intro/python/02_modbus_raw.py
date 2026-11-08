# 실습 2 : Modbus TCP 메시지를 "손으로" 만들어 보낸다 - 12 바이트면 충분하다
#   사용:  .\run.cmd 02_modbus_raw.py
import os
import socket
import struct

HOST, PORT = os.environ.get("PLC_HOST", "plc"), int(os.environ.get("PLC_PORT", "5020"))


def hexs(b):
    return " ".join(f"{x:02X}" for x in b)


def request(tid, unit, fc, addr, count):
    pdu = struct.pack(">BHH", fc, addr, count)                       # 기능 코드, 시작 주소, 개수
    mbap = struct.pack(">HHHB", tid, 0, len(pdu) + 1, unit)          # 전송 ID, 프로토콜(0), 길이, 장치 번호
    return mbap + pdu


s = socket.create_connection((HOST, PORT))

print("=== 1) 요청: 'Input Register 0번부터 2개를 읽어 줘' (FC04)")
req = request(tid=1, unit=1, fc=4, addr=0, count=2)
print(f"  보낸 바이트 ({len(req)} 바이트): {hexs(req)}")
print("   00 01        전송 ID (요청과 응답을 짝짓는 번호)")
print("   00 00        프로토콜 ID (항상 0 = Modbus)")
print("   00 06        이 뒤에 오는 바이트 수 (6)")
print("   01           장치 번호 (Unit ID)")
print("   04           기능 코드 (04 = Input Register 읽기)")
print("   00 00        시작 주소 0")
print("   00 02        개수 2")
s.sendall(req)

resp = s.recv(256)
print(f"\n=== 2) 응답 ({len(resp)} 바이트): {hexs(resp)}")
tid, proto, length, unit, fc, nbytes = struct.unpack(">HHHBBB", resp[:9])
vals = struct.unpack(f">{nbytes // 2}H", resp[9:9 + nbytes])
print(f"   전송 ID={tid}  길이={length}  장치={unit}  기능 코드={fc:02X}  데이터 {nbytes} 바이트")
print(f"   레지스터 값 = {list(vals)}  ->  온도1 {vals[0] / 10:.1f} ℃, 온도2 {vals[1] / 10:.1f} ℃")

print("\n=== 3) 잘못된 요청: 없는 주소 (오류는 기능 코드에 0x80 을 더해 알린다)")
bad = request(tid=2, unit=1, fc=4, addr=9999, count=1)
print(f"  보낸 바이트: {hexs(bad)}")
s.sendall(bad)
resp = s.recv(256)
print(f"  응답: {hexs(resp)}   -> 기능 코드 {resp[7]:02X} = 04 + 80 (오류),  예외 코드 {resp[8]:02X} (02 = 잘못된 데이터 주소)")

print("\n=== 4) 코일 쓰기 (FC05): 히터를 켠다 -> 값은 FF00 = ON, 0000 = OFF")
w = struct.pack(">HHHBBHH", 3, 0, 6, 1, 5, 0, 0xFF00)
print(f"  보낸 바이트: {hexs(w)}")
s.sendall(w)
print(f"  응답: {hexs(s.recv(256))}   (쓴 내용을 그대로 되돌려 확인해 준다)")
s.sendall(struct.pack(">HHHBBHH", 4, 0, 6, 1, 5, 0, 0x0000))        # 히터 끄기
s.recv(256)
s.close()

print(f"\n요약: 요청 {len(req)} 바이트 + 응답 13 바이트로 온도 두 개가 오갔다.  JSON 이라면?")
print('  {"temp1": 23.5, "temp2": 22.0}  = 31 바이트 + 이름, 단위, HTTP 헤더 ...  <- Modbus 는 "의미"를 보내지 않고 "값"만 보낸다')

# 해 보라
#  1) 위 바이트열을 .\run.cmd capture.py modbus 로 캡처한 pcap 의 Modbus 패킷(Wireshark 필터: mbtcp)과 비교해 보라
#  2) 요청의 '길이' 필드(00 06)는 어떤 바이트들의 개수인가?
#  3) 보안(인증, 암호화)은 이 메시지의 어디에 있는가?  -> 없다.  그래서 Modbus TCP 는 폐쇄된 설비 네트워크 안에서 쓴다
