# LLM 호출 도우미 - 진짜 Gemini 와 모의 LLM 서버를 같은 코드로 쓴다.
#   GEMINI_API_KEY 가 있으면 진짜 Gemini, 없으면 모의 LLM(mock-llm 서비스)을 쓴다.
#   LLM_PROVIDER=mock 로 키가 있어도 모의 LLM 을 강제할 수 있다.
#   진짜 Gemini 가 호출 한도(429)나 연결 문제로 실패하면 자동으로 모의 LLM 으로 넘어간다 (LLM_FALLBACK=none 이면 끈다).
#   수업에서 보여 주려는 것은 "구조"다: 요청(contents) -> 응답(parts: 글 또는 functionCall) -> 다시 요청 ...
import json
import os
import sys
import time

import requests

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
MOCK_BASE = os.environ.get("MOCK_LLM_BASE", "http://mock-llm:8000/v1beta")
KEY = os.environ.get("GEMINI_API_KEY", "").strip()
FORCE = os.environ.get("LLM_PROVIDER", "").strip().lower()
FALLBACK = os.environ.get("LLM_FALLBACK", "mock").strip().lower() != "none"
MODEL = os.environ.get("GEMINI_MODEL", "").strip() or "gemini-3.6-flash"

state = {"provider": "mock" if (FORCE == "mock" or (not KEY and FORCE != "gemini")) else "gemini"}


class LLMError(RuntimeError):
    pass


def provider():
    return state["provider"]


def _base():
    return GEMINI_BASE if state["provider"] == "gemini" else MOCK_BASE


def banner():
    if state["provider"] == "gemini":
        print(f"[LLM] 진짜 Gemini 사용 · 모델 {MODEL}  (응답에 수 초가 걸린다)\n")
    else:
        print("[LLM] 모의 LLM(규칙 기반) 사용  — 진짜 Gemini 를 쓰려면 .env 에 GEMINI_API_KEY 를 넣는다\n")


def _headers():
    h = {"Content-Type": "application/json"}
    if state["provider"] == "gemini":
        h["x-goog-api-key"] = KEY                   # 키는 URL이 아니라 Header 로
    return h


def _explain(r):
    try:
        msg = r.json().get("error", {}).get("message", r.text[:200])
    except ValueError:
        msg = r.text[:200]
    hints = {400: "요청 형식이나 키를 확인하세요", 403: "이 키/계정으로는 사용할 수 없습니다",
             404: "모델 이름을 확인하세요 (GEMINI_MODEL, 모델 이름은 자주 바뀐다)",
             429: "무료 호출 한도 초과 (잠시 후 다시 하면 풀린다)"}
    return f"HTTP {r.status_code}: {msg[:110]}  → {hints.get(r.status_code, '')}"


def _switch_to_mock(reason):
    """진짜 Gemini 가 안 될 때 모의 LLM 으로 넘어간다 (한 번만 알린다)."""
    if state["provider"] == "gemini" and FALLBACK:
        state["provider"] = "mock"
        print(f"\n[LLM] ⚠ 진짜 Gemini 호출 실패({reason}) → 지금부터 모의 LLM 으로 계속한다.\n"
              "      (무료 키는 호출 한도가 작다. 이 점이 실제 서비스에서 한도·재시도·대체 수단을 설계해야 하는 이유다)\n", flush=True)
        return True
    return False


def body_of(contents, tools=None, system=None):
    body = {"contents": contents}
    if tools:
        body["tools"] = [{"functionDeclarations": tools}]
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    return body


def _post(path, body, **kw):
    """한 번 보내 본다. 실패하면 (가능하면) 모의 LLM 으로 바꿔 다시 보낸다."""
    while True:
        try:
            r = requests.post(f"{_base()}/models/{MODEL}:{path}", headers=_headers(), json=body, **kw)
        except requests.RequestException as e:
            if _switch_to_mock(f"연결 실패 {type(e).__name__}"):
                continue
            raise LLMError(f"연결 실패: {type(e).__name__}")
        if r.status_code == 200:
            return r
        if r.status_code in (429, 500, 503) and _switch_to_mock(f"HTTP {r.status_code}"):
            continue
        raise LLMError(_explain(r))


def generate(contents, tools=None, system=None):
    """한 번 호출하고 {parts, usage, seconds} 를 돌려준다. parts 는 서버가 준 그대로 보관한다(이력에 다시 넣을 때 필요)."""
    t0 = time.time()
    r = _post("generateContent", body_of(contents, tools, system), timeout=90)
    data = r.json()
    cand = data["candidates"][0]
    return {"parts": cand.get("content", {}).get("parts", []), "usage": data.get("usageMetadata", {}),
            "seconds": time.time() - t0}


def stream(contents, system=None):
    """SSE 로 조금씩 받는다. (경과 시간, 텍스트 조각, usage) 를 차례로 내놓는다."""
    t0 = time.time()
    r = _post("streamGenerateContent?alt=sse", body_of(contents, None, system), stream=True, timeout=(5, 90))
    r.encoding = "utf-8"                                   # SSE 응답에는 문자 집합 표시가 없어 직접 지정한다
    usage = {}
    for line in r.iter_lines(decode_unicode=True, chunk_size=1):   # chunk_size=1 : 도착하는 즉시 읽는다
        if not line or not line.startswith("data: "):
            continue
        d = json.loads(line[6:])
        usage = d.get("usageMetadata", usage)
        for p in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            if "text" in p:
                yield time.time() - t0, p["text"], usage


def pj(obj, limit=700):
    """오간 JSON 을 사람이 읽기 좋게 보여 준다 (너무 길면 자른다)."""
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    return s if len(s) <= limit else s[:limit] + "\n ... (생략)"


def user(text):
    return {"role": "user", "parts": [{"text": text}]}


def model_content(parts):
    return {"role": "model", "parts": parts}


def tool_results(results):
    """도구 실행 결과 [(name, dict), ...] 를 'user' 역할의 functionResponse 로 만든다."""
    return {"role": "user", "parts": [{"functionResponse": {"name": n, "response": r}} for n, r in results]}


def text_of(parts):
    return "".join(p.get("text", "") for p in parts if "text" in p)


def calls_of(parts):
    return [p["functionCall"] for p in parts if "functionCall" in p]


# ---- 학생에게는 긴 오류 화면 대신 짧은 안내를 보여 준다 (asyncio 의 ExceptionGroup 도 풀어서 찾는다)
def _find(exc):
    if isinstance(exc, LLMError):
        return exc
    for sub in getattr(exc, "exceptions", []) or []:
        found = _find(sub)
        if found:
            return found
    return None


def _hook(t, v, tb):
    err = _find(v)
    if err:
        print(f"\n[오류] {err}\n  → 모의 LLM 으로 해 보려면 .env 에서 GEMINI_API_KEY 줄을 지우거나 LLM_PROVIDER=mock 으로 설정하세요", file=sys.stderr)
        sys.exit(1)
    sys.__excepthook__(t, v, tb)


sys.excepthook = _hook
