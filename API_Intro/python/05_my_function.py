# 실습 5 : HTTP API 호출을 '내 함수'로 감싸기
#   API = 함수 호출 (주제 2).  이제 정말 함수로 만들어 보자.
import os
from datetime import datetime, timedelta, timezone
import requests

BASE = os.environ.get("KMA_BASE", "http://mock-kma:4000")
KEY = os.environ.get("KMA_KEY", "mock-key")


def get_temperature(nx, ny):
    """격자 좌표 (nx, ny) 지역의 현재 기온(℃)을 돌려준다."""
    kst = datetime.now(timezone(timedelta(hours=9))) - timedelta(minutes=40)
    params = {"serviceKey": KEY, "pageNo": 1, "numOfRows": 10, "dataType": "JSON",
              "base_date": kst.strftime("%Y%m%d"), "base_time": kst.strftime("%H00"),
              "nx": nx, "ny": ny}
    r = requests.get(BASE + "/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst", params=params, timeout=10)
    items = r.json()["response"]["body"]["items"]["item"]
    return float([it["obsrValue"] for it in items if it["category"] == "T1H"][0])


# ---- 여기부터는 이 함수를 '사용하는 쪽' : HTTP도 JSON도 몰라도 된다 ----
cities = {"부산": (98, 76), "서울": (60, 127), "대구": (89, 90)}

for name, (nx, ny) in cities.items():
    print(f"{name}: {get_temperature(nx, ny)} ℃")

hottest = max(cities, key=lambda c: get_temperature(*cities[c]))
print("가장 따뜻한 곳:", hottest)

# 해 보라
#  1) 다른 도시를 추가해 보라 (광주 58,74 / 대전 67,100 / 제주 52,38)
#  2) get_temperature() 를 부르는 쪽 코드에서 '요청 URL', 'JSON' 이 보이는가?
#     -> Interface(함수 이름·인자) 와 Implementation(HTTP 호출) 의 분리
