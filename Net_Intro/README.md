# Net_Intro — 네트워크 프로그래밍의 이해 (I)

같은 네트워크에 놓인 컨테이너들 사이에서 **통신을 직접 만들고, `tcpdump`로 캡처해서 Wireshark로 들여다본다.**
주소(MAC · IP · Port · 이름), HTTP가 글자라는 것, TCP와 UDP의 차이, Unicast와 Multicast, HTTP와 HTTPS의 차이를 **내가 만든 패킷**으로 확인한다.

> 미리 녹화된 캡처 파일(`HTTP_Intro/captures`)을 분석하는 실습도 함께 쓸 수 있다. 이 폴더는 **직접 캡처**하는 실습이다.

## 준비
- Docker Desktop 실행, 실습 이미지 준비 (`Web_Intro\check.cmd` 로 이미 끝나 있어야 한다)
- Windows에 **Wireshark** 설치 (캡처 파일을 여는 용도)

## 실행 방법
PowerShell에서 `Net_Intro` 폴더로 이동한 뒤:
```
.\run.cmd 01_network_tour.py
```
서버들(web, tls, tcp-server, udp-server, multicast 수신자 2개)은 **자동으로 함께 시작**된다.
서버가 무엇을 받았는지는 `docker compose logs tcp-server` 처럼 본다. 끝나면 `docker compose down`.

## 실습 순서

| # | 실행 | 배우는 것 |
|---|---|---|
| 1 | `.\run.cmd 01_network_tour.py` | **주소들**: 내 MAC · IP, 이름(DNS) → IP, 내 쪽 Port와 서버 쪽 Port, 서버의 MAC |
| 2 | `.\run.cmd 02_raw_http.py` | **HTTP는 글자**다: 라이브러리 없이 소켓으로 요청을 직접 써서 보낸다 |
| 3 | `.\run.cmd 03_tcp_client.py` | **TCP**: `send` 3번 → 서버의 `recv`는 몇 번? (Stream). 아무도 없는 포트: `--port 9999` |
| 4 | `.\run.cmd 04_udp_client.py` | **UDP**: 데이터그램 3개가 따로 도착(경계 보존). 아무도 없는 포트: `--port 9999` |
| 5 | `.\run.cmd 05_mcast_sender.py` | **Multicast**: 한 번 보내면 그룹에 가입한 수신자 모두가 받는다 |

3~5번은 보낸 뒤 서버 쪽 로그를 꼭 본다.
```
docker compose logs tcp-server
docker compose logs udp-server
docker compose logs mcast-rx1 mcast-rx2
```

## 직접 캡처하기 (tcpdump)

```
.\run.cmd capture.py http
```
`tcpdump`가 컨테이너의 네트워크 인터페이스를 엿듣는 동안 통신이 일어나고, 결과가 `captures\live_http.pcap` 으로 저장된다.
화면에도 패킷 목록(시각, **MAC**, **IP.Port**, TCP 플래그)과 "본문 글자를 찾았는가"가 출력된다.

| 시나리오 | 명령 | 무엇을 볼 것인가 |
|---|---|---|
| HTTP | `capture.py http` | ARP(MAC 알아내기) → **TCP 3-way handshake** → 요청/응답 → 연결 종료. **센서 값(JSON)이 글자 그대로 보인다** |
| HTTPS | `capture.py https` | TLS handshake 후 **본문이 보이지 않는다** (암호화). TLS 버전과 서버 이름(SNI)은 보인다 |
| TCP | `capture.py tcp` | SYN/SYN-ACK/ACK, 데이터, FIN. 보낸 3번이 몇 개 패킷인가? |
| UDP | `capture.py udp` | handshake 없이 데이터그램 3개만 |
| Multicast | `capture.py multicast` | 목적지 IP `224.1.1.1`, 목적지 MAC `01:00:5e:...` |

### Wireshark로 열기
`Net_Intro\captures\live_http.pcap` 등을 **더블클릭**하거나 Wireshark의 File → Open. 표시 필터 예:
- `http`, `tcp.flags.syn == 1`, `tls`, `udp`, `ip.dst == 224.1.1.1`
- 패킷 우클릭 → **Follow → TCP Stream**: 주고받은 글자를 한눈에 본다

### 해 보라
1. `capture.py http` 의 결과에서 **MAC 주소**가 바뀌는 지점은 어디인가? IP 주소와 Port 는 요청과 응답에서 어떻게 뒤바뀌는가?
2. 같은 센서 값을 `http` 와 `https` 로 캡처해 비교하라. 어느 쪽에서 값이 보이는가?
3. `tcp` 와 `udp` 캡처에서 패킷 수가 다른 이유는? `udp` 에는 어떤 패킷이 **없는가**?
4. `multicast` 캡처의 목적지 MAC 이 왜 `01:00:5e:01:01:01` 일까? (힌트: 224.1.1.1 의 뒤 3바이트)
5. 이 폴더의 캡처와 `HTTP_Intro\captures\Curltest_http_cse.pcapng` (실제 인터넷 서버)를 비교하라. 무엇이 같고 무엇이 다른가?

## 알아 두면 좋은 점
- 컨테이너 네트워크에서는 **ARP 줄이 중복**되어 보이거나, 마지막에 자기 주소를 알리는 ARP 가 보일 수 있다. 정상이다.
- 캡처는 컨테이너 안(`eth0`)에서 한다. Windows PC의 인터넷 통신을 캡처하려면 Windows의 Wireshark로 직접 한다.
- `captures\*.pcap` 파일은 Git에 올라가지 않는다. 필요 없으면 지워도 된다.

## 파일 구성
```
Net_Intro/
├─ compose.yaml, run.cmd
├─ captures/            캡처 결과(.pcap)가 저장되는 곳
└─ python/
   ├─ 01_network_tour.py   02_raw_http.py
   ├─ 03_tcp_server.py / 03_tcp_client.py
   ├─ 04_udp_server.py / 04_udp_client.py
   ├─ 05_mcast_receiver.py / 05_mcast_sender.py
   ├─ tls_server.py        (HTTPS 서버, 자체 서명 인증서)
   └─ capture.py           (tcpdump 캡처 도구)
```
