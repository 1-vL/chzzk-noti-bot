# chzzk-noti-bot

[![GitHub last commit](https://img.shields.io/github/last-commit/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2F1-vL%2Fchzzk-noti-bot%2Fhit-counter&count_bg=%2344cc11&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/1-vL/chzzk-noti-bot)
[![GitHub issues](https://img.shields.io/github/issues/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/issues)
[![GitHub stars](https://img.shields.io/github/stars/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/network)
[![Docker Hub Version](https://img.shields.io/docker/v/onevl/chzzk-noti-bot?label=docker%20hub%20version)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![DockerHub](https://img.shields.io/docker/pulls/onevl/chzzk-noti-bot)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This bot provides notifications based on 치지직 (Chzzk) broadcast categories via Discord webhooks.

## Usage

### Docker Run

```bash
docker run -d --name chzzk-noti-bot \
  -p 34224:34224 \
  --restart always onevl/chzzk-noti-bot
```

### docker-compose.yml

```yaml
services:
  chzzk-noti-bot:
    image: onevl/chzzk-noti-bot
    container_name: chzzk-noti-bot
    ports: -34224:34224
    restart: always
```

# 치지직 카테고리 알림 봇 chzzk-noti-bot

[![GitHub last commit](https://img.shields.io/github/last-commit/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2F1-vL%2Fchzzk-noti-bot%2Fhit-counter&count_bg=%2344cc11&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/1-vL/chzzk-noti-bot)
[![GitHub issues](https://img.shields.io/github/issues/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/issues)
[![GitHub stars](https://img.shields.io/github/stars/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/network)
[![Docker Hub Version](https://img.shields.io/docker/v/onevl/chzzk-noti-bot?label=docker%20hub%20version)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![DockerHub](https://img.shields.io/docker/pulls/onevl/chzzk-noti-bot)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

이 봇은 지정한 치지직 방송 카테고리에서 방송이 시작되면 해당 방송의 정보를 디스코드 알림으로 알리는 봇입니다.

도커를 통해 설치하여 사용하시면 됩니다.

## 사용법

### Docker Run

```bash
docker run -d --name chzzk-noti-bot \
  -p 34224:34224 \
  --restart always onevl/chzzk-noti-bot
```

### docker-compose.yml

```yaml
services:
  chzzk-noti-bot:
    image: onevl/chzzk-noti-bot
    container_name: chzzk-noti-bot
    ports: -34224:34224
    restart: always
```
