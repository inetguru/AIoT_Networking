# 실습 8 : A2A - 에이전트가 "다른 에이전트"를 찾아서 일을 맡긴다
#   MCP 는 "AI -> 도구", A2A 는 "에이전트 -> 에이전트" 다.
#   사용:  .\run.cmd 08_a2a_client.py
import json
import uuid

import requests

AGENT = "http://a2a-agent:8300"

print("=== 1) 상대 에이전트를 발견한다: Agent Card (명함) 를 읽는다")
card = requests.get(f"{AGENT}/.well-known/agent-card.json", timeout=5).json()
print(f"  이름 : {card['name']}")
print(f"  설명 : {card['description']}")
for s in card["skills"]:
    print(f"  할 수 있는 일: [{s['id']}] {s['name']} - {s['description']}  예) {s['examples']}")

print("\n=== 2) 일을 맡긴다: JSON-RPC 2.0 'message/send'")
msg = {"jsonrpc": "2.0", "id": 1, "method": "message/send",
       "params": {"message": {"role": "user", "messageId": str(uuid.uuid4()),
                              "parts": [{"kind": "text", "text": "temp02 온도 알려 줘"}]}}}
print("  → 요청:", json.dumps(msg, ensure_ascii=False)[:200])
reply = requests.post(card["url"], json=msg, timeout=10).json()
print("  ← 응답:", json.dumps(reply, ensure_ascii=False)[:260])
print("\n  상대 에이전트의 답:", reply["result"]["parts"][0]["text"])

print("\n=== 3) 없는 방법을 요청하면?")
bad = requests.post(card["url"], json={"jsonrpc": "2.0", "id": 2, "method": "unknown/method", "params": {}}, timeout=5).json()
print("  ←", bad)

# 해 보라
#  1) 이 클라이언트는 상대 에이전트의 주소만 알고, "무엇을 할 수 있는지"는 어디서 알았는가?
#  2) 06번(MCP)의 tools/list 와 이 Agent Card 는 어떻게 닮았고 어떻게 다른가?
#  3) 같은 JSON-RPC 2.0 을 쓴다는 점이 MCP 와 A2A 의 공통점이다. 다른 점은 "누가 누구에게" 말하는가이다
