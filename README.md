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

### Environment Variables

| Name                | Description                                     | Example Value                                                                    | Required |
| ------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------- | -------- |
| API_URL             | chzzk broadcasting category API URL             | https://api.chzzk.naver.com/service/v2/categories/GAME/Tabletop_Simulator/lives? | ✅ true  |
| DISCORD_WEBHOOK_URL | Discord webhook URL for receiving notifications | https://discord.com/api/webhooks/your-webhook-id/your-webhook-token              | ✅ true  |
| CUSTOM_USER_AGENT   | Optional: Custom user agent for troubleshooting | PostmanRuntime/7.37.3                                                            | ❌ false |

## Usage

### Docker Run

```bash
docker run -d --name chzzk-noti-bot \
  -e API_URL='your_api_url_here' \
  -e DISCORD_WEBHOOK_URL='your_discord_webhook_url_here' \
  --restart always onevl/chzzk-noti-bot
```

### docker-compose.yml

```yaml
services:
  chzzk-noti-bot:
    image: onevl/chzzk-noti-bot
    container_name: chzzk-noti-bot
    environment:
      - API_URL=https://api.chzzk.naver.com/service/v2/categories/GAME/Tabletop_Simulator/lives?
      - DISCORD_WEBHOOK_URL=디스코드 웹훅 url
      # - CUSTOM_USER_AGENT=PostmanRuntime/7.37.3 (Optional)
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

### 환경변수

| 이름                | 설명                                              | 예시                                                                             | 필수    |
| ------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------- | ------- |
| API_URL             | 치지직 방송 카테고리 API URL                      | https://api.chzzk.naver.com/service/v2/categories/GAME/Tabletop_Simulator/lives? | ✅ 필수 |
| DISCORD_WEBHOOK_URL | 알림을 수신할 디스코드 웹훅 url                   | https://discord.com/api/webhooks/your-webhook-id/your-webhook-token              | ✅ 필수 |
| CUSTOM_USER_AGENT   | (선택) 문제 발생시 사용할 커스텀 유저 에이전트 값 | PostmanRuntime/7.37.3                                                            | ❌ 선택 |

## 사용법

### Docker Run

```bash
docker run -d --name chzzk-noti-bot \
  -e API_URL='원하시는 api_url을 넣어주세요' \
  -e DISCORD_WEBHOOK_URL='디스코드에서 생성한 웹 훅 url을 넣어주세요' \
  --restart always onevl/chzzk-noti-bot
```

### docker-compose.yml

```yaml
services:
  chzzk-noti-bot:
    image: onevl/chzzk-noti-bot
    container_name: chzzk-noti-bot
    environment:
      - API_URL=https://api.chzzk.naver.com/service/v2/categories/GAME/Tabletop_Simulator/lives?
      - DISCORD_WEBHOOK_URL=디스코드 웹훅 url
      # - CUSTOM_USER_AGENT=PostmanRuntime/7.37.3 (Optional)
    restart: always
```
