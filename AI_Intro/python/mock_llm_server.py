# 모의 LLM 서버 - Gemini 의 generateContent / streamGenerateContent REST 형식을 흉내 낸다.
#   * 진짜 AI 가 아니라 "규칙 기반"이다. 키·네트워크·한도 걱정 없이 Agent 의 구조(요청/응답/도구 호출)를 실습하기 위한 것.
#   * 같은 클라이언트 코드가 진짜 Gemini 에서도 그대로 동작한다 (주소만 다르다).
#   compose.yaml 의 mock-llm 서비스로 자동 실행된다. 포트 8000.
import http.server
import json
import re
import time

PORT = 8000
LATENCY = 0.4                                      # 네트워크/추론 지연을 흉내 낸다 (초)
SENSOR_WORDS = {"temp01": ("temp01", "1호", "라인1", "라인 1", "line1"),
                "temp02": ("temp02", "2호", "라인2", "라인 2", "line2")}


def texts_of(content):
    return [p["text"] for p in content.get("parts", []) if "text" in p]


def sensors_in(text):
    low = text.lower()
    return [sid for sid, words in SENSOR_WORDS.items() if any(w in low for w in words)]


def has_tool(tools, name):
    return any(d["name"] == name for t in (tools or []) for d in t.get("functionDeclarations", []))


def answer_from_results(responses):
    """도구 실행 결과(functionResponse)를 받아 최종 답을 만든다."""
    errors = [r for r in responses if "error" in r["response"]]
    if errors:
        return f"죄송합니다. 요청을 처리하지 못했습니다: {errors[0]['response']['error']}"
    temps = [(r["response"]["id"], r["response"]["value"]) for r in responses if r["name"] == "get_temperature"]
    if len(temps) == 2:
        (a, va), (b, vb) = temps
        hot = a if va >= vb else b
        return f"{a}은(는) {va}℃, {b}은(는) {vb}℃입니다. {hot} 쪽이 더 따뜻합니다."
    if len(temps) == 1:
        return f"{temps[0][0]}의 현재 온도는 {temps[0][1]}℃입니다."
    for r in responses:
        if r["name"] == "list_sensors":
            names = ", ".join(f"{s['id']}({s['line']})" for s in r["response"]["sensors"])
            return f"현재 등록된 센서는 {names} 입니다."
        if r["name"] == "set_setpoint":
            d = r["response"]
            return f"{d['id']}의 설정 온도를 {d['setpoint']}℃로 변경했습니다."
    return "요청하신 작업을 마쳤습니다."


