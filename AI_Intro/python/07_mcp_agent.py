# 실습 7 : MCP + LLM = 도구를 "발견"해서 쓰는 Agent
#   05번 실습은 도구 목록(plant_tools.py)을 코드에 직접 적었다. 여기서는 MCP 서버에게 물어 도구를 알아낸다.
#   사용:  .\run.cmd 07_mcp_agent.py
#          .\run.cmd 07_mcp_agent.py "temp02 센서의 온도를 알려 줘"
import asyncio
import json
import sys

import mcp
from mcp.client.stdio import StdioServerParameters

import llm

WRITE_TOOLS = {"set_setpoint"}


def to_declaration(tool):
    """MCP 도구 설명(JSON Schema) -> LLM 이 받는 함수 선언. LLM 이 모르는 항목(title 등)은 뺀다."""
    def clean(schema):
        keep = {k: v for k, v in schema.items() if k in ("type", "description", "properties", "required", "items", "enum")}
        if "properties" in keep:
            keep["properties"] = {k: clean(v) for k, v in keep["properties"].items()}
        return keep
    return {"name": tool.name, "description": tool.description or "", "parameters": clean(tool.input_schema or {"type": "object"})}


async def main(question):
    server = StdioServerParameters(command=sys.executable, args=["-u", "06_mcp_server.py"])
    async with mcp.Client(server) as client:
        tools = (await client.list_tools()).tools
        decls = [to_declaration(t) for t in tools]
        print("MCP 서버에서 발견한 도구:", [d["name"] for d in decls], "\n")

        contents = [llm.user(question)]
        print(f"질문: {question}")
        for step in range(1, 7):
            r = llm.generate(contents, decls, system="너는 공장 설비 보조 AI다. 센서 값은 반드시 도구로 확인하고 한국어로 짧게 답한다.")
            contents.append(llm.model_content(r["parts"]))
            calls = llm.calls_of(r["parts"])
            if not calls:
                print(f"[{step}] AI 최종 답: {llm.text_of(r['parts'])}")
                return
            results = []
            for c in calls:
                if c["name"] in WRITE_TOOLS:                               # 쓰기 도구는 사람의 승인 없이는 실행하지 않는다
                    out = {"error": f"'{c['name']}' 은(는) 설비를 바꾸는 도구라서 허용되지 않았다"}
                    print(f"[{step}] AI 요청: {c['name']}({c.get('args')}) -> ⛔ 차단")
                else:
                    res = await client.call_tool(c["name"], c.get("args", {}))      # MCP 로 도구 호출
                    out = res.structured_content or json.loads(res.content[0].text)
                    print(f"[{step}] AI 요청: {c['name']}({c.get('args')}) -> MCP 호출 결과 {out}")
                results.append((c["name"], out))
            contents.append(llm.tool_results(results))


llm.banner()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "temp01과 temp02 중 어디가 더 따뜻해?"))

# 해 보라
#  1) 05번(plant_tools.py 에 도구를 직접 적음)과 이 파일의 차이는? 도구를 추가할 때 어느 쪽 코드를 고쳐야 하는가?
#  2) 같은 MCP 서버(06_mcp_server.py)를 다른 AI 앱(다른 LLM, 다른 프로그램)이 쓴다면? "표준"의 의미는?
#  3) 쓰기 도구를 막는 코드는 AI 쪽에 있는가, 우리 프로그램 쪽에 있는가?
