# Net2_Intro — 네트워크 프로그래밍의 이해 (II)

서버가 **여러 클라이언트를 어떻게 처리하는지**, 연결이 **어떤 방식으로 발전했는지**, 그리고 센서 값을 **누구에게 어떻게 전달하는지**(Polling → Push → Publish/Subscribe)를 직접 실행해 비교한다.
같은 방식으로 `tcpdump` 캡처도 할 수 있어서, 눈에 보이는 결과와 패킷을 함께 확인한다. (앞 단계 실습은 [`../Net_Intro`](../Net_Intro))

## 준비
- Docker Desktop 실행, 실습 이미지 준비 (`Web_Intro\check.cmd`)
- (캡처 파일을 열려면) Windows에 Wireshark 설치

## 실행 방법
PowerShell에서 `Net2_Intro` 폴더로 이동한 뒤:
```
.\run.cmd 01_load_client.py
```
서버들(blocking/threaded/async 서버, 챗봇, 센서, 웹, **Mosquitto 브로커**, OPC UA)이 **자동으로 함께 시작**된다. 처음에는 몇 초 걸린다.
서버 로그는 `docker compose logs <서비스 이름>` 으로 본다. 끝나면 `docker compose down`.

서비스 이름: `srv-blocking`, `srv-threaded`, `srv-async`, `chat`, `sensor`, `web`, `mosquitto`, `opcua`

## 실습 순서

### 1. 서버는 여러 손님을 어떻게 받을까? (Blocking vs Non-Blocking)
| 실행 | 확인할 것 |
|---|---|
| `.\run.cmd 01_load_client.py` | 손님 10명이 **동시에** 몰려오면, 기다리는 일(IO)을 세 서버가 얼마나 걸려 처리하는가 |
| `.\run.cmd 01_load_client.py --work cpu` | **계산하는 일**은? 결과가 왜 비슷해지는가 |

- `blocking`은 한 번에 한 명, `threaded`는 손님마다 스레드, `async`는 **한 흐름이 기다리는 동안 다른 손님을 돌본다**.
- 서버 로그: `docker compose logs srv-blocking`

### 2. 서버는 기억해야 할까? (Stateless vs Stateful)
| 실행 | 확인할 것 |
|---|---|
| `.\run.cmd 02_chat_client.py` | 기억하지 않는 서버에 **대화 전체를 매번** 보내야 하는 이유(LLM API 방식), 서버가 재시작되면 Stateful은 어떻게 되는가 |

### 3. 변화를 어떻게 알려 줄까? (Polling · SSE · WebSocket)
센서 값이 2초마다 바뀐다.

| 실행 | 방식 | 확인할 것 |
|---|---|---|
| `.\run.cmd 03_poll_client.py` | **Polling** (계속 묻는다) | 요청 20번 중 새 값은 몇 번? 지연은? |
| `.\run.cmd 03_sse_client.py` | **SSE** (HTTP 연결을 열어 두고 서버가 밀어 준다) | HTTP 요청은 몇 번? 지연은? |
| `.\run.cmd 03_ws_client.py` | **WebSocket** (양방향 연결 유지) | 반대 방향(클라이언트→서버)도 보낼 수 있다 |
| `.\run.cmd 04_keepalive.py` | **HTTP/1.1 Keep-Alive** | 요청 5번에 TCP 연결이 5번 vs 1번 (tcpdump로 센다) |

### 4. 보내는 쪽과 받는 쪽을 분리하자 (MQTT, Publish/Subscribe)
브로커(Mosquitto) 하나가 중간에서 전달한다. **Publisher는 누가 받는지 모른다.**

