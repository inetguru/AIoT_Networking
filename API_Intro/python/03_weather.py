# 실습 3 : 기상청 초단기실황 API 호출 - 응답 JSON에서 필요한 값만 꺼내기
#   기본값은 모의 서버. 실제 API로 바꾸려면 .env 에 KMA_BASE / KMA_KEY 설정 (.env.example 참고)
import os
from datetime import datetime, timedelta, timezone
import requests

BASE = os.environ.get("KMA_BASE", "http://mock-kma:4000")
KEY = os.environ.get("KMA_KEY", "mock-key")          # 키는 코드에 쓰지 않고 환경변수로 받는다

# 초단기실황은 매시 40분경 발표 -> 40분 전 시각의 정시를 기준으로 (한국 시간)
kst = datetime.now(timezone(timedelta(hours=9))) - timedelta(minutes=40)

url = BASE + "/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
params = {
    "serviceKey": KEY,
    "pageNo": 1, "numOfRows": 10, "dataType": "JSON",
    "base_date": kst.strftime("%Y%m%d"),
    "base_time": kst.strftime("%H00"),
    "nx": 98, "ny": 76,                              # 격자 좌표 (부산)
}

r = requests.get(url, params=params, timeout=10)
print("상태 코드:", r.status_code)

try:
    data = r.json()
except ValueError:                                   # JSON이 아닌 응답 (예: 인증키 오류 메시지)
    raise SystemExit("JSON이 아닌 응답입니다:\n" + r.text[:300])

# 응답 구조를 따라 내려간다:  response -> body -> items -> item (리스트)
items = data["response"]["body"]["items"]["item"]
for it in items:
    print(it["category"], it["obsrValue"])

temp = [it["obsrValue"] for it in items if it["category"] == "T1H"][0]
print(f"\n부산 현재 기온: {temp} ℃")

# 해 보라
#  1) 습도(REH)와 풍속(WSD)도 함께 출력하도록 고쳐 보라
#  2) nx, ny 를 다른 지역으로 바꿔 보라 (서울 60,127 / 대구 89,90)
#  3) Postman 에서 같은 호출을 하고 Response 와 비교해 보라
