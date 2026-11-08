# 실습 6 (SDK) : MCP 클라이언트 - 서버에게 "무슨 도구가 있나?"를 묻고, 도구를 부른다
#   사용:  .\run.cmd 06_mcp_client.py
import asyncio
import json
import sys

import mcp
from mcp.client.stdio import StdioServerParameters


async def main():
    server = StdioServerParameters(command=sys.executable, args=["-u", "06_mcp_server.py"])
    async with mcp.Client(server) as client:                       # 서버를 자식 프로세스로 띄워 연결 (initialize 자동)
        info = client.server_info
        print(f"연결됨: 서버 '{getattr(info, 'name', info)}'\n")

        print("=== 1) list_tools : 서버가 내놓은 도구 (이름, 설명, 인자)")
        tools = (await client.list_tools()).tools
        for t in tools:
            props = list((t.input_schema or {}).get("properties", {}))
            print(f"  - {t.name}({', '.join(props)}) : {t.description}")

        print("\n=== 2) call_tool : 도구를 호출한다")
        for name, args in [("get_temperature", {"sensor_id": "temp01"}), ("get_temperature", {"sensor_id": "zzz"})]:
            res = await client.call_tool(name, args)
            data = res.structured_content or json.loads(res.content[0].text)
            print(f"  {name}({args}) -> {data}")


asyncio.run(main())

# 해 보라
#  1) 이 클라이언트 코드에는 "get_temperature" 가 하드코딩되어 있나? 도구 목록은 어디서 왔는가?
#  2) 06_mcp_server.py 에 도구 하나를 추가하면(예: 평균 온도), 이 클라이언트는 코드 수정 없이 그 도구를 볼 수 있는가?
