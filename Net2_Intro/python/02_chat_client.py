# 실습 2 (클라이언트) : "기억하는 서버"와 "기억하지 않는 서버"
#   사용:  .\run.cmd 02_chat_client.py
import requests

BASE = "http://chat:9200"


def post(path, **body):
    return requests.post(BASE + path, json=body, timeout=5).json()


def show(who, text):
    print(f"    나   : {who}")
    print(f"    서버 : {text}")


print("=== 장면 1. Stateless - 새 문장만 보낸다")
show("내 이름은 철수", post("/stateless", messages=["내 이름은 철수"])["answer"])
show("내 이름이 뭐야?", post("/stateless", messages=["내 이름이 뭐야?"])["answer"])
print("  -> 서버는 앞 요청을 기억하지 않는다\n")

print("=== 장면 2. Stateless - 대화 전체를 매번 함께 보낸다 (LLM API 방식)")
history = []
for text in ["내 이름은 철수", "내 이름이 뭐야?"]:
    history.append(text)
    show(text, post("/stateless", messages=list(history))["answer"])
print(f"  -> 클라이언트가 이력을 들고 있다. 두 번째 요청에는 문장 {len(history)}개가 들어갔다\n")

print("=== 장면 3. Stateful - 세션 번호와 새 문장만 보낸다")
for text in ["내 이름은 영희", "내 이름이 뭐야?"]:
    show(text, post("/stateful", session="s1", text=text)["answer"])
print("  -> 서버가 세션별로 기억한다. 서버 상태:", requests.get(BASE + "/stats", timeout=5).json(), "\n")

print("=== 장면 4. 서버가 재시작되었다면? (다른 서버로 요청이 갔다고 생각해도 같다)")
post("/restart")
show("내 이름이 뭐야?   (Stateful, 같은 세션 s1)", post("/stateful", session="s1", text="내 이름이 뭐야?")["answer"])
show("내 이름이 뭐야?   (Stateless, 이력을 함께 보냄)", post("/stateless", messages=["내 이름은 철수", "내 이름이 뭐야?"])["answer"])
print("  -> Stateful 은 서버가 상태를 잃으면 대화도 잃는다. Stateless 는 서버를 늘리거나 바꿔도 문제가 없다")

# 해 보라
#  1) 장면 2에서 대화가 길어질수록 요청의 크기는 어떻게 될까? (LLM API 의 토큰 비용과 연결해 보라)
#  2) 서버가 100대로 늘어나고 요청이 아무 서버로나 간다면 Stateful 방식에는 어떤 문제가 생길까?
#  3) 센서 값을 받는 서버는 Stateless 가 좋을까, Stateful 이 좋을까?
