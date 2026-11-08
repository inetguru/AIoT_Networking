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

---

## Python으로 API 호출하기 (`python/`)

Postman에서 손으로 하던 호출을 **Python 코드**로 해 본다. 설치할 것은 없다 (컨테이너에 Python과 `requests`가 들어 있다).
실습 준비(Docker Desktop 실행, 이미지 내려받기)는 [`Web_Intro/check.cmd`](../Web_Intro) 로 이미 끝나 있어야 한다.

### 실행 방법

PowerShell에서 `API_Intro` 폴더로 이동한 뒤:

```
.\run.cmd 01_echo_get.py
```

(같은 의미의 원래 명령: `docker compose run --rm py 01_echo_get.py`)  끝나면 `docker compose down` 으로 정리한다.

| 파일 | 내용 | 키 필요 |
|---|---|---|
| `01_echo_get.py` | GET + Query Parameters (Postman Echo) | 없음 |
| `02_echo_post.py` | POST + Header + JSON Body | 없음 |
| `03_weather.py` | 기상청 초단기실황 호출, 응답 JSON에서 기온 꺼내기 | 없음 (모의 서버) / 실제 API는 선택 |
| `04_errors.py` | 실패 다루기: 404, Timeout, 연결 실패, JSON 아님 | 없음 |
| `05_my_function.py` | API 호출을 `get_temperature(nx, ny)` 함수로 감싸기 | 없음 (모의 서버) |
| `06_search_api.py` | (선택) 네이버/카카오 검색, 인증 정보를 Header로 | 네이버/카카오 키 |

각 파일 맨 아래 주석에 **"해 보라"** 과제가 있다. 파일은 메모장이나 VS Code로 열어 고치고, 다시 실행하면 바로 반영된다.

### 실제 API로 바꾸려면 (선택)
기상청 API는 기본적으로 **모의 서버**(`Web_Intro/mock-kma`)를 쓰므로 키가 없어도 된다.
`.env.example` 을 `.env` 로 복사하고 안내대로 키를 넣으면 실제 API로 바뀐다. 키는 코드가 아니라 `.env` 에만 둔다.
