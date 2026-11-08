# Web_Intro — HTTP와 Web Programming

Node.js(Express) 웹 서버를 만들어 보고, 브라우저에서 Open API를 호출할 때 왜 **CORS 오류**가 나는지,
그리고 **서버가 대신 호출**하면 어떻게 해결되는지 체험한다.
설치할 것은 없다. **Docker 컨테이너에 Node.js와 Express가 이미 들어 있다.**

## 준비 (수업 전날까지)

1. Docker Desktop을 실행하고 좌측 하단이 **Engine running** 인지 확인한다.
2. 이 폴더(`Web_Intro`)에서 PowerShell을 열고 아래를 실행한다.

   ```
   powershell -ExecutionPolicy Bypass -File .\check.ps1
   ```

   모두 `[OK]` 가 나오면 준비 끝. (실습 이미지를 미리 내려받는 작업 포함)

## 실습 방법

PowerShell에서 `Web_Intro` 폴더로 이동한 뒤, **한 번에 하나의 step만** 실행한다.
멈출 때는 `Ctrl + C`.

| 명령 | 슬라이드 | 브라우저에서 열 주소 | 해 볼 일 |
|---|---|---|---|
| `docker compose up step0` | Step-0 | http://localhost:3000/ | Hello World 확인 |
| `docker compose up step1` | Step-1 | http://localhost:3000/Path1, /Path2 | Routing. PUT/POST는 Postman으로 |
| `docker compose up step2` | Step-2 ~ 4 | http://localhost:3000/first.html, /second.html, /third.html | 정적 파일, 그리고 **third.html의 CORS 오류** (F12 → Console) |
| `docker compose up step3` | Step-5 ~ 6 | http://localhost:3000/webapi, /fourth.html | 서버가 대신 호출 → 성공 |

코드는 `lab` 폴더에 있다. 메모장이나 VS Code로 열어 고친 뒤, `Ctrl + C` → 같은 명령 재실행.

### 관찰 포인트
- `third.html`을 눌러 CORS 오류가 난 직후, 터미널의 `mock-kma` 로그를 보라.
  **서버는 요청을 받았고 응답도 했다.** 막은 것은 누구일까?
- `third.html`과 `fourth.html`의 차이를 설명해 보라 (F12 → Network 탭).

### 끝내기 / 정리
```
docker compose down
```

## 실제 기상청 API로 바꾸려면 (선택)

기본 설정은 모의 서버(`mock-kma`)라서 키가 없어도 된다.
공공데이터포털 키가 있다면 `.env.example` 을 `.env` 로 복사하고 안내대로 두 줄을 수정한다.

## 문제가 생기면

| 증상 | 확인 |
|---|---|
| `docker` 명령을 찾을 수 없음 / 연결 오류 | Docker Desktop이 실행 중인가? |
| `port is already allocated` | 이전 step이 아직 실행 중. `docker compose down` 후 다시 |
| 이미지 내려받기 실패 | 네트워크 확인. 강사가 준 tar 파일이 있으면 `docker load -i aiot-lab.tar` |
| 파일 수정이 반영되지 않음 | `Ctrl + C` 후 다시 `up` (자동 재시작 없음) |
