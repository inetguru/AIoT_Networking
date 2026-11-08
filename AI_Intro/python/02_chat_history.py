# 실습 2 : LLM API 는 기억하지 않는다 (Stateless) - 대화 이력은 "내가" 매번 보낸다
#   사용:  .\run.cmd 02_chat_history.py
import llm

llm.banner()

print("=== 장면 1. 새 문장만 보낸다 (이력 없음)")
r1 = llm.generate([llm.user("내 이름은 철수야.")])
print("  나  : 내 이름은 철수야.\n  AI  :", llm.text_of(r1["parts"]))
r2 = llm.generate([llm.user("내 이름이 뭐야?")])
print("  나  : 내 이름이 뭐야?\n  AI  :", llm.text_of(r2["parts"]))
print("  -> 두 요청은 서로 아무 관계가 없다. 서버는 앞의 대화를 기억하지 않는다.\n")

print("=== 장면 2. 대화 전체를 매번 함께 보낸다 (이력 포함)")
history = []
rows = []
for q in ["내 이름은 철수야.", "나는 부산 공장에서 일해.", "내 이름이 뭐야?", "내가 어디서 일한다고 했지?"]:
    history.append(llm.user(q))
    r = llm.generate(history)
    answer = llm.text_of(r["parts"])
    history.append(llm.model_content(r["parts"]))               # AI 의 답도 이력에 붙인다
    rows.append((q, answer, len(history) - 1, r["usage"].get("promptTokenCount")))
    print(f"  나  : {q}\n  AI  : {answer}")

print("\n=== 요청에 실려 간 이력의 크기")
print(f"  {'번호':>3} {'보낸 메시지 수':>12} {'입력 토큰':>10}   질문")
for i, (q, a, n, tok) in enumerate(rows, 1):
    print(f"  {i:>3} {n:>12} {str(tok):>10}   {q}")
print("\n  -> 대화가 길어질수록 매번 보내는 양(=토큰=비용=지연)이 늘어난다.")

# 해 보라
#  1) 장면 1과 장면 2의 차이는? 기억하는 쪽은 서버인가, 내 프로그램인가?
#  2) 대화가 100번 오가면 마지막 요청에는 메시지가 몇 개 실릴까? 비용 문제를 줄이려면?
#  3) 02_chat_server (Net2_Intro) 의 /stateless 와 같은 구조임을 확인하라
