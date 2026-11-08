# API_Intro — API란 무엇일까?

Postman으로 HTTP API를 호출해 보며 Black Box, Interface vs. Implementation, API의 이름과 인자를 체감한다.

## Postman Collection (`postman/`)

| 파일 | 내용 | 키 필요 |
|---|---|---|
| `Postman Echo.postman_collection.json` | Postman 공식 테스트 서버. 요청이 어떻게 보이는지 되돌려 줌 | 없음 |
| `공공데이터-기상청-동네예보조회서비스.postman_collection.json` | 기상청 초단기실황/예보 | 공공데이터포털 인증키 |
| `공공데이터-부산버스정보시스템.postman_collection.json` | 부산 버스 정류장·노선·도착 정보 | 공공데이터포털 인증키 |
| `Naver_Kakao Search API.postman_collection.json` | 네이버/카카오 검색 API | 네이버 Client ID/Secret, 카카오 REST API 키 |

사용법: Postman → **Import** → 파일 선택.

## API 키 넣는 방법

저장소의 파일에는 실제 키 대신 `YOUR_SERVICE_KEY`, `YOUR_NAVER_CLIENT_ID`, `YOUR_NAVER_CLIENT_SECRET`,
`YOUR_KAKAO_REST_API_KEY` 가 들어 있다. Import 한 뒤 해당 값을 **본인 키로 바꿔서** 사용한다.

- 공공데이터포털(data.go.kr): 활용신청 후 마이페이지에서 인증키 확인. Postman에는 **일반 인증키(Decoding)** 를 넣는다.
- 네이버/카카오: 각 개발자 센터에서 애플리케이션 등록 후 발급.

> 키는 개인 자격 증명이다. 수정한 Collection을 GitHub 등에 다시 올리지 않는다.
