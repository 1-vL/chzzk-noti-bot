# 치지직 카테고리 알림 봇 chzzk-noti-bot

[![GitHub last commit](https://img.shields.io/github/last-commit/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot)
![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=1-vL.chzzk-noti-bot)
[![GitHub issues](https://img.shields.io/github/issues/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/issues)
[![GitHub stars](https://img.shields.io/github/stars/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/network)
[![Docker Hub Version](https://img.shields.io/docker/v/onevl/chzzk-noti-bot?label=docker%20hub%20version)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![DockerHub](https://img.shields.io/docker/pulls/onevl/chzzk-noti-bot)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/M4M510DV50)

이 봇은 지정한 치지직 방송 카테고리에서 방송이 시작되면 해당 방송의 정보를 디스코드 알림으로 알리는 봇입니다.

도커를 통해 설치하여 사용하시면 됩니다.

<br>

![main](https://i.imgur.com/YkW5X7N.png)

![discord-result](https://i.imgur.com/a7N0T2Z.png)

# 사용법

## 설치

### (선택) 바인드할 폴더 접근권한 부여

![pre-install-1](https://i.imgur.com/TvzhQlA.png)

설정 파일을 저장할 `data` 폴더와 로그 파일을 저장할 `logs` 폴더를 호스트 시스템의 원하는 위치에서

```sh
sudo mkdir chzzk && sudo mkdir chzzk/data chzzk/logs
```

또는

```sh
mkdir chzzk
cd chzzk
mkdir data logs
```

등의 방법으로 생성합니다.

![pre-install-2](https://i.imgur.com/XGzWrn5.png)

생성한 폴더에 도커에서 접근 가능하도록 `nobody:nogroup` 접근 권한을 부여합니다.

```sh
sudo chown -R nobody:nogroup chzzk
```

![pre-install-3](https://i.imgur.com/aoSqEMn.png)

성공적으로 접근 권한이 부여되었습니다.

### Docker Run

```bash
docker run -d \
  --name chzzk-noti-bot \
  -p 34224:34224 \ # host:container 80:34224
  # -e TZ=Asia/Seoul \ # 선택사항, 기본: Asia/Seoul
  -v /root/docker/volumes/chzzk/data:/app/data \ # 선택사항, config.json 설정파일을 저장할 경로
  -v /root/docker/volumes/chzzk/logs:/app/logs \ # 선택사항, 로그 파일을 저장할 경로
  --restart always \ # 재시작 옵션
  onevl/chzzk-noti-bot # latest 도커 이미지 사용
```

### docker-compose.yml

```yaml
services:
  chzzk-noti-bot-tts:
    image: onevl/chzzk-noti-bot
    container_name: chzzk-noti-bot
    ports:
      - "34224:34224"
    # environment:
    #   - TZ=Asia/Seoul # 선택사항, 기본: Asia/Seoul
    volumes:
      - /root/docker/volumes/chzzk/data:/app/data # 선택사항, config.json 설정파일을 저장할 경로
      - /root/docker/volumes/chzzk/logs:/app/logs # 선택사항, 로그 파일을 저장할 경로
    restart: always
```

## 디스코드 웹훅 생성

![discord-webhook-1](https://i.imgur.com/DoHpXPz.png)

알림을 수신하고자 하는 채널의 설정으로 들어갑니다.

![discord-webhook-2](https://i.imgur.com/kd1wFu8.png)

연동 탭의 웹후크로 이동합니다.

![discord-webhook-3](https://i.imgur.com/yYgbrr9.png)

새 웹후크를 생성하고, 관리페이지에서 등록 가능하도록 URL을 복사합니다.

## 카테고리 등록 및 수정

![init](https://i.imgur.com/w9VqjBI.png)

도커 설치 이후 초기 상태입니다.

예제로 사용될 알림이 2개 작성되어 있으며, 디스코드 웹훅 URL이 올바르지 않으므로 실제 알림이 발송되지는 않습니다.

![modify-add](https://i.imgur.com/5LZnpzF.png)

디스코드 웹훅 URL을 입력하는 칸에 복사해온 URL을 입력합니다.

![category](https://i.imgur.com/J5NLXUN.png)

API URL 칸에는 치지직 공식 사이트에서 확인한 카테고리 정보를 가진 API 주소의 URL을 입력합니다.

```HTML
  https://api.chzzk.naver.com/service/v2/categories/(카테고리 타입)/(카테고리)/lives
  ex: https://api.chzzk.naver.com/service/v2/categories/GAME/Tabletop_Simulator/lives
```

## 전역 기본 설정

![global](https://i.imgur.com/Y7gz2wc.png)

새로운 알림을 생성하는 경우 기본으로 적용될 속성들을 관리하는 페이지입니다.

<br>
<br>
<hr>
<br>
<br>

# chzzk-noti-bot

[![GitHub last commit](https://img.shields.io/github/last-commit/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot)
![Visitor Count](https://visitor-badge.laobi.icu/badge?page_id=1-vL.chzzk-noti-bot)
[![GitHub issues](https://img.shields.io/github/issues/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/issues)
[![GitHub stars](https://img.shields.io/github/stars/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/1-vL/chzzk-noti-bot)](https://github.com/1-vL/chzzk-noti-bot/network)
[![Docker Hub Version](https://img.shields.io/docker/v/onevl/chzzk-noti-bot?label=docker%20hub%20version)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![DockerHub](https://img.shields.io/docker/pulls/onevl/chzzk-noti-bot)](https://hub.docker.com/r/onevl/chzzk-noti-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/M4M510DV50)

This bot provides notifications based on 치지직 (Chzzk) broadcast categories via Discord webhooks.

<br>

![main](https://i.imgur.com/YkW5X7N.png)

![discord-result](https://i.imgur.com/a7N0T2Z.png)

# Usage

## Installation

### (Optional) Grant Access Permissions to the Bind Folder

![pre-install-1](https://i.imgur.com/TvzhQlA.png)

```sh
sudo mkdir chzzk && sudo mkdir chzzk/data chzzk/logs
```

Or

```sh
mkdir chzzk
cd chzzk
mkdir data logs
```

Create the `data` folder for configuration files and the `logs` folder for log files at your desired location on the host system.

![pre-install-2](https://i.imgur.com/XGzWrn5.png)

Grant nobody:nogroup access permissions to the created folders to allow Docker access.

```sh
sudo chown -R nobody:nogroup chzzk
```

![pre-install-3](https://i.imgur.com/aoSqEMn.png)

Access permissions were successfully granted.

### Docker Run

```bash
docker run -d \
  --name chzzk-noti-bot \
  -p 34224:34224 \ # host:container 80:34224
  # -e TZ=Asia/Seoul \ # optional, default: Asia/Seoul
  -v /root/docker/volumes/chzzk/data:/app/data \ # optional, path to store config.json file
  -v /root/docker/volumes/chzzk/logs:/app/logs \ # optional, path to store log files
  --restart always \ # restart policy
  onevl/chzzk-noti-bot # Use the latest Docker image

```

### docker-compose.yml

```yaml
services:
  chzzk-noti-bot-tts:
    image: onevl/chzzk-noti-bot
    container_name: chzzk-noti-bot
    ports:
      - "34224:34224"
    # environment:
    #   - TZ=Asia/Seoul # Optional, Default: Asia/Seoul
    volumes:
      - /root/docker/volumes/chzzk/data:/app/data # Optional, path to store config.json file
      - /root/docker/volumes/chzzk/logs:/app/logs # Optional, path to store log files
    restart: always
```

## Create a Discord Webhook

![discord-webhook-1](https://i.imgur.com/DoHpXPz.png)

Go to the settings of the channel where you want to receive notifications.

![discord-webhook-2](https://i.imgur.com/kd1wFu8.png)

Go to the Webhooks tab under Integrations.

![discord-webhook-3](https://i.imgur.com/yYgbrr9.png)

Create a new webhook and copy the URL for registration in the management page.

## Add or Edit a Category

![init](https://i.imgur.com/w9VqjBI.png)

This is the initial state after Docker installation.

Two example notifications are written, but actual notifications will not be sent because the Discord webhook URLs are incorrect.

![modify-add](https://i.imgur.com/5LZnpzF.png)

Enter the copied URL in the Discord webhook URL field.

![category](https://i.imgur.com/J5NLXUN.png)

"In the 'API URL' field, enter the URL of the API address containing category information, which you can find on the official Cheezic website."

```HTML
  https://api.chzzk.naver.com/service/v2/categories/(Type of the category)/(category)/lives
  ex: https://api.chzzk.naver.com/service/v2/categories/GAME/Tabletop_Simulator/lives
```

## Global Default Settings

![global](https://i.imgur.com/Y7gz2wc.png)

This is the page for managing the properties that will be applied by default when creating new notifications.
