import json
import requests
import logging
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import os
from datetime import datetime
from cachetools import TTLCache
import threading

# 설정 파일 경로
CONFIG_FILE = 'data/config.json'
cache = TTLCache(maxsize=200, ttl=86400)  # 캐시 설정

IS_CONFIG_CHANGED = False

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 설정 파일 읽기
def read_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 설정 파일 쓰기
def write_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

class StoppableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def is_duplicate_live_id(live_id):
    return live_id in cache

def add_live_id_to_cache(live_id):
    cache[live_id] = True

def parse_do_not_disturb(CONFIG):
    start_time_str = CONFIG.get("do_not_disturb_start")
    end_time_str = CONFIG.get("do_not_disturb_end")
    start_time = datetime.strptime(start_time_str.strip(), '%H:%M').time()
    end_time = datetime.strptime(end_time_str.strip(), '%H:%M').time()
    return start_time, end_time

def is_within_do_not_disturb(start_time, end_time):
    now = datetime.now().time()
    if start_time <= end_time: 
        logging.info(f"start_time <= end_time {start_time <= now <= end_time}")
        return start_time <= now <= end_time
    else:
        return now >= start_time or now <= end_time

def should_disturb(CONFIG):
    start_time, end_time = parse_do_not_disturb(CONFIG)
    now = datetime.now().time()
    is_do_not_disturb_on = CONFIG.get("do_not_disturb_on")
    logging.info(f"should_disturb not is_within_do_not_disturb {now} {is_do_not_disturb_on} {start_time} {end_time} {not is_within_do_not_disturb(start_time, end_time)}")
    logging.info(f"if state is_within_do_not_disturb {is_do_not_disturb_on == 'False' or not is_within_do_not_disturb(start_time, end_time)}")
    return is_do_not_disturb_on == "False" or not is_within_do_not_disturb(start_time, end_time)
    
    # if start_time <= end_time: 
    # else:
    #     return now >= start_time or now <= end_time

def check_api_response(API_URL, DISCORD_WEBHOOK_URL, CUSTOM_USER_AGENT='Mozilla/5.0'):
    HEADERS = {"User-Agent": CUSTOM_USER_AGENT}
    logging.info(f"check_api_response 개별 알림에 설정된 게임의 방송이 진행중인지  \"{API_URL}\" 주소로 요청을 보내 체크합니다.")
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json().get('content', {}).get('data', [])

        if data:
            for item in data:
                live_id = item['liveId']
                if not is_duplicate_live_id(live_id):
                    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
                    embed = DiscordEmbed(title=item['liveTitle'], description=f"https://chzzk.naver.com/live/{item['channel']['channelId']}", color="1DFFA3")
                    embed.set_author(name=item['channel']['channelName'], url=f"https://chzzk.naver.com/{item['channel']['channelId']}", icon_url=item['channel']['channelImageUrl'])
                    if item['liveImageUrl']:
                        embed.set_thumbnail(url=item['liveImageUrl'].replace("{type}", "480"))
                    embed.add_embed_field(name=item['liveCategoryValue'], value=f"[방송 바로가기](https://chzzk.naver.com/live/{item['channel']['channelId']})", inline=False)
                    embed.set_footer(text="1-vL/chzzk-noti-bot", url="https://github.com/1-vL/chzzk-noti-bot", icon_url="https://play-lh.googleusercontent.com/wvo3IB5dTJHyjpIHvkdzpgbFnG3LoVsqKdQ7W3IoRm-EVzISMz9tTaIYoRdZm1phL_8=w240-h480-rw")
                    webhook.add_embed(embed)
                    webhook.execute()
                    logging.info(f"알림이 전송되었습니다: 현재 진행 중인 \"{item['channel']['channelName']}\" 님의 \"{item['liveCategoryValue']}\" 방송이 있습니다!")
                    add_live_id_to_cache(live_id)
                else:
                    logging.info(f"중복된 방송입니다. {item['liveCategoryValue']} 방송 ID: {live_id}. 알림을 보내지 않습니다.")
        else:
            logging.info('진행 중인 방송이 없습니다.')

    except requests.exceptions.RequestException as e:
        logging.error(f'{API_URL} API 응답을 가져오는 중 오류 발생: {e}')

def process_individual_config(CONFIG, stop_event):
    while not stop_event.is_set():        
        title = CONFIG.get("title", "기본 제목")
        file_noti_configs = read_config().get("individual_configs", [])
        if CONFIG not in file_noti_configs:
            logging.info(f"설정 변경으로 인해 \"{title}\" 개별 알림에 설정된 카테고리의 방송은 더이상 체크하지 않습니다.")
            stop_event.set()  # stop_event를 설정하여 루프 종료
            break  # 루프 즉시 종료
        logging.info(f"\"{title}\" 게임의 방송이 진행중인지 스캔이 시작되었습니다.")
        MODE = CONFIG.get("mode", "default")

        if MODE == "default":
            logging.info("알림이 기본 모드입니다.")
            process_default_mode(CONFIG)
        elif MODE == "off":
            logging.info("해당 설정은 OFF 상태입니다. 실행하지 않습니다.")
        elif MODE == "blacklist":
            logging.info("알림이 블랙리스트 모드입니다.")
            process_blacklist_mode(CONFIG)
        elif MODE == "advanced":
            logging.info("알림이 고급 모드입니다.")
            process_advanced_mode(CONFIG)
        else:
            logging.warning(f"알 수 없는 모드 설정: {MODE}. 기본 모드로 실행합니다.")
            process_default_mode(CONFIG)
        
        interval_seconds = CONFIG.get("interval_seconds", 60)
        logging.info(f"\"{title}\" 개별 알림에 설정된 게임의 방송이 진행중인지 {interval_seconds}초 뒤에 다시 체크합니다.")
        time.sleep(interval_seconds)

