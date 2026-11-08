# 실습 2 : POST 호출 - 데이터(Body)를 보내고, 헤더(Header)로 인증 정보를 전달하기
#   Postman:  POST https://postman-echo.com/post
#             Headers: X-My-Key = abc123      Body(raw, JSON): {"sensor": "temp-01", "value": 23.5}
import requests

url = "https://postman-echo.com/post"
headers = {"X-My-Key": "abc123"}                       # 인증 정보는 URL이 아닌 Header 로 (네이버/카카오 방식)
body = {"sensor": "temp-01", "value": 23.5}            # 서버로 보낼 데이터

r = requests.post(url, headers=headers, json=body)     # json= 을 쓰면 JSON 텍스트로 바꿔서 보낸다

print("상태 코드 :", r.status_code)
result = r.json()
print("서버가 받은 Body   :", result["json"])
print("서버가 받은 Header :", result["headers"].get("x-my-key"))

# 해 보라
#  1) value 를 바꿔서 다시 보내 보라
#  2) Postman Echo 는 받은 내용을 그대로 되돌려 준다. 서버가 받은 Header 에 우리가 보낸 키가 있는가?
