# 실습 5 : 같은 이상 상황, 판단하는 곳이 다르면? - 엣지(System 1) vs 클라우드(System 2)
#   PLC 에 "이상"을 일으킨다 (온도가 초당 3 ℃ 씩 오른다).  10 Hz 로 온도를 읽다가 이상을 알아채면 '긴급 냉각' 코일을 켠다.
#     edge  : 현장 컴퓨터가 직접 판단한다 (기울기 규칙, 수 ms)
#     cloud : 매번 값을 클라우드 AI 로 보내 판단을 받는다 (왕복 지연은 시뮬레이션, 기본 400 ms)
#   사용:  .\run.cmd 05_edge_vs_cloud.py            (둘 다 실행해서 비교)
#          .\run.cmd 05_edge_vs_cloud.py edge       (하나만)
#   지연 바꾸기:  $env:CLOUD_DELAY_MS=1500; .\run.cmd 05_edge_vs_cloud.py cloud     (PowerShell)
import json
import os
import sys
import time

import requests
from pymodbus.client import ModbusTcpClient

PLC = (os.environ.get("PLC_HOST", "plc"), int(os.environ.get("PLC_PORT", "5020")))
CLOUD = os.environ.get("CLOUD_URL", "http://cloud:8400") + "/decide"
HZ = 10
UNIT = 1


def read_temp(c):
    return c.read_input_registers(0, count=1, device_id=UNIT).registers[0] / 10


def reset(c):
    c.write_coil(1, False, device_id=UNIT)
    c.write_register(10, 0, device_id=UNIT)
    for _ in range(60):                                      # 정상 온도로 돌아올 때까지 기다린다
        if read_temp(c) < 25.5:
            return
        c.write_coil(1, True, device_id=UNIT)
        time.sleep(0.2)
    c.write_coil(1, False, device_id=UNIT)


NORMAL_SECONDS = 5


def run(mode):
    c = ModbusTcpClient(PLC[0], port=PLC[1])
    c.connect()
    reset(c)
    time.sleep(1.0)
    hist, uplink, sent = [], 0, 0
    print(f"\n=== [{mode}] {NORMAL_SECONDS} 초 동안 평소 감시 → 이상 발생 ({HZ} Hz 로 온도를 읽는다)")
    t_start = time.time()
    t_fault = None
    action_at = None
    while True:
        t0 = time.time()
        if t_fault is None and t0 - t_start >= NORMAL_SECONDS:
            t_fault = time.time()
            c.write_register(10, 1, device_id=UNIT)           # 이상 시작: 온도가 오르기 시작한다
            print("  ★ 이상 발생! (온도가 초당 3 ℃ 씩 오른다)")
        if t_fault is not None and t0 - t_fault > 15:
            break
        temp = read_temp(c)
        hist.append(temp)
        if mode == "edge":
            rising = len(hist) >= 3 and hist[-1] - hist[-3] > 0.6          # 0.2초 동안 0.6 ℃ 이상 상승
            decide = temp > 27.0 or rising
        else:
            body = json.dumps({"temp": temp, "history": hist[-5:]}).encode()
            uplink += len(body); sent += 1                                    # 값 하나하나를 클라우드로 올린다
            decide = requests.post(CLOUD, data=body, timeout=10).json()["action"] == "cool"
        if decide and t_fault is not None:
            c.write_coil(1, True, device_id=UNIT)            # 긴급 냉각
            action_at = time.time()
            print(f"  → 판단! 이상 시작 후 {action_at - t_fault:.2f} 초,  명령 시점의 온도 {temp:.1f} ℃  →  긴급 냉각 명령")
            break
        time.sleep(max(0.0, 1 / HZ - (time.time() - t0)))
    peak = max(hist[-30:])
    for _ in range(8):                                       # 명령이 닿은 뒤에도 온도가 더 오르는지 관찰한다
        time.sleep(0.1)
        peak = max(peak, read_temp(c))
    if mode == "edge":                                       # 엣지는 '사건' 한 건만 위로 알린다 (시간을 재지 않는다)
        body = json.dumps({"event": "overheat", "line": "Line1", "peak": round(peak, 1)}).encode()
        uplink += len(body); sent += 1
        requests.post(CLOUD, data=body, timeout=10)
    reset(c)
    c.close()
    return {"mode": mode, "react": (action_at - t_fault) if action_at else None, "peak": peak, "sent": sent, "uplink": uplink, "hz": len(hist) / (time.time() - t_start)}


modes = [sys.argv[1]] if len(sys.argv) > 1 else ["edge", "cloud"]
res = [run(m) for m in modes]

print("\n=== 비교 (같은 이상, 같은 규칙, 판단하는 위치만 다르다)")
print(f"  {'':8s} {'반응 시간':>10s} {'최고 온도':>10s} {'실제 읽기':>10s}   위로 보낸 것 (본문만)")
for r in res:
    react = f"{r['react']:.2f} 초" if r["react"] else "못 알아챔"
    print(f"  {r['mode']:8s} {react:>10s} {r['peak']:>8.1f}℃ {r['hz']:>7.1f} Hz   {r['sent']:>3d} 건 / {r['uplink']:>5d} 바이트")
cl = next((r for r in res if r["mode"] == "cloud"), None)
if cl:
    per = cl["uplink"] / max(1, cl["sent"])
    print(f"\n  센서 1000 개가 {HZ} Hz 로 값을 올린다면:  약 {per * HZ * 1000 / 1024:,.0f} KB/초  (HTTP 헤더 제외)  ← 클라우드 판단 방식")
    print("  엣지 판단 방식은 평소에는 거의 0, 이상이 있을 때만 '사건' 한 건씩.")
    print(f"  또 하나: 클라우드 방식은 응답을 기다리느라 '실제 읽기' 가 {HZ} Hz 가 되지 못했다 ({cl['hz']:.1f} Hz) — 그만큼 이상을 늦게 알아챈다.")
print(f"\n  ※ 클라우드 지연은 시뮬레이션이다 (CLOUD_DELAY_MS = {os.environ.get('CLOUD_DELAY_MS', '400')} ms).  실제로는 수십 ms ~ 수 초.")
print("  ※ 온도가 초당 3 ℃ 오르므로, 반응이 0.5 초 늦으면 1.5 ℃ 더 오른 채로 대응한다.")

# 해 보라
#  1) 어느 쪽의 최고 온도가 더 높은가?  차이는 무엇 때문인가?
#  2) CLOUD_DELAY_MS 를 2000 으로 올려 cloud 를 다시 실행해 보라.  네트워크가 끊기면?
#  3) 클라우드에 모든 값을 올릴 필요가 있었는가?  (위로 보낸 데이터 열) → 엣지에서 걸러 '사건'만 올리는 이유
#  4) 그렇다면 클라우드 AI 는 어떤 일에 쓰는가?  (오래 걸려도 되는 일: 원인 분석, 보고서, 예측 정비 — System 2)
