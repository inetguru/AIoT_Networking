# 실습 3-1 : CAN 의 "중재(Arbitration)" - 여럿이 동시에 말하면 누가 이기는가?
#   CAN 은 모두가 한 쌍의 전선을 공유한다. 0(우성, dominant)이 1(열성, recessive)을 이긴다 (선이 AND 로 동작).
#   각 노드는 자기 ID 를 한 비트씩 보내면서 선의 값을 같이 "듣는다". 내가 1 을 보냈는데 선이 0 이면 -> 더 높은 우선순위가 있다 -> 양보
#   사용:  .\run.cmd 03_can_arbitration.py
nodes = {"브레이크 ECU": 0x080, "온도 센서 ECU": 0x100, "진단 도구": 0x7E0}   # ID 가 작을수록 우선순위가 높다 (11비트)

print("노드별 ID (11비트):")
for name, i in nodes.items():
    print(f"  {name:10s} 0x{i:03X} = {i:011b}")

alive = dict(nodes)
print("\n비트 단위 중재 (왼쪽 비트부터):")
print("  비트  " + "  ".join(f"{n:>10s}" for n in nodes) + "   선의 값")
for bit in range(10, -1, -1):
    sent = {n: (i >> bit) & 1 for n, i in alive.items()}
    bus = min(sent.values())                         # 0 이 이긴다 (wired-AND)
    row = []
    for n in nodes:
        row.append(f"{sent[n]:>10d}" if n in sent else f"{'(양보)':>9s}")
    print(f"  {11 - bit:>2d}   " + "  ".join(row) + f"      {bus}")
    for n in [n for n, v in sent.items() if v != bus]:
        print(f"        → {n} : 내가 1 을 보냈는데 선은 0 → 더 중요한 메시지가 있다 → 양보")
        del alive[n]
winner = next(iter(alive))
print(f"\n승자: {winner} (0x{alive[winner]:03X}).  진 노드는 이 프레임이 끝난 뒤 자동으로 다시 시도한다.")
print("충돌로 데이터가 깨지지 않는다: 중재는 비트를 보내는 도중에 끝나므로 승자의 메시지는 손상 없이 전달된다.")

# 해 보라
#  1) nodes 의 ID 를 바꿔 보라. 같은 ID 를 두 노드가 쓰면?  (CAN 에서 ID 는 '누가'가 아니라 '무슨 메시지인가'다)
#  2) 이더넷(CSMA/CD)의 충돌 처리와 비교하면 어떤 점이 다른가?  CAN 은 지연을 예측할 수 있는가?
