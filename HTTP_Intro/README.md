# HTTP_Intro — HTTP의 이해

Wireshark로 패킷을 열어 보며 계층 구조(HTTP–TCP–IP), TCP 3-way handshake, HTTP와 HTTPS의 차이를 관찰한다.

## 캡처 파일 (`captures/`)

| 파일 | 패킷 수 | 내용 |
|---|---|---|
| `Curltest_http_cse.pcapng` | 9 | `curl`로 HTTP 요청. 요청·응답이 평문으로 보임 |
| `Curltest_https_cse.pcapng` | 91 | `curl`로 HTTPS 요청. TLS 1.3 핸드셰이크 이후 암호화됨 |
| `Browser_https_cse.pcapng` | 271 | 브라우저로 HTTPS 접속. TCP 연결이 여러 개 생성됨 |

공통: 클라이언트 `192.168.0.37` ↔ 서버 `164.125.8.25` (cse.pusan.ac.kr)

## 사용법
1. [Wireshark](https://www.wireshark.org/) 설치 후 파일을 연다.
2. 표시 필터 예: `tcp.flags.syn == 1` (연결 시작), `http`, `tls.handshake`
3. 세 파일에서 같은 서버와의 통신이 **어떻게 다르게 보이는지** 비교해 보라.

## 직접 캡처해 보기
녹화된 파일 대신 **내가 일으킨 통신을 `tcpdump`로 직접 캡처**하는 실습은 [`../Net_Intro`](../Net_Intro) 에 있다.
