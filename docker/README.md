# docker/ — 실습 이미지

모든 실습이 공유하는 **하나의 기본 이미지**를 만든다.

```
ghcr.io/inetguru/aiot-lab:v2        (latest 도 같은 이미지)
```

| 폴더 | 내용 |
|---|---|
| `base/` | **현재 이미지.** `Dockerfile`, `requirements.txt`(라이브러리 목록), `requirements.lock.txt`(고정된 버전) |
| `legacy-node24/` | 이전 이미지(`aiot-lab:node24`)의 Dockerfile. 더 이상 빌드하지 않고 참고용으로만 보관 |

## 이미지에 들어 있는 것

| 구분 | 내용 | 쓰이는 곳 |
|---|---|---|
| 언어 | Python 3.12, Node.js 24 (+ Express 4.21.2) | 전 주제 |
| Python 라이브러리 | `requests`, `paho-mqtt`, `pymodbus`, `asyncua`, `mcp`, `websockets`, `python-can` (버전은 lock 파일) | HTTP API, MQTT, Modbus, OPC UA, MCP, WebSocket, CAN |
| 네트워크 도구 | `curl`, `ping`, `dig`/`nslookup`, `nc`, `ip`/`ss`, `tcpdump`, `jq` | 네트워크 실습, 패킷 캡처 |

**이미지에 넣지 않은 것**: MQTT 브로커(Mosquitto), ROS2 같은 서버성 구성요소는 각 실습의 `compose.yaml`에서 **공식 이미지**를 따로 쓴다. 모의 서버(`mock-kma` 등)는 코드만 폴더에 있고 이 이미지로 실행한다.

## 설계 원칙
- **이미지에는 도구만, 코드는 넣지 않는다.** 실습 코드는 학생 PC의 폴더를 컨테이너에 연결(bind mount)해서 쓰므로, 코드를 고쳐도 이미지를 다시 받지 않는다.
- 컨테이너는 root로 실행한다 (`tcpdump` 패킷 캡처에 필요). 실습 전용 컨테이너라 격리 수준은 충분하다.
- 라이브러리 버전은 **lock 파일로 고정**해 수업 날 갑자기 동작이 달라지지 않게 한다.

## 라이브러리를 추가하거나 버전을 올릴 때
1. `base/requirements.txt` 에 패키지를 추가한다.
2. lock 파일을 다시 만든다 (같은 Python 버전으로):
   ```
   docker run --rm -v "<이 폴더의 절대경로>/base:/req" python:3.12-slim sh -c "pip install -q -r /req/requirements.txt && pip freeze" > base/requirements.lock.txt
   ```
   (출력 앞에 pip 안내문이 섞이지 않았는지 확인한다)
3. `docker build -t ghcr.io/inetguru/aiot-lab:v2 docker/base` 로 로컬에서 확인한다.
4. push 하면 GitHub Actions가 amd64/arm64 이미지를 빌드해 GHCR에 올린다 (`docker/**` 변경 시 자동. 첫 push는 `Run workflow`로 수동 실행).

## 로컬에서 직접 확인
```
docker build -t ghcr.io/inetguru/aiot-lab:v2 docker/base
docker run --rm ghcr.io/inetguru/aiot-lab:v2 python3 -c "import requests, paho.mqtt.client, asyncua; print('ok')"
```
