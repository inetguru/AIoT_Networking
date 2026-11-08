# 실습 6 (서버) : MCP 서버 - 기존 시스템(plant REST API)을 "AI 가 쓸 수 있는 도구"로 표준화해서 내놓는다
#   이 파일은 직접 실행하지 않는다. 클라이언트(06_mcp_raw.py, 06_mcp_client.py, 07_mcp_agent.py)가
#   자식 프로세스로 띄우고 표준 입출력(stdio)으로 대화한다.
#   (주의: stdout 은 MCP 메시지 전용이다. 사람이 볼 로그는 stderr 로 보낸다)
import os
import sys

import requests
from mcp.server.mcpserver import MCPServer

PLANT = os.environ.get("PLANT_URL", "http://plant:8200")

server = MCPServer("factory-sensors", instructions="공장 온도 센서를 조회하고, 설정 온도를 바꾸는 도구 모음")


def log(*a):
    print("[mcp-server]", *a, file=sys.stderr, flush=True)


@server.tool()
def list_sensors() -> dict:
    """공장에 등록된 모든 온도 센서의 목록과 현재 값을 돌려준다."""
    log("list_sensors")
    return requests.get(f"{PLANT}/sensors", timeout=5).json()


@server.tool()
def get_temperature(sensor_id: str) -> dict:
    """센서 한 개의 현재 온도(섭씨)를 돌려준다. sensor_id 예: temp01, temp02"""
    log("get_temperature", sensor_id)
    r = requests.get(f"{PLANT}/sensors/{sensor_id}", timeout=5)
    return r.json() if r.ok else {"error": f"센서 '{sensor_id}' 를 찾을 수 없다"}


@server.tool()
def set_setpoint(sensor_id: str, value: float) -> dict:
    """센서가 달린 설비의 설정 온도(섭씨)를 변경한다. 설비를 실제로 바꾸는 쓰기 동작이다."""
    log("set_setpoint", sensor_id, value)
    r = requests.put(f"{PLANT}/sensors/{sensor_id}/setpoint", json={"value": value}, timeout=5)
    return r.json() if r.ok else {"error": f"센서 '{sensor_id}' 를 찾을 수 없다"}


if __name__ == "__main__":
    server.run("stdio")
