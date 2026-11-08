# AI 에게 알려 줄 "도구" 정의와 실행 - 기존 시스템(plant REST API)을 함수로 감싼 것
#   읽기 도구는 자유롭게, 쓰기 도구(설비를 바꾸는 것)는 허용된 경우에만 실행한다.
import os

import requests

PLANT = os.environ.get("PLANT_URL", "http://plant:8200")

# 모델에게 보여 주는 "도구 설명서" (이름, 설명, 인자). 설명이 곧 AI 의 사용설명서다.
DECLARATIONS = [
    {"name": "list_sensors",
     "description": "공장에 등록된 모든 온도 센서의 목록과 현재 값을 돌려준다.",
     "parameters": {"type": "object", "properties": {}}},
    {"name": "get_temperature",
     "description": "센서 한 개의 현재 온도(섭씨)를 돌려준다.",
     "parameters": {"type": "object",
                    "properties": {"sensor_id": {"type": "string", "description": "센서 ID. 예: temp01, temp02"}},
                    "required": ["sensor_id"]}},
    {"name": "set_setpoint",
     "description": "센서가 달린 설비의 설정 온도를 변경한다. (설비를 실제로 바꾸는 쓰기 동작)",
     "parameters": {"type": "object",
                    "properties": {"sensor_id": {"type": "string", "description": "센서 ID"},
                                   "value": {"type": "number", "description": "새 설정 온도(섭씨)"}},
                    "required": ["sensor_id", "value"]}},
]
WRITE_TOOLS = {"set_setpoint"}                     # 설비 상태를 바꾸는 도구


def run(name, args):
    """도구를 실제로 실행한다 (plant REST API 호출)."""
    if name == "list_sensors":
        return requests.get(f"{PLANT}/sensors", timeout=5).json()
    if name == "get_temperature":
        r = requests.get(f"{PLANT}/sensors/{args['sensor_id']}", timeout=5)
        return r.json() if r.ok else {"error": f"센서 '{args['sensor_id']}' 를 찾을 수 없다"}
    if name == "set_setpoint":
        r = requests.put(f"{PLANT}/sensors/{args['sensor_id']}/setpoint", json={"value": args["value"]}, timeout=5)
        return r.json() if r.ok else {"error": f"센서 '{args['sensor_id']}' 를 찾을 수 없다"}
    return {"error": f"알 수 없는 도구: {name}"}
