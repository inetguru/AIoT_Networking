# 실습 1 : LLM 도 결국 "HTTP API" 다 - 한 번 묻고 한 번 답을 받는다
#   사용:  .\run.cmd 01_hello_llm.py
import llm

llm.banner()
prompt = "HTTP API란 무엇인지 한 문장으로 설명해 줘."
contents = [llm.user(prompt)]

print("=== 1) 서버로 보내는 요청 본문 (POST .../models/<모델>:generateContent)")
print(llm.pj(llm.body_of(contents)))

r = llm.generate(contents)

print("\n=== 2) 서버가 돌려준 응답의 parts")
print(llm.pj(r["parts"]))

print("\n=== 3) 결과")
print("질문 :", prompt)
print("답변 :", llm.text_of(r["parts"]))
u = r["usage"]
print(f"토큰 : 입력 {u.get('promptTokenCount')}, 출력 {u.get('candidatesTokenCount')}, 합계 {u.get('totalTokenCount')}")
print(f"시간 : {r['seconds']:.1f}초")
if (u.get('totalTokenCount') or 0) > (u.get('promptTokenCount') or 0) + (u.get('candidatesTokenCount') or 0):
    print("       (합계가 입력+출력보다 큰 것은 모델이 답을 만들기 전에 '생각'하는 데 쓴 토큰도 세기 때문이다)")

# 해 보라
#  1) 응답 JSON 의 구조를 보라: candidates -> content -> parts -> text.  주제 1 의 API 응답과 닮았는가?
#  2) prompt 를 바꿔서 다시 실행해 보라. 입력/출력 토큰은 무엇에 따라 늘어나는가?
#  3) 요청에 "키가 들어 있는가"? 키는 어디에 있는가? (llm.py 의 _headers 를 보라)
