# 실습 4 : Tool Calling - AI 는 함수를 "실행"하지 않고 "호출을 요청"한다. 실행은 우리 프로그램이 한다
#   사용:  .\run.cmd 04_tool_calling.py
import llm
import plant_tools

llm.banner()
tools = [d for d in plant_tools.DECLARATIONS if d["name"] == "get_temperature"]   # 도구 한 개만 알려 준다
question = "temp01 센서의 현재 온도를 알려 줘."

print("=== 0) AI 에게 알려 주는 '도구 설명서' (이름, 설명, 인자)")
print(llm.pj(tools[0], 500))

print(f"\n=== 1) 질문을 보낸다:  \"{question}\"")
contents = [llm.user(question)]
r1 = llm.generate(contents, tools)
calls = llm.calls_of(r1["parts"])
print("  AI 의 응답 parts:")
print(llm.pj(r1["parts"], 500))
if not calls:
    raise SystemExit("AI 가 도구 호출을 요청하지 않았다: " + llm.text_of(r1["parts"]))

print("\n=== 2) 우리 프로그램이 도구를 실행한다  (AI 가 한 것이 아니다!)")
results = []
for c in calls:
    out = plant_tools.run(c["name"], c.get("args", {}))
    print(f"  실행: {c['name']}({c.get('args')})  ->  {out}")
    results.append((c["name"], out))

print("\n=== 3) 결과를 AI 에게 돌려주고, 최종 답을 받는다")
contents += [llm.model_content(r1["parts"]), llm.tool_results(results)]        # AI 의 요청 + 우리의 실행 결과를 이력에 붙인다
r2 = llm.generate(contents, tools)
print("  최종 답:", llm.text_of(r2["parts"]))

print("\n=== 이 대화에 실제로 오간 메시지 (contents)")
for i, c in enumerate(contents, 1):
    kind = ", ".join(next(iter(p)) for p in c["parts"])
    print(f"  {i}. role={c['role']:5s}  parts=[{kind}]")
print(f"  ({len(contents)}개의 메시지 + 마지막 답 = 서버 호출 2번)")

# 해 보라
#  1) AI 가 get_temperature 를 "직접" 실행했는가? 누가 plant API 를 호출했는가?
#  2) 도구 설명서(description)를 "아무 말이나"로 바꾸면 AI 가 도구를 제대로 고를까?
#  3) tools 를 빼고 질문하면(tools=None) AI 는 어떻게 답하는가?
