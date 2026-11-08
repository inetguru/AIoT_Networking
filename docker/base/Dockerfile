# syntax=docker/dockerfile:1
# AIoT_Networking 공용 실습 이미지 (v2)
#  - Python 3.12 기반 + Node.js 24 + Express + 수업용 Python 라이브러리(버전 고정) + 네트워크 점검 도구
#  - MQTT 브로커(Mosquitto)나 ROS2 같은 서버성 구성요소는 이 이미지에 넣지 않고 공식 이미지를 compose에서 따로 쓴다.

# ---- 1단계: Node.js와 Express 준비 ------------------------------------------
FROM node:24-slim AS node
RUN npm install --prefix /opt/lab-node --no-audit --no-fund express@4.21.2 \
 && rm -rf /root/.npm

# ---- 2단계: 최종 이미지 ------------------------------------------------------
FROM python:3.12-slim

ENV LANG=C.UTF-8 \
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 네트워크 실습용 도구: curl, ping, dig/nslookup, nc, ip/ss, tcpdump, jq
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      curl ca-certificates iputils-ping dnsutils netcat-openbsd iproute2 tcpdump jq procps \
 && rm -rf /var/lib/apt/lists/*

# Node.js (실행 파일만 복사) + 전역 모듈
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /opt/lab-node/node_modules /opt/lab-node/node_modules
ENV NODE_PATH=/opt/lab-node/node_modules

# Python 라이브러리 (requirements.lock.txt 로 버전 고정. 갱신 방법은 docker/README.md)
COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN pip install -r /tmp/requirements.lock.txt && rm /tmp/requirements.lock.txt

LABEL org.opencontainers.image.source="https://github.com/inetguru/AIoT_Networking" \
      org.opencontainers.image.description="AIoT Networking lab image: Python 3.12 + Node.js 24 + course libraries + network tools"

WORKDIR /lab
CMD ["python3", "--version"]
