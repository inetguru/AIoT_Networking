# 실습 6 (손으로) : MCP 는 "JSON-RPC 2.0" 메시지다 - SDK 없이 줄 단위 JSON 을 직접 주고받아 본다
#   사용:  .\run.cmd 06_mcp_raw.py
import json
import subprocess
import sys

proc = subprocess.Popen([sys.executable, "-u", "06_mcp_server.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL, text=True, bufsize=1)
_id = 0


def show(arrow, msg):
    print(f"{arrow} {json.dumps(msg, ensure_ascii=False)[:230]}")


def request(method, params=None):
    """요청(id 가 있다)을 보내고, 같은 id 의 응답을 기다린다."""
    global _id
    _id += 1
    msg = {"jsonrpc": "2.0", "id": _id, "method": method, "params": params or {}}
    show("클라이언트 → 서버", msg)
    proc.stdin.write(json.dumps(msg) + "\n")
    while True:
        reply = json.loads(proc.stdout.readline())
        if reply.get("id") == _id:
            show("서버 → 클라이언트", reply)
            print()
            return reply["result"]


def notify(method):
    msg = {"jsonrpc": "2.0", "method": method}                   # 알림: id 가 없으니 응답도 없다
    show("클라이언트 → 서버", msg)
    proc.stdin.write(json.dumps(msg) + "\n")
    print()


print("=== 1) initialize : 서로 인사하고 능력을 교환한다")
init = request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "raw-client", "version": "1.0"}})
print(f"   → 서버 이름: {init.get('serverInfo', {}).get('name')}, 서버가 선택한 프로토콜 버전: {init.get('protocolVersion')}\n")
notify("notifications/initialized")

print("=== 2) tools/list : 이 서버가 가진 도구의 목록과 사용설명서를 묻는다")
tools = request("tools/list")["tools"]
print("   → 도구:", [t["name"] for t in tools], "\n")

print("=== 3) tools/call : 도구를 호출한다")
result = request("tools/call", {"name": "get_temperature", "arguments": {"sensor_id": "temp01"}})
print("   → 결과 content:", result["content"][0]["text"][:100], "\n")

proc.stdin.close()
proc.terminate()

# 해 보라
#  1) 모든 메시지에 "jsonrpc": "2.0" 이 있다. 요청과 응답은 무엇으로 짝을 맞추는가? ("id")
#  2) 알림(notification)은 요청과 무엇이 다른가?
#  3) tools/list 응답의 한 도구를 보라. "name", "description", "inputSchema" — 05 번 실습의 "도구 설명서"와 같은가?
#  4) 이 통신은 HTTP 가 아니라 표준 입출력(stdio)이다. MCP 는 HTTP 로도 쓸 수 있다 (전송 방식만 다르고 메시지는 같다)
