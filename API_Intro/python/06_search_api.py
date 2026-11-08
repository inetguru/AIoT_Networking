# 실습 6 (선택) : 네이버 / 카카오 검색 API - 인증 정보를 Header 로 전달
#   키가 있어야 실행된다. .env 에 NAVER_ID, NAVER_SECRET, KAKAO_KEY 를 넣는다 (.env.example 참고)
#   공공데이터 API : serviceKey 를 Query Parameter(URL)로 전달  -> 키가 URL에 노출됨
#   네이버/카카오  : 인증 정보를 HTTP Header 로 전달            -> URL에 키가 남지 않음
import os
import requests

query = "스마트 제조"
naver_id, naver_secret = os.environ.get("NAVER_ID"), os.environ.get("NAVER_SECRET")
kakao_key = os.environ.get("KAKAO_KEY")

if naver_id and naver_secret:
    r = requests.get("https://openapi.naver.com/v1/search/webkr.json",
                     params={"query": query},
                     headers={"X-Naver-Client-Id": naver_id, "X-Naver-Client-Secret": naver_secret},
                     timeout=10)
    print("[네이버]", r.status_code)
    for item in r.json().get("items", [])[:3]:
        print(" -", item["title"])
else:
    print("[네이버] NAVER_ID / NAVER_SECRET 이 설정되지 않아 건너뜁니다.")

if kakao_key:
    r = requests.get("https://dapi.kakao.com/v2/search/web",
                     params={"query": query},
                     headers={"Authorization": "KakaoAK " + kakao_key},
                     timeout=10)
    print("[카카오]", r.status_code)
    for doc in r.json().get("documents", [])[:3]:
        print(" -", doc["title"])
else:
    print("[카카오] KAKAO_KEY 가 설정되지 않아 건너뜁니다.")

# 해 보라 : query 를 바꿔 보고, Postman 의 같은 호출(Headers 탭)과 비교해 보라