def process_default_mode(CONFIG):
    API_URL = CONFIG.get("api_url")
    DISCORD_WEBHOOK_URL = CONFIG.get("discord_webhook_url")
    CUSTOM_USER_AGENT = CONFIG.get("custom_user_agent")
    
    if should_disturb(CONFIG):
        check_api_response(API_URL, DISCORD_WEBHOOK_URL, CUSTOM_USER_AGENT)
        interval_seconds = CONFIG.get("interval_seconds", 60)
        time.sleep(interval_seconds)

def process_blacklist_mode(CONFIG):
    API_URL = CONFIG.get("api_url")
    DISCORD_WEBHOOK_URL = CONFIG.get("discord_webhook_url")
    CUSTOM_USER_AGENT = CONFIG.get("custom_user_agent")
    BLACKLIST = CONFIG.get("blacklist", [])
    
    if should_disturb(CONFIG):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json().get('content', {}).get('data', [])

            if data:
                for item in data:
                    if item['channel']['channelId'] not in BLACKLIST:
                        check_api_response(API_URL, DISCORD_WEBHOOK_URL, CUSTOM_USER_AGENT)
                        break
                    else:
                        logging.info(f"블랙리스트에 포함된 채널 ID입니다. 방송 ID: {item['liveId']}. 알림을 보내지 않습니다.")
            else:
                logging.info('진행 중인 방송이 없습니다.')

        except requests.exceptions.RequestException as e:
            logging.error(f'{API_URL} API 응답을 가져오는 중 오류 발생: {e}')

def process_advanced_mode(CONFIG):
    API_URL = CONFIG.get("api_url")
    DISCORD_WEBHOOK_URL = CONFIG.get("discord_webhook_url")
    CUSTOM_USER_AGENT = CONFIG.get("custom_user_agent")
    BLACKLIST = CONFIG.get("blacklist", [])
    WHITELIST = CONFIG.get("whitelist", [])
    EXCLUDE_KEYWORDS = CONFIG.get("exclude_keywords", [])

    if should_disturb(CONFIG):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json().get('content', {}).get('data', [])

            if data:
                for item in data:
                    channel_id = item['channel']['channelId']
                    live_title = item['liveTitle']
                    live_tags = item.get('tags', [])
                    exclude_flag = False
                    if channel_id not in WHITELIST:
                        if channel_id in BLACKLIST:
                            exclude_flag = True
                        for keyword in EXCLUDE_KEYWORDS:
                            if keyword in live_title or keyword in live_tags:
                                exclude_flag = True
                                break
                        
                        if not exclude_flag:
                            check_api_response(API_URL, DISCORD_WEBHOOK_URL, CUSTOM_USER_AGENT)
                            break
                        else:
                            logging.info(f"[고급 모드] 방송 제목 또는 설명에 제외 키워드가 포함되어 알림을 보내지 않습니다. 방송 ID: {item['liveId']}")
                    else:
                        check_api_response(API_URL, DISCORD_WEBHOOK_URL, CUSTOM_USER_AGENT)
                        logging.info(f"[고급 모드] 화이트리스트에 포함되었거나 블랙리스트에 포함되지 않은 채널 ID입니다. 방송 ID: {item['liveId']}. 알림을 보냅니다.")
            else:
                logging.info('[고급 모드] 진행 중인 방송이 없습니다.')

        except requests.exceptions.RequestException as e:
            logging.error(f'{API_URL} API 응답을 가져오는 중 오류 발생: {e}')

def monitor_config_changes(interval_seconds=10):
    last_modified_time = time.time()
    
    while True:
        config_modified_time = os.path.getmtime(CONFIG_FILE)
        if config_modified_time > last_modified_time:
            logging.info("설정 파일이 변경되었습니다. 변경 사항을 적용합니다.")
            global IS_CONFIG_CHANGED
            IS_CONFIG_CHANGED = True
            last_modified_time = config_modified_time
            main_bot_process()

        time.sleep(interval_seconds)

def main_bot_process():
    global IS_CONFIG_CHANGED
    threads = []
    bot_thread_init(threads)
    
    while True:
        if IS_CONFIG_CHANGED:
            logging.info("설정 파일이 변경되었습니다. 이전 스레드를 종료하고 다시 로드합니다.")
            bot_thread_init(threads)            
            IS_CONFIG_CHANGED = False
        time.sleep(60)

def bot_thread_init(threads):
    config = read_config()
    DEFAULT_CONFIGS = config.get('default_config', {})
    GLOBAL_CONFIGS = config.get('global_config', {})
    
    for prev_thread in threads:
        prev_thread.stop()
        prev_thread.join()
    
    threads.clear()

    APPLIED_GLOBAL_CONFIG = {**DEFAULT_CONFIGS, **GLOBAL_CONFIGS}
    individual_configs = config.get("individual_configs", [])
    logging.info(f"총 {len(individual_configs)} 개의 개별 설정을 처리합니다.")
    for individual_config in individual_configs:
        merged_config = {**APPLIED_GLOBAL_CONFIG, **individual_config}
        stop_event = threading.Event()
        thread = StoppableThread(target=process_individual_config, args=(merged_config, stop_event))
        thread._stop_event = stop_event
        thread.start()
        threads.append(thread)

if __name__ == '__main__':
    monitor_thread = threading.Thread(target=monitor_config_changes)
    monitor_thread.daemon = False
    monitor_thread.start()
    logging.info("__main__ 함수")
    discord_thread = threading.Thread(target=main_bot_process)
    discord_thread.daemon = False
    discord_thread.start()

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