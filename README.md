# AIoT_Networking

부산대학교 정보컴퓨터공학부 김종덕 — **사물인터넷 플랫폼과 디바이스** (재직자 석사 과정) 실습 자료 저장소.

AI Agent와 AIoT 시대의 **네트워킹 구조와 기술 변화의 방향**을 간단한 실습으로 체감하는 것을 목표로 한다.
주제별 폴더에 실습 자료가 들어 있고, 모든 실습은 같은 Docker 이미지 위에서 동작한다.

## 폴더 구성

| 폴더 | 주제 | 상태 |
|---|---|---|
| [`API_Intro/`](API_Intro) | API란 무엇일까? (Postman 실습) | **사용 가능** |
| [`HTTP_Intro/`](HTTP_Intro) | HTTP의 이해 (패킷 캡처 실습) | **사용 가능** |
| [`Net_Intro/`](Net_Intro) | 네트워크 프로그래밍 (I): 직접 캡처(tcpdump), 소켓, TCP/UDP, Multicast | **사용 가능** |
| [`Net2_Intro/`](Net2_Intro) | 네트워크 프로그래밍 (II): Blocking vs Non-Blocking, Stateless/Stateful, SSE·WebSocket, MQTT, OPC UA | **사용 가능** |
| [`AI_Intro/`](AI_Intro) | 인공지능과 네트워크 프로그래밍: LLM API, Tool Calling, Agent, MCP, A2A (키 없이도 동작) | **사용 가능** |
| [`docs/industrial-iot/`](docs/industrial-iot/index.html) | **보조 문서**: 제조 현장의 디바이스와 네트워킹, OPC UA 배경 (HTML) | **사용 가능** |
| [`Web_Intro/`](Web_Intro) | HTTP와 Web Programming (Node.js/Express, AJAX, CORS) | **사용 가능** |
| [`docker/`](docker) | 모든 실습이 공유하는 이미지 (Node.js + Express + Python3) | 사용 가능 |

주제가 늘어나면 `<주제>_Intro/` 형태로 폴더를 추가한다. 각 폴더는 자체 `README.md`를 가진다.

## 시작하기

1. WSL2 + Docker Desktop 설치 (수업 시간에 안내한 사전 준비 자료 참고)
2. 이 저장소를 내려받는다: **Code → Download ZIP** 후 `C:\iot-lab` 같은 짧은 영문 경로에 압축 해제
   (한글·OneDrive 경로는 피한다)
3. 실습할 주제 폴더의 `README.md`를 따라 한다. 예: [`Web_Intro/README.md`](Web_Intro/README.md)

## 실습 이미지

```
ghcr.io/inetguru/aiot-lab:v2
```

`docker/Dockerfile`이 바뀌면 GitHub Actions가 amd64/arm64용으로 자동 빌드하여 GHCR에 올린다.
