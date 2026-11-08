# Physical_Intro — Physical AI와 네트워킹

AI가 **현실의 기계**를 다루려면 센서와 설비의 말(**Modbus, CAN**)을 알아듣고, 빠른 판단은 **현장(엣지)** 에서, 느린 추론은 **클라우드**에서 하도록 나누어야 한다. 이 폴더에서는 그 구조를 가상 PLC와 가상 CAN 버스로 직접 실행해 본다.

```
센서 ─▶ 필드버스 ─▶ 게이트웨이/미들웨어 ─▶ 엣지 AI ─▶ 클라우드 AI
        Modbus, CAN     MQTT, OPC UA, DDS     빠른 반사     느린 추론
        (값만 오간다)    (의미가 붙는다)     (System 1)    (System 2)
```

> 실제 장비 없이 **가상 PLC**(`plc`)와 **가상 클라우드 AI**(`cloud`, 지연은 시뮬레이션)로 진행한다. 모든 실습은 키 없이 된다.

## 준비
- Docker Desktop 실행, 실습 이미지 준비 (`Web_Intro\check.cmd`)
- (캡처 파일을 열려면) Windows에 Wireshark 설치
- (선택) ROS 2 실습은 공식 `ros` 이미지가 필요하다 (디스크 약 1.3GB). **필수가 아니다**

## 실행 방법
PowerShell에서 `Physical_Intro` 폴더로 이동한 뒤:
```
.\run.cmd 01_modbus_read.py
```
서버들(가상 PLC, 가상 클라우드 AI, **Mosquitto 브로커**)이 **자동으로 함께 시작**된다. PLC 로그는 `docker compose logs plc`. 끝나면 `docker compose down`.

## 실습 순서

| # | 실행 | 배우는 것 |
|---|---|---|
| 1 | `01_modbus_read.py` | **Modbus**: PLC의 레지스터를 읽고 쓴다. 온도 23.5 ℃ 가 `235` 라는 **정수**로 오간다 (의미·단위는 문서에만 있다). 네 종류의 데이터 영역과 기능 코드 |
| 2 | `02_modbus_raw.py` | 요청을 **12 바이트로 직접 만들어** 보낸다 (MBAP 헤더 + 기능 코드). 오류 응답(예외 코드)과 코일 쓰기. 인증·암호화가 **없다** |
| 3 | `03_can_arbitration.py` | **CAN**: 여럿이 동시에 말하면? 비트 단위 **중재**로 ID가 작은(우선순위가 높은) 쪽이 이긴다 |
| 3 | `03_can_bus.py` | 가상 CAN 버스에 노드 셋. 프레임에는 보내는/받는 **주소가 없고**, ID는 '메시지의 종류'. 방송 + 수신 필터 |
| 4 | `04_gateway.py` | **게이트웨이**: Modbus로 읽은 2 바이트에 이름·단위·시각을 붙여 **MQTT/JSON** 으로 내보낸다 |
| 5 | `05_edge_vs_cloud.py` | 같은 이상(온도 급상승)을 **엣지에서 판단**할 때와 **클라우드에서 판단**할 때의 반응 시간·최고 온도·올려 보낸 데이터 비교 |
| 6 | (선택) ROS 2 / DDS | 브로커 없는 Pub/Sub. 노드끼리 **자동으로 서로를 발견**한다 |

### 캡처해서 보기 (tcpdump → Wireshark)
```
.\run.cmd capture.py modbus       captures\live_modbus.pcap   Wireshark 필터: mbtcp
.\run.cmd capture.py gateway      captures\live_gateway.pcap  Wireshark 필터: mbtcp || mqtt
```
Modbus 패킷의 바이트가 2번 실습에서 손으로 만든 12 바이트와 같은지 확인해 보라. MQTT 쪽은 토픽과 JSON이 글자로 보이지만 Modbus 쪽은 숫자뿐이다.

### 5번 실습: 엣지 vs 클라우드
```
.\run.cmd 05_edge_vs_cloud.py                 둘 다 실행해서 비교
.\run.cmd 05_edge_vs_cloud.py edge            엣지만
$env:CLOUD_DELAY_MS = 2000; .\run.cmd 05_edge_vs_cloud.py cloud     클라우드 지연을 2초로 (PowerShell)
```
5초간 평소 감시를 하다가 PLC에 이상(온도가 초당 3 ℃ 상승)을 일으킨다. 감지하면 PLC의 **긴급 냉각 코일**을 쓴다.
- 엣지: 현장 컴퓨터가 읽은 값으로 직접 판단 (기울기 규칙)
- 클라우드: 읽은 값을 **매번** 클라우드 AI로 보내 판단을 받는다 (응답을 기다리는 동안 읽기도 느려진다)
- 클라우드의 지연은 `CLOUD_DELAY_MS`(기본 400 ms)로 **시뮬레이션**한다. 실제 지연은 환경에 따라 다르다.

### 6번 (선택): ROS 2 / DDS
```
docker compose --profile ros up ros-talker ros-listener
```
처음에는 `ros:jazzy-ros-base` 이미지를 내려받는다 (디스크 약 1.3GB). `ros-talker` 가 `factory/temperature` 토픽으로 값을 발행하고, `ros-listener` 가 **브로커 없이** 자동으로 받는다. 끝나면 `docker compose --profile ros down`.

## 알아 두면 좋은 점
- **가상 PLC 의 레지스터**: Input Register 0~1 = 온도(×10), Holding Register 0 = 설정 온도(×10), 10 = 이상 시험, Coil 0 = 히터, 1 = 긴급 냉각, Discrete Input 0 = 과열 경보
- Modbus 포트는 원래 **502** 이지만 실습에서는 **5020** 을 쓴다 (권한 문제 회피)
- `pymodbus` 3.16 은 서버 구성 방식이 예전 예제와 다르다 (`SimDevice`/`SimData`). 인터넷의 예전 예제(`ModbusSlaveContext` 등)는 그대로 동작하지 않는다.
- CAN 은 `python-can` 의 **virtual** 버스(한 프로세스 안의 노드)로 개념만 보여 준다. 실제 CAN 장치나 가상 CAN 인터페이스(SocketCAN)는 WSL2 환경에서 보장되지 않는다.
- 이 실습의 Modbus/MQTT/CAN 에는 **인증·암호화가 없다**. 설비 네트워크를 분리하는 이유다.

## 파일 구성
```
Physical_Intro/
├─ compose.yaml, run.cmd, mosquitto.conf
├─ captures/               캡처 결과 (live_*.pcap)
├─ ros/                    (선택) ROS 2 talker / listener
└─ python/
   ├─ plc_server.py          가상 PLC (Modbus TCP 서버)
   ├─ cloud_server.py        가상 클라우드 AI (지연 시뮬레이션)
   ├─ 01_modbus_read.py  02_modbus_raw.py
   ├─ 03_can_arbitration.py  03_can_bus.py
   ├─ 04_gateway.py  05_edge_vs_cloud.py
   └─ capture.py
```
