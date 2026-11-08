# Gemini API 접근 점검

대학 계정(Google Workspace for Education)으로 **학생이 Gemini API를 수업에서 쓸 수 있는지** 확인하는 도구.
(주제 6 "AI Model과 소통하기"의 실습 가능 여부 판단용)

## 확인하는 것
| 단계 | 확인 내용 |
|---|---|
| 1 | API 키가 유효하고 사용 가능한 모델 목록이 보이는가 |
| 2 | 글 생성(`generateContent`)이 되는가 |
| 3 | **함수 호출(Tool Calling)** 이 되는가 — `get_temperature` 를 AI에게 알려 주고 호출을 요청하는지 |
| 4 | 스트리밍(SSE)으로 답이 조금씩 도착하는가 |

## 실행 순서
1. 대학 Google 계정으로 로그인한 상태에서 https://aistudio.google.com/apikey 접속 → **API 키 만들기**
   - "접근 권한이 없습니다" 류의 메시지가 나오면 그 문구를 그대로 기록해 둔다 (관리자 설정 또는 나이 제한)
2. `.env.example` 을 `.env` 로 복사하고 `GEMINI_API_KEY=` 뒤에 키를 붙여 넣는다
3. 이 폴더에서 PowerShell로 `.\run.cmd` 실행 (Docker Desktop 실행 중, `Web_Intro\check.cmd` 로 이미지 준비된 상태)

## 결과 읽는 법
- 마지막 "결과 요약"에 단계별 `[OK]` / `[FAIL]` 이 나온다.
- 실패하면 HTTP 상태 코드와 원인 안내가 함께 출력된다 (400 키 오류, 403 권한/정책, 429 한도 초과 등).
- 키 값은 화면에 출력하지 않는다.
