# 실습 1 : Postman으로 했던 GET 호출을 Python으로
#   Postman:  GET https://postman-echo.com/get   Params: foo1=bar1, foo2=bar2
import requests

url = "https://postman-echo.com/get"          # 서버 주소 + 경로 (= 함수 이름)
params = {"foo1": "bar1", "foo2": "bar2"}     # Query Parameters (= 인자)

r = requests.get(url, params=params)          # Send 버튼 = 이 한 줄

print("요청한 URL   :", r.url)                 # ? 와 & 로 이어진 URL이 만들어졌는가?
print("상태 코드    :", r.status_code)         # 200 = 성공
print("Content-Type :", r.headers["Content-Type"])
print("응답 본문    :")
print(r.json())                               # JSON 텍스트 -> Python 딕셔너리

# 해 보라
#  1) params 에 foo3 를 추가하고 다시 실행해 보라
#  2) 출력된 '요청한 URL' 을 Postman 의 URL 과 비교해 보라
