# 실습 5 : Agent = LLM + 도구 + 반복.  그리고 "무엇을 허용할 것인가"
#   사용:  .\run.cmd 05_agent_loop.py                               (세 가지 질문을 차례로)
#          .\run.cmd 05_agent_loop.py "temp01과 temp02 중 어디가 더 따뜻해?"
#          .\run.cmd 05_agent_loop.py "temp01 설정 온도를 28도로 바꿔 줘" --allow-write
import sys

import llm
import plant_tools

MAX_STEPS = 6                       # 무한 반복 방지


def run_agent(question, allow_write=False):
    print(f"\n{'=' * 60}\n질문: {question}   (쓰기 도구 허용: {allow_write})\n{'=' * 60}")
    contents = [llm.user(question)]
    for step in range(1, MAX_STEPS + 1):
        r = llm.generate(contents, plant_tools.DECLARATIONS,
                         system="너는 공장 설비 보조 AI다. 센서 값은 반드시 도구로 확인하고 한국어로 짧게 답한다.")
        contents.append(llm.model_content(r["parts"]))
        calls = llm.calls_of(r["parts"])
        if not calls:                                           # 도구 요청이 없으면 끝: 최종 답
            print(f"[{step}] AI 최종 답: {llm.text_of(r['parts'])}")
            return
        results = []
        for c in calls:
            name, args = c["name"], c.get("args", {})
            if name in plant_tools.WRITE_TOOLS and not allow_write:        # ★ 권한 통제: 쓰기는 허락된 경우에만
                out = {"error": f"'{name}' 은(는) 설비를 바꾸는 도구라서 허용되지 않았다 (사람의 승인이 필요하다)"}
                print(f"[{step}] AI 요청: {name}({args})  ->  ⛔ 차단: {out['error']}")
            else:
                out = plant_tools.run(name, args)
                print(f"[{step}] AI 요청: {name}({args})  ->  실행 결과 {out}")
            results.append((name, out))
        contents.append(llm.tool_results(results))
    print(f"[!] {MAX_STEPS}번 반복해도 끝나지 않아 중단했다")


llm.banner()
args = [a for a in sys.argv[1:] if not a.startswith("--")]
allow = "--allow-write" in sys.argv
if args:
    run_agent(args[0], allow)
else:
    run_agent("어떤 센서가 있는지 알려 줘.")
    run_agent("temp01과 temp02 중 어디가 더 따뜻해?")
    run_agent("temp01 설정 온도를 30도로 바꿔 줘.")               # 쓰기 요청 -> 기본은 차단된다
    print("\n※ 쓰기 요청이 차단되었다. 허용해 보려면:  .\\run.cmd 05_agent_loop.py \"temp01 설정 온도를 30도로 바꿔 줘\" --allow-write")

# 해 보라
#  1) 두 번째 질문에서 AI 는 도구를 몇 번 요청했는가? 한 번에 여러 개를 요청했는가?
#  2) 세 번째 질문의 쓰기 요청이 왜 차단되었는가? 차단 사유를 받은 AI 는 어떻게 답했는가?
#  3) --allow-write 로 실행한 뒤 docker compose logs plant 를 보라. 설비 값이 바뀌었는가?
#  4) 만약 AI 가 잘못 판단해 위험한 값을 요청한다면, 막을 수 있는 곳은 어디일까? (AI 안? 우리 프로그램?)
