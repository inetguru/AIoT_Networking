# AIoT_Networking 공용 실습 이미지
# - Node.js LTS + Express(전역 설치) + curl + Python3
# - 학생은 npm init / npm install 을 하지 않아도 require('express') 가 바로 동작한다.
FROM node:24-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates python3 \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g express@4.21.2 \
 && npm cache clean --force

# 전역 설치한 모듈을 어느 폴더의 코드에서든 require 할 수 있게 한다.
ENV NODE_PATH=/usr/local/lib/node_modules

LABEL org.opencontainers.image.source="https://github.com/inetguru/AIoT_Networking" \
      org.opencontainers.image.description="AIoT Networking lab image (Node.js + Express + Python3)"

WORKDIR /lab
USER node
CMD ["node", "--version"]
