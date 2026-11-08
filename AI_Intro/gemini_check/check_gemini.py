# Gemini API 접근 점검 (수업에서 쓸 수 있는지 확인용)
#   학생 계정(대학 Google Workspace)으로 발급한 API 키로 아래 4가지를 차례로 확인한다.
#     1) 키가 유효하고, 사용 가능한 모델 목록이 보이는가       (GET  /v1beta/models)
#     2) 글을 생성할 수 있는가                                 (POST :generateContent)
#     3) 함수 호출(Tool Calling)이 되는가                      (tools / functionDeclarations)
#     4) 스트리밍(SSE)으로 조금씩 받을 수 있는가               (:streamGenerateContent?alt=sse)
#   키는 코드에 쓰지 않고 환경변수 GEMINI_API_KEY 로 받는다 (.env 에 넣는다).
import os
import sys
import json
import time
import requests

BASE = "https://generativelanguage.googleapis.com/v1beta"
KEY = os.environ.get("GEMINI_API_KEY", "").strip()
FORCED_MODEL = os.environ.get("GEMINI_MODEL", "").strip()     # 지정하면 이 모델로 시험
results = []                                                  # (항목, 성공 여부, 메모)


def diagnose(r):
    """오류 응답을 사람이 이해할 수 있는 말로 바꾼다."""
    try:
        err = r.json().get("error", {})
    except ValueError:
        err = {}
    msg = err.get("message", r.text[:200])
    status = err.get("status", "")
    hint = {
        400: "요청 형식 오류이거나 API 키가 올바르지 않습니다 (API_KEY_INVALID?)",
        401: "인증 실패: 키가 없거나 잘못되었습니다",
        403: "권한 없음: 이 계정/프로젝트에서 Gemini API 사용이 허용되지 않았을 수 있습니다 (관리자 정책, 지역, 나이 제한)",
        404: "모델 이름이 없습니다 (모델이 바뀌었거나 이 키로는 쓸 수 없음)",
        429: "호출 한도 초과 (무료 한도). 잠시 후 다시 시도하거나 다른 모델을 써 보세요",
        500: "Google 서버 오류. 잠시 후 다시 시도",
        503: "서버가 바쁩니다. 잠시 후 다시 시도",
    }.get(r.status_code, "")
    return f"HTTP {r.status_code} {status}: {msg}" + (f"\n    → {hint}" if hint else "")


def call(method, url, **kw):
    kw.setdefault("timeout", 30)
    headers = kw.pop("headers", {})
    headers["x-goog-api-key"] = KEY                    # 키는 URL이 아니라 Header 로 (06_search_api 와 같은 방식)
    t0 = time.time()
    r = requests.request(method, url, headers=headers, **kw)
    return r, time.time() - t0


def pick_model(models):
    """generateContent 를 지원하는 텍스트용 flash 모델 중 하나를 고른다."""
    bad = ("image", "tts", "audio", "live", "embedding", "robotics", "computer", "veo", "imagen", "native", "preview-")
    ok = []
    for m in models:
        name = m["name"].replace("models/", "")
        if "generateContent" not in m.get("supportedGenerationMethods", []):
            continue
        if "flash" in name and not any(b in name for b in bad):
            ok.append(name)
    stable = [n for n in ok if "preview" not in n and "exp" not in n and "latest" not in n]
    pool = stable or ok
    return sorted(pool)[-1] if pool else None


if not KEY:
    sys.exit("GEMINI_API_KEY 가 설정되어 있지 않습니다.\n"
             "  1) https://aistudio.google.com/apikey 에서 API 키를 만든다\n"
             "  2) API_Intro 와 같은 방식으로 .env 에 GEMINI_API_KEY=키 를 넣는다 (.env.example 참고)")

print(f"키 길이: {len(KEY)} (값은 출력하지 않음)\n")

# ---- 1) 모델 목록 -------------------------------------------------------------
print("[1] 사용 가능한 모델 목록")
try:
    r, sec = call("GET", f"{BASE}/models", params={"pageSize": 200})
except requests.RequestException as e:
    sys.exit(f"  네트워크 오류: {e}\n  → 이 네트워크에서 generativelanguage.googleapis.com 에 접속할 수 있는지 확인")
if r.status_code != 200:
    print("  실패:", diagnose(r))
    results.append(("모델 목록", False, f"HTTP {r.status_code}"))
    print("\n결과 요약: 키 또는 계정 권한 문제로 이후 단계를 진행할 수 없습니다.")
    sys.exit(1)
models = r.json().get("models", [])
gen = [m["name"].replace("models/", "") for m in models if "generateContent" in m.get("supportedGenerationMethods", [])]
print(f"  성공 ({sec:.1f}초): 전체 {len(models)}개, generateContent 지원 {len(gen)}개")
for n in sorted(gen)[:12]:
    print("   -", n)