| 실행 | 확인할 것 |
|---|---|
| `.\run.cmd 05_publisher.py` | 토픽 `factory/line1/temp01/temperature` 로 값 발행 (`--qos 0/1/2`, `--retain`) |
| `.\run.cmd 05_subscriber.py` | **다른 PowerShell 창**에서 먼저 실행해 두면 값이 도착한다. 토픽 필터: `"factory/line1/+/temperature"`, `"factory/#"` |
| `.\run.cmd 05_retain_demo.py` | **Retained**: 늦게 접속한 구독자도 마지막 값을 바로 받는다 |
| `.\run.cmd 05_lwt_demo.py` | **Last Will**: 센서가 갑자기 죽으면 브로커가 대신 `offline` 을 알린다 |

> 두 창을 쓰는 방법: 창 1에서 `.\run.cmd 05_subscriber.py --seconds 60`, 창 2에서 `.\run.cmd 05_publisher.py`.
> 브로커 로그는 `docker compose logs mosquitto` (연결과 구독이 기록된다).

### 5. 공장 설비의 표준 (OPC UA)
| 실행 | 확인할 것 |
|---|---|
| `.\run.cmd 06_opcua_client.py` | **Browse**(서버가 가진 것을 트리로 탐색), **Read**, **Write**, 쓰기 불가 변수에 쓰면 거부 |
| `.\run.cmd 06_opcua_subscribe.py` | **Subscription**: 값이 바뀔 때 서버가 알려 준다 |

MQTT의 토픽(`factory/line1/temp01/temperature`)과 OPC UA의 주소 공간(`Factory/Line1/Temp01/Temperature`)을 비교해 보라.

## 직접 캡처하기 (tcpdump)
```
.\run.cmd capture.py mqtt
```
결과는 `captures\live_mqtt.pcap` 에 저장된다. Windows에서 **Wireshark로 열어** 본다.

| 시나리오 | 무엇을 볼 것인가 |
|---|---|
| `mqtt` | CONNECT, SUBSCRIBE, **PUBLISH** — 토픽과 값이 **글자 그대로** 보인다 (MQTT는 기본이 암호화 없음) |
| `sse` | HTTP 응답 헤더 `text/event-stream` 뒤로 `data: {...}` 가 **끊기지 않고** 이어진다 |
| `ws` | HTTP 요청에 `Upgrade: websocket`, 응답 `101 Switching Protocols` → 이후 WebSocket 프레임 |
| `opcua` | 글자가 아닌 **바이너리**. `HEL → ACK → OPN → MSG … → CLO` |

Wireshark 표시 필터: `mqtt`, `mqtt.msgtype == 3`, `websocket`, `opcua`, `tcp.port == 1883`

## 알아 두면 좋은 점
- `requests` 로 SSE를 읽을 때는 `iter_lines(chunk_size=1)` 이 필요하다. 기본값(512바이트)이면 작은 이벤트가 한참 뒤에야 보인다. (LLM의 스트리밍 응답을 읽을 때도 같다)
- OPC UA 서버는 주소 `opc.tcp://opcua:4840/factory/` 로 접속한다. 컨테이너 안에서는 서비스 이름(`opcua`)이 주소다.
- 브로커 설정은 `mosquitto.conf` (인증 없음, 실습 전용). 실제 설비에서는 **인증과 TLS를 켜야 한다**.
- `captures\*.pcap` 파일은 Git에 올라가지 않는다.

## 파일 구성
```
Net2_Intro/
├─ compose.yaml, run.cmd, mosquitto.conf
├─ captures/                캡처 결과(.pcap)
└─ python/
   ├─ 01_servers.py, 01_load_client.py        (blocking / threaded / async)
   ├─ 02_chat_server.py, 02_chat_client.py    (Stateless / Stateful)
   ├─ 03_sensor_server.py                     (HTTP polling, SSE, WebSocket 서버)
   ├─ 03_poll_client.py, 03_sse_client.py, 03_ws_client.py
   ├─ 04_keepalive.py
   ├─ 05_publisher.py, 05_subscriber.py, 05_retain_demo.py, 05_lwt_demo.py   (MQTT)
   ├─ 06_opcua_server.py, 06_opcua_client.py, 06_opcua_subscribe.py          (OPC UA)
   └─ capture.py                              (tcpdump 캡처 도구)
```
