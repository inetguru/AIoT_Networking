# 실습 3 : 스트리밍 - 답이 완성될 때까지 기다리지 않고, 만들어지는 대로 받는다 (SSE)
#   사용:  .\run.cmd 03_streaming.py
import llm

llm.banner()
prompt = "AI Agent가 무엇인지 설명해 줘."
contents = [llm.user(prompt)]

print("=== 1) 일반 호출: 전체 답이 완성된 뒤에 한꺼번에 도착")
r = llm.generate(contents)
print(f"  {r['seconds']:.1f}초 뒤에 전체 도착 → {llm.text_of(r['parts'])[:60]}...\n")

print("=== 2) 스트리밍 호출: 조각이 도착하는 대로 화면에 찍는다")
n, first, last, text = 0, None, 0.0, ""
print("  ", end="", flush=True)
for t, piece, usage in llm.stream(contents):
    first = first if first is not None else t
    last = t
    n += 1
    text += piece
    print(piece, end="", flush=True)
print(f"\n\n  조각 {n}개 · 첫 글자까지 {first:.1f}초 · 전부 도착까지 {last:.1f}초")

print("\n=== 3) 비교")
print(f"  일반 호출은 {r['seconds']:.1f}초 동안 아무것도 안 보이다가 한꺼번에 나타난다.")
print(f"  스트리밍은 {first:.1f}초 만에 첫 글자가 보이기 시작한다 → 같은 답이어도 '체감 지연'이 훨씬 짧다.")

# 해 보라
#  1) llm.py 의 stream() 에서 chunk_size=1 을 지우고(기본값 512바이트) 다시 실행해 보라. 무슨 일이 생기는가?
#     (Net2_Intro 의 SSE 실습에서 겪은 문제와 같다)
#  2) 스트리밍은 HTTP 의 어떤 기능인가? (Net2_Intro 의 Polling/SSE/WebSocket 실습을 떠올려 보라)