def respond(contents, tools):
    """규칙으로 '모델의 다음 말'(parts 목록)을 정한다."""
    last = contents[-1]
    frs = [p["functionResponse"] for p in last.get("parts", []) if "functionResponse" in p]
    if frs:
        return [{"text": answer_from_results(frs)}]

    user_texts = [t for c in contents if c.get("role") == "user" for t in texts_of(c)]
    text = user_texts[-1] if user_texts else ""
    ids = sensors_in(text)

    if "센서" in text and any(w in text for w in ("어떤", "목록", "뭐가", "무엇")) and has_tool(tools, "list_sensors"):
        return [{"functionCall": {"name": "list_sensors", "args": {}}}]
    mo = re.search(r"(\d+(?:\.\d+)?)\s*(?:도|℃|°)", text)
    if "설정" in text and mo and any(w in text for w in ("바꿔", "변경", "올려", "내려", "설정해")):
        if has_tool(tools, "set_setpoint"):
            return [{"functionCall": {"name": "set_setpoint", "args": {"sensor_id": (ids or ["temp01"])[0], "value": float(mo.group(1))}}}]
        return [{"text": "설정 온도를 바꾸는 도구가 제공되지 않아 변경할 수 없습니다."}]
    if any(w in text for w in ("온도", "기온", "몇 도", "따뜻", "더워", "높")):
        if not has_tool(tools, "get_temperature"):
            return [{"text": "저는 실시간 센서 값에 접근할 수 없어서 현재 온도는 알 수 없습니다. (도구가 있어야 합니다)"}]
        if any(w in text for w in ("비교", "더 따뜻", "어느", "어디가")) and len(ids) < 2:
            ids = list(SENSOR_WORDS)
        return [{"functionCall": {"name": "get_temperature", "args": {"sensor_id": sid}}} for sid in (ids or ["temp01"])]

    def name_of(s):
        mo = re.search(r"내 이름은 ([가-힣A-Za-z0-9]+?)(?:이야|야|입니다|이에요|예요)?[\s.!]*$", s)
        return mo.group(1) if mo else None

    def place_of(s):
        mo = re.search(r"(\S+?) 공장에서 일", s)
        return mo.group(1) if mo else None

    if "이름이 뭐" in text:
        for t_ in reversed(user_texts[:-1]):
            if name_of(t_):
                return [{"text": f"{name_of(t_)}님이라고 하셨어요."}]
        return [{"text": "아직 이름을 듣지 못했어요."}]
    if "어디서" in text and ("일" in text or "근무" in text):
        for t_ in reversed(user_texts[:-1]):
            if place_of(t_):
                return [{"text": f"{place_of(t_)} 공장에서 일한다고 하셨어요."}]
        return [{"text": "아직 근무지를 듣지 못했어요."}]
    if name_of(text):
        return [{"text": f"반가워요, {name_of(text)}님!"}]
    if place_of(text):
        return [{"text": f"{place_of(text)} 공장에서 일하시는군요. 기억해 둘게요."}]
    if "HTTP" in text and ("API" in text or "란" in text):
        return [{"text": "HTTP API는 HTTP 프로토콜로 다른 프로그램의 기능과 데이터를 이용할 수 있게 한 인터페이스입니다."}]
    if "MCP" in text:
        return [{"text": "MCP(Model Context Protocol)는 AI가 외부 도구와 데이터를 표준화된 방식으로 사용하게 해 주는 프로토콜입니다. 메시지는 JSON-RPC 2.0 을 씁니다."}]
    if "에이전트" in text or "Agent" in text:
        return [{"text": "AI Agent는 LLM이 목표를 이해하고, 도구를 호출하고, 결과를 보고 다음 행동을 정하는 일을 반복하는 구조입니다."}]
    if any(w in text for w in ("안녕", "hello", "Hello")):
        return [{"text": "안녕하세요! 저는 모의 LLM(규칙 기반)입니다. 센서 온도나 설정을 물어보세요."}]
    return [{"text": "네, 알겠습니다. (모의 LLM은 규칙 기반이라 이해하는 문장이 제한적입니다)"}]


def usage(contents, parts):
    sent = sum(len(json.dumps(c, ensure_ascii=False)) for c in contents) // 3
    out = sum(len(json.dumps(p, ensure_ascii=False)) for p in parts) // 3
    return {"promptTokenCount": sent, "candidatesTokenCount": out, "totalTokenCount": sent + out}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        contents, tools = body.get("contents", []), body.get("tools")
        stream = ":streamGenerateContent" in self.path
        time.sleep(LATENCY)
        parts = respond(contents, tools)
        kinds = ["functionCall" if "functionCall" in p else "functionResponse" if "functionResponse" in p else "text" for p in parts]
        print(f"[mock-llm] 요청 contents={len(contents)}개 -> 응답 {kinds}", flush=True)
        text_len = sum(len(p.get("text", "")) for p in parts)
        if not stream:
            time.sleep(0.12 * ((text_len + 5) // 6))          # 답이 길수록 완성까지 오래 걸린다 (실제 LLM 처럼)
            out = {"candidates": [{"content": {"role": "model", "parts": parts}, "finishReason": "STOP"}],
                   "usageMetadata": usage(contents, parts)}
            self._json(out)
            return
        # 스트리밍(SSE): 글을 조각내서 조금씩 보낸다
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")   # (진짜 Gemini 처럼 charset 표시 없음)
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        text = "".join(p.get("text", "") for p in parts)
        chunks = [text[i:i + 6] for i in range(0, len(text), 6)] if text else [None]
        for k, ch in enumerate(chunks):
            last = k == len(chunks) - 1
            cparts = [{"text": ch}] if ch is not None else parts
            msg = {"candidates": [{"content": {"role": "model", "parts": cparts}, **({"finishReason": "STOP"} if last else {})}]}
            if last:
                msg["usageMetadata"] = usage(contents, parts)
            self.wfile.write(f"data: {json.dumps(msg, ensure_ascii=False)}\r\n\r\n".encode())
            self.wfile.flush()
            time.sleep(0.12)

    def _json(self, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass


print(f"모의 LLM 서버 시작: 포트 {PORT}  (Gemini generateContent 형식, 규칙 기반)", flush=True)
http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