if len(gen) > 12:
    print(f"   ... 외 {len(gen) - 12}개")
results.append(("모델 목록", True, f"{len(gen)}개"))

model = FORCED_MODEL or pick_model(models)
if not model:
    sys.exit("시험할 flash 모델을 찾지 못했습니다. GEMINI_MODEL 로 모델 이름을 지정하세요.")
print(f"\n  시험에 사용할 모델: {model}\n")

# ---- 2) 글 생성 ---------------------------------------------------------------
print("[2] 글 생성 (generateContent)")
body = {"contents": [{"role": "user", "parts": [{"text": "한 문장으로 답해 줘: HTTP API란 무엇인가?"}]}]}
r, sec = call("POST", f"{BASE}/models/{model}:generateContent", json=body)
if r.status_code == 200:
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        text = "(응답 형식이 예상과 다름) " + json.dumps(data, ensure_ascii=False)[:200]
    usage = data.get("usageMetadata", {})
    print(f"  성공 ({sec:.1f}초)\n  응답: {text}")
    print(f"  토큰: 입력 {usage.get('promptTokenCount')}, 출력 {usage.get('candidatesTokenCount')}, 합계 {usage.get('totalTokenCount')}")
    results.append(("글 생성", True, f"{sec:.1f}초"))
else:
    print("  실패:", diagnose(r))
    results.append(("글 생성", False, f"HTTP {r.status_code}"))

# ---- 3) 함수 호출 (Tool Calling) -----------------------------------------------
print("\n[3] 함수 호출 (Tool Calling) - 수업의 get_temperature 와 같은 함수를 AI에게 알려 준다")
body = {
    "contents": [{"role": "user", "parts": [{"text": "부산의 현재 기온을 알려 줘. (부산 격자 좌표는 nx=98, ny=76)"}]}],
    "tools": [{"functionDeclarations": [{
        "name": "get_temperature",
        "description": "격자 좌표 (nx, ny) 지역의 현재 기온(섭씨)을 돌려준다.",
        "parameters": {"type": "object",
                       "properties": {"nx": {"type": "integer", "description": "격자 X 좌표"},
                                      "ny": {"type": "integer", "description": "격자 Y 좌표"}},
                       "required": ["nx", "ny"]}}]}],
}
r, sec = call("POST", f"{BASE}/models/{model}:generateContent", json=body)
if r.status_code == 200:
    parts = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
    calls = [p["functionCall"] for p in parts if "functionCall" in p]
    if calls:
        print(f"  성공 ({sec:.1f}초): AI가 함수 호출을 요청했다 → {json.dumps(calls[0], ensure_ascii=False)}")
        results.append(("함수 호출", True, calls[0].get("name", "")))
    else:
        print("  AI가 함수를 부르지 않고 글로만 답했다:", json.dumps(parts, ensure_ascii=False)[:200])
        results.append(("함수 호출", False, "functionCall 없음"))
else:
    print("  실패:", diagnose(r))
    results.append(("함수 호출", False, f"HTTP {r.status_code}"))

# ---- 4) 스트리밍 --------------------------------------------------------------
print("\n[4] 스트리밍 (SSE) - 답이 한 번에 오는지, 조금씩 오는지")
body = {"contents": [{"role": "user", "parts": [{"text": "공장 센서 데이터를 서버로 보내는 방법을 5문장으로 설명해 줘."}]}]}
t0 = time.time()
try:
    r = requests.post(f"{BASE}/models/{model}:streamGenerateContent", params={"alt": "sse"},
                      headers={"x-goog-api-key": KEY}, json=body, stream=True, timeout=60)
    if r.status_code == 200:
        chunks = []
        for line in r.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                try:
                    d = json.loads(line[6:])
                    txt = d["candidates"][0]["content"]["parts"][0].get("text", "")
                except (ValueError, KeyError, IndexError):
                    continue
                chunks.append((time.time() - t0, txt))
        print(f"  성공: {len(chunks)}개 조각으로 도착")
        for sec, txt in chunks[:4]:
            print(f"   +{sec:.1f}초  {txt[:40].strip()!r}")
        results.append(("스트리밍", len(chunks) > 1, f"{len(chunks)}개 조각"))
    else:
        print("  실패:", diagnose(r))
        results.append(("스트리밍", False, f"HTTP {r.status_code}"))
except requests.RequestException as e:
    print("  네트워크 오류:", e)
    results.append(("스트리밍", False, "네트워크 오류"))

# ---- 요약 ---------------------------------------------------------------------
print("\n=== 결과 요약 ===")
for name, ok, note in results:
    print(f"  [{'OK' if ok else 'FAIL'}] {name}  {note}")
print("\n참고: 무료 사용량의 입력 내용은 Google 제품 개선에 사용될 수 있다. 민감한 정보는 넣지 않는다.")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
