# AI_Intro — 인공지능과 네트워크 프로그래밍

LLM도 결국 **HTTP API**다. 이 폴더에서는 AI에게 말을 걸고(LLM API), AI가 **도구를 부르게** 하고(Tool Calling), 그것을 반복하는 **Agent**를 만들고, 도구를 **표준 방식(MCP)** 으로 내놓고, 에이전트끼리 **서로 찾아 일을 맡기는(A2A)** 구조를 직접 실행해 본다.

> 모든 실습은 **키 없이** 된다. 기본으로 **모의 LLM 서버**(규칙 기반)가 동작하고, `.env` 에 Gemini 키를 넣으면 **같은 코드가 진짜 Gemini**로 동작한다.
> (Gemini 접근 가능 여부 점검 도구는 [`gemini_check/`](gemini_check))

## 준비
- Docker Desktop 실행, 실습 이미지 준비 (`Web_Intro\check.cmd`)
- (선택) 진짜 Gemini 사용: [AI Studio](https://aistudio.google.com/apikey)에서 API 키를 만들고, `.env.example` 을 `.env` 로 복사해 `GEMINI_API_KEY=` 줄을 채운다
  - 키는 **개인 자격 증명**이다. 코드나 GitHub에 올리지 않는다 (`.env` 는 Git에서 제외됨)
  - 무료 키의 입력은 Google 제품 개선에 쓰일 수 있으니 **민감한 내용은 넣지 않는다**
  - 무료 키는 **호출 한도가 작다**. 한도에 걸리면 자동으로 모의 LLM으로 넘어가며 화면에 알려 준다 (`LLM_FALLBACK=none` 으로 끌 수 있다)

## 실행 방법
PowerShell에서 `AI_Intro` 폴더로 이동한 뒤:
```
.\run.cmd 01_hello_llm.py
```
서버들(모의 LLM, 설비 API, 설비 에이전트)이 **자동으로 함께 시작**된다. 끝나면 `docker compose down`.
화면 첫 줄의 `[LLM] ...` 으로 지금 모의 LLM인지 진짜 Gemini인지 확인할 수 있다.

## 실습 순서

| # | 실행 | 배우는 것 |
|---|---|---|
| 1 | `01_hello_llm.py` | LLM 호출은 **HTTP API**: 요청 JSON(`contents`) → 응답 JSON(`parts`). 토큰과 지연 |
| 2 | `02_chat_history.py` | LLM API는 **Stateless**: 대화 이력을 **내가** 매번 보낸다. 이력이 길어질수록 입력 토큰(=비용)이 늘어난다 |
| 3 | `03_streaming.py` | **스트리밍(SSE)**: 답이 완성될 때까지 기다리지 않고 만들어지는 대로 받는다. 첫 글자까지의 시간 비교 |
| 4 | `04_tool_calling.py` | **Tool Calling**: AI는 함수를 *실행*하지 않고 **호출을 요청**한다. 실행은 우리 프로그램이 한다 |
| 5 | `05_agent_loop.py` | **Agent = LLM + 도구 + 반복**. 여러 도구를 한 번에 요청, **쓰기 도구는 기본 차단**(권한 통제) |
| 6 | `06_mcp_raw.py`, `06_mcp_client.py` | **MCP**: 도구를 표준으로 내놓는 서버. 메시지는 **JSON-RPC 2.0**. 손으로 주고받아 보고(raw), SDK로도 해 본다 |
| 7 | `07_mcp_agent.py` | MCP 서버에서 도구를 **발견**해서 쓰는 Agent (도구 목록을 코드에 적지 않는다) |
| 8 | `08_a2a_client.py` | **A2A**: 에이전트가 다른 에이전트의 **Agent Card(명함)** 를 읽고 일을 맡긴다 |

### 공통 시나리오: 공장 온도 센서
모든 실습의 대상은 **공장 설비 API**(`plant`, 센서 `temp01`, `temp02`)다. 기존 시스템(REST API)을 AI의 도구로 만드는 과정을 따라간다.
```
사용자 → AI(LLM) ─ "get_temperature 를 불러 줘" ─▶ 우리 프로그램 ──▶ plant API (센서 값)
              ◀──────────── 결과를 돌려준다 ◀────────────
```
설비의 실제 동작은 `docker compose logs plant` 로 볼 수 있다 (`--allow-write` 로 설정을 바꾸면 기록이 남는다).

### 5번 실습: 권한 통제
```
.\run.cmd 05_agent_loop.py                                              세 가지 질문 (마지막은 쓰기 요청 → 차단됨)
.\run.cmd 05_agent_loop.py "temp01 설정 온도를 28도로 바꿔 줘" --allow-write     쓰기를 허용해서 실행
```
AI가 **위험한 요청**을 해도 **우리 프로그램이 막을 수 있다.** 차단 사유를 받은 AI가 어떻게 답하는지 보라. 판단하는 것은 AI이지만, **무엇을 실행할지 결정하는 것은 사람이 짠 코드**다.

## 알아 두면 좋은 점
- **모의 LLM은 규칙 기반**이라 정해진 몇 가지 문장만 이해한다 (센서·온도·설정, 이름 기억, 몇 가지 정의). 진짜 AI의 이해력을 보여 주는 것이 아니라 **요청·응답·도구 호출의 구조**를 보여 주는 용도다.
- 진짜 Gemini는 응답에 수 초가 걸린다. `합계 토큰`이 `입력+출력`보다 큰 것은 모델이 답하기 전에 **'생각'에 쓴 토큰**도 세기 때문이다.
- 모델 이름은 자주 바뀐다. 오류가 나면 `GEMINI_MODEL` 로 지정하거나 [`gemini_check`](gemini_check) 로 쓸 수 있는 모델을 확인한다.
- `requests` 로 SSE를 읽을 때는 `iter_lines(chunk_size=1)` 과 `r.encoding = "utf-8"` 이 필요하다 (`llm.py` 참고).
- MCP SDK 2.x 는 이름이 바뀐 것이 있다 (`MCPServer`, `input_schema` 등). 인터넷의 예전 예제(`FastMCP`, `inputSchema`)와 다를 수 있다.
- A2A는 규격이 계속 바뀌고 있어 **개념을 보여 주는 단순화 데모**다 (Agent Card 탐색 → JSON-RPC 요청).

## 파일 구성
```
AI_Intro/
├─ compose.yaml, run.cmd, .env.example
├─ gemini_check/            Gemini 접근 점검 도구 (별도)
└─ python/
   ├─ llm.py                 LLM 호출 도우미 (Gemini / 모의 LLM 자동 선택, 한도 초과 시 전환)
   ├─ plant_tools.py         AI에게 알려 줄 도구 정의와 실행
   ├─ 01_hello_llm.py  02_chat_history.py  03_streaming.py
   ├─ 04_tool_calling.py  05_agent_loop.py
   ├─ 06_mcp_server.py  06_mcp_raw.py  06_mcp_client.py  07_mcp_agent.py
   ├─ a2a_agent.py  08_a2a_client.py
   └─ mock_llm_server.py  plant_server.py      (자동 실행되는 서버들)
```
