# 실습 4 : API 호출은 실패할 수 있다 - 실패를 다루는 방법
#   원격 호출은 지역 호출과 다르다 (주제 2, '분산 컴퓨팅의 8가지 오해')
import os
import requests

BASE = os.environ.get("KMA_BASE", "http://mock-kma:4000")

# 1) 서버는 응답했지만 '실패'를 알려 주는 경우 : 상태 코드 확인
r = requests.get("https://postman-echo.com/status/404")
print("1) 상태 코드:", r.status_code, "/ 성공 여부(r.ok):", r.ok)

# 2) 서버가 너무 늦게 응답하는 경우 : timeout 을 반드시 지정한다
try:
    requests.get("https://postman-echo.com/delay/5", timeout=2)      # 서버는 5초 뒤에 응답
except requests.exceptions.Timeout:
    print("2) 2초 안에 응답이 없어 포기했다 (Timeout)")

# 3) 서버에 아예 연결할 수 없는 경우
try:
    requests.get("http://localhost:9/", timeout=2)                   # 아무도 듣지 않는 포트
except requests.exceptions.ConnectionError:
    print("3) 서버에 연결할 수 없다 (ConnectionError)")

# 4) 응답이 약속한 JSON 형식이 아닌 경우
r = requests.get(BASE + "/")                                         # 이 주소는 JSON이 아닌 글자를 돌려준다
try:
    r.json()
except ValueError:
    print("4) JSON이 아니다. 받은 내용:", r.text[:30].strip())

# 해 보라
#  1) 2번의 timeout 을 10 으로 바꾸면 어떻게 되는가?
#  2) 만약 timeout 을 지정하지 않았다면 프로그램은 어떻게 될까? (공장 라인의 데이터 수집 프로그램이라면?)
