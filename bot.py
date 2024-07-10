import requests
import logging
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
from dotenv import load_dotenv
import os
from functools import lru_cache
from datetime import datetime, timedelta
from cachetools import TTLCache

# 환경 변수를 로드합니다.
load_dotenv()

# TTL을 설정할 수 있는 캐시 객체 생성
cache = TTLCache(maxsize=200, ttl=86400)  # 최대 200개의 아이템을 24시간 동안 유지

API_URL = os.getenv('API_URL')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
CUSTOM_USER_AGENT = os.getenv('CUSTOM_USER_AGENT', 'PostmanRuntime/7.37.3')

HEADERS = {"User-Agent": CUSTOM_USER_AGENT}

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_duplicate_live_id(live_id):
    """중복 방송인지 체크하는 함수"""
    return live_id in cache

def add_live_id_to_cache(live_id):
    """방송 ID를 캐시에 추가하는 함수"""
    cache[live_id] = True

def check_api_response():
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json().get('content', {}).get('data', [])

        if data:
            for item in data:
                live_id = item['liveId']
                if not is_duplicate_live_id(live_id):
                    # message = (f"현재 진행 중인 {item['liveCategoryValue']} 방송이 있습니다!\n제목: {item['liveTitle']}\n"
                    #            f"링크: https://chzzk.naver.com/live/{item['channel']['channelId']}")
                    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
                    embed = DiscordEmbed(title=item['liveTitle'], description=f"https://chzzk.naver.com/live/{item['channel']['channelId']}", color="1DFFA3")
                    embed.set_author(name=item['channel']['channelName'], url=f"https://chzzk.naver.com/{item['channel']['channelId']}", icon_url=item['channel']['channelImageUrl'])

                    embed.set_thumbnail(url=item['liveImageUrl'].replace("{type}", "480"))
                    # embed.set_image(url=item['liveImageUrl'].replace("{type}","480"))
                    
                    embed.add_embed_field(name="", value=f"[방송 바로가기](https://chzzk.naver.com/live/{item['channel']['channelId']})", inline=False)
                    embed.set_footer(text="1-vL/chzzk-noti-bot", url=f"https://github.com/1-vL/chzzk-noti-bot", icon_url="https://play-lh.googleusercontent.com/wvo3IB5dTJHyjpIHvkdzpgbFnG3LoVsqKdQ7W3IoRm-EVzISMz9tTaIYoRdZm1phL_8=w240-h480-rw")
                    # add embed object to webhook
                    webhook.add_embed(embed)

                    webhook.execute()
                    logging.info(f"알림이 전송되었습니다: 현재 진행 중인 {item['liveCategoryValue']} 방송이 있습니다!")
                    add_live_id_to_cache(live_id)
                else:
                    logging.info(f'중복된 방송입니다. 방송 ID: {live_id}. 알림을 보내지 않습니다.')
        else:
            logging.info('진행 중인 방송이 없습니다.')

    except requests.exceptions.RequestException as e:
        logging.error(f'{API_URL} API 응답을 가져오는 중 오류 발생: {e}'
                      f'CUSTOM_USER_AGENT: {CUSTOM_USER_AGENT}')

if __name__ == "__main__":
    while True:
        check_api_response()
        time.sleep(60)  # 60초마다 실행


# https://api.chzzk.naver.com/service/v2/categories/GAME/Tabletop_Simulator/lives?

# {
#   "code": 200,
#   "message": null,
#   "content": {
#     "size": 20,
#     "page": {
#       "next": {
#         "concurrentUserCount": 2,
#         "liveId": 1234567
#       }
#     },
#     "data": [
#       {
#         "liveId": 1234567,
#         "liveTitle": "스트리머가 설정한 방송제목",
#         "liveImageUrl": "썸네일 이미지 링크",
#         "defaultThumbnailImageUrl": null,
#         "concurrentUserCount": 2,
#         "accumulateCount": 12,
#         "openDate": "2024-07-07 01:11:58",
#         "adult": false,
#         "tags": [
#           "즐겜",
#           "일본어"
#         ],
#         "categoryType": "GAME", # 카테고리 종류
#         "liveCategory": "Tabletop_Simulator", # 게임 태그
#         "liveCategoryValue": "테이블탑 시뮬레이터", # 게임 제목
#         "channel": {
#           "channelId": "----채널 ID 위치----",
#           "channelName": "채널명예시",
#           "channelImageUrl": "채널 이미지",
#           "verifiedMark": false,
#           "personalData": {
#             "privateUserBlock": false
#           }
#         },
#         "blindType": null
#       }
#     ]
#   }
# }