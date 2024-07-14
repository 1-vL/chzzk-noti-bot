from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import requests
import logging
from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import os
from functools import lru_cache
from datetime import datetime, timedelta
from cachetools import TTLCache
import threading

app = Flask(__name__)

# 설정 파일 경로
CONFIG_FILE = 'data/config.json'
# TTL을 설정할 수 있는 캐시 객체 생성
cache = TTLCache(maxsize=200, ttl=86400)  # 최대 200개의 아이템을 24시간 동안 유지

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

# 커스텀 필터 정의: enumerate 함수를 사용할 수 있도록 함
def jinja2_enumerate(iterable):
    return enumerate(iterable)

# Flask 애플리케이션에 필터 등록
app.jinja_env.filters['enumerate'] = jinja2_enumerate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/global_config')
def global_config():
    config = read_config()
    return render_template('global_config.html', global_config=config['global_config'])

@app.route('/individual_configs')
def individual_configs():
    config = read_config()
    return render_template('individual_configs.html', individual_configs=config['individual_configs'])

@app.route('/update_global_config', methods=['POST'])
def update_global_config():
    new_config = request.json    
    config = read_config()
    config['global_config'] = new_config
    write_config(config)
    return redirect(url_for('global_config'))

@app.route('/update_individual_config/<int:idx>', methods=['POST'])
def update_individual_config(idx):
    new_config = request.json
    config = read_config()
    config['individual_configs'][idx] = new_config
    write_config(config)
    return redirect(url_for('individual_configs'))

@app.route('/delete_individual_config/<int:idx>', methods=['DELETE'])
def delete_individual_config(idx):
    config = read_config()
    try:
        del config['individual_configs'][idx]
    except IndexError:
        return "Index out of range", 404  # 삭제할 인덱스가 범위를 벗어날 경우 404 에러 반환
    write_config(config)
    return jsonify({'message': 'Config deleted successfully.'}), 200

@app.route('/add_individual_config', methods=['POST'])
def add_individual_config():
    request_config = request.json
    config = read_config()
    new_config = {**config['default_config'], **config['global_config'] , **request_config}
    config['individual_configs'].append(new_config)
    write_config(config)
    return jsonify({"message": "새로운 설정이 추가되었습니다."}), 200

def is_duplicate_live_id(live_id):
    """Method to check if the live ID is duplicated."""
    """중복 방송인지 체크하는 함수"""
    return live_id in cache

def add_live_id_to_cache(live_id):
    """Method to add the live ID to the cache."""
    """방송 ID를 캐시에 추가하는 함수"""
    cache[live_id] = True

# "DO_NOT_DISTURB" 설정 파싱
def parse_do_not_disturb(CONFIG):
    """Parses the 'do_not_disturb' time settings."""
    """'do_not_disturb' 시간 설정을 파싱합니다."""
    start_time_str = CONFIG.get("do_not_disturb_start")
    end_time_str = CONFIG.get("do_not_disturb_end")
    start_time = datetime.strptime(start_time_str.strip(), '%H:%M').time()
    end_time = datetime.strptime(end_time_str.strip(), '%H:%M').time()
    return start_time, end_time

# 현재 시간이 방해 금지 시간 내에 있는지 확인
def is_within_do_not_disturb(start_time, end_time):
    """Checks if the current time is within the 'do_not_disturb' time range."""
    """현재 시간이 'do_not_disturb' 시간 범위 내에 있는지 확인합니다."""
    now = datetime.now().time()
    if start_time <= end_time:
        return start_time <= now <= end_time
    else:
        return now >= start_time or now <= end_time

# chzzk API 응답 확인 및 Discord 웹훅 메시지 전송
def check_api_response(API_URL, DISCORD_WEBHOOK_URL, CUSTOM_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'):
    """Calls the chzzk API and sends a Discord webhook message if live is on."""
    """치지직 API를 호출하고 방송중인 경우 Discord 웹훅으로 메시지를 전송합니다."""
    HEADERS = {"User-Agent": CUSTOM_USER_AGENT}
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
                    item['liveImageUrl'] and embed.set_thumbnail(url=item['liveImageUrl'].replace("{type}", "480"))
                    embed.add_embed_field(name=item['liveCategoryValue'], value=f"[방송 바로가기](https://chzzk.naver.com/live/{item['channel']['channelId']})", inline=False)
                    embed.set_footer(text="1-vL/chzzk-noti-bot", url="https://github.com/1-vL/chzzk-noti-bot", icon_url="https://play-lh.googleusercontent.com/wvo3IB5dTJHyjpIHvkdzpgbFnG3LoVsqKdQ7W3IoRm-EVzISMz9tTaIYoRdZm1phL_8=w240-h480-rw")
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

# 개별 설정을 처리하는 함수
def process_individual_config(CONFIG):
    """Processes individual configuration."""
    """개별 설정을 처리하는 함수"""
    logging.info("process_individual_config 개별 설정을 처리하는 함수")
    MODE = CONFIG.get("mode", "default")

    if MODE == "default":
        process_default_mode(CONFIG)
    elif MODE == "off":
        logging.info("해당 설정은 OFF 상태입니다. 실행하지 않습니다.")
    elif MODE == "blacklist":
        process_blacklist_mode(CONFIG)
    elif MODE == "advanced":
        process_advanced_mode(CONFIG)
    else:
        logging.warning(f"알 수 없는 모드 설정: {MODE}. 기본 모드로 실행합니다.")
        process_default_mode(CONFIG)

# 기본 모드 처리 함수
def process_default_mode(CONFIG):
    """Processes in DEFAULT mode."""
    """기본 모드에서 처리합니다."""
    API_URL = CONFIG.get("api_url")
    DISCORD_WEBHOOK_URL = CONFIG.get("discord_webhook_url")
    CUSTOM_USER_AGENT = CONFIG.get("custom_user_agent")
    start_time, end_time = parse_do_not_disturb(CONFIG)
    is_do_not_disturb_on = CONFIG.get("do_not_disturb_on")
    if is_do_not_disturb_on == "False" or not is_within_do_not_disturb(start_time, end_time):
        check_api_response(API_URL, DISCORD_WEBHOOK_URL, CUSTOM_USER_AGENT)
        interval_seconds = CONFIG.get("interval_seconds", 60)  # 기본값 60초
        time.sleep(interval_seconds)

# 블랙리스트 모드 처리 함수
def process_blacklist_mode(CONFIG):
    """Processes in BLACKLIST mode."""
    """블랙리스트 모드에서 처리합니다."""
    API_URL = CONFIG.get("api_url")
    DISCORD_WEBHOOK_URL = CONFIG.get("discord_webhook_url")
    CUSTOM_USER_AGENT = CONFIG.get("custom_user_agent")
    BLACKLIST = CONFIG.get("blacklist", [])
    start_time, end_time = parse_do_not_disturb(CONFIG)
    is_do_not_disturb_on = CONFIG.get("do_not_disturb_on")
    
    if is_do_not_disturb_on == "False" or not is_within_do_not_disturb(start_time, end_time):
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
            logging.error(f'{API_URL} API 응답을 가져오는 중 오류 발생: {e}'
                        f'CUSTOM_USER_AGENT: {CUSTOM_USER_AGENT}')

# 고급 모드 처리 함수
def process_advanced_mode(CONFIG):
    """Processes in ADVANCED mode."""
    """고급 모드에서 처리합니다."""
    API_URL = CONFIG.get("api_url")
    DISCORD_WEBHOOK_URL = CONFIG.get("discord_webhook_url")
    CUSTOM_USER_AGENT = CONFIG.get("custom_user_agent")
    BLACKLIST = CONFIG.get("blacklist", [])
    WHITELIST = CONFIG.get("whitelist", [])
    EXCLUDE_KEYWORDS = CONFIG.get("exclude_keywords", [])
    start_time, end_time = parse_do_not_disturb(CONFIG)
    is_do_not_disturb_on = CONFIG.get("do_not_disturb_on")

    if is_do_not_disturb_on == "False" or not is_within_do_not_disturb(start_time, end_time):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json().get('content', {}).get('data', [])

            if data:
                for item in data:
                    channel_id = item['channel']['channelId']
                    live_title = item['liveTitle']
                    live_tags = item.get('tags', [])
    #  and channel_id in BLACKLIST
                        # exclude_flag = True
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
            logging.error(f'{API_URL} API 응답을 가져오는 중 오류 발생: {e}'
                        f'CUSTOM_USER_AGENT: {CUSTOM_USER_AGENT}')
            
def monitor_config_changes(interval_seconds=10):
    last_modified_time = time.time()

    while True:
        config_modified_time = os.path.getmtime(CONFIG_FILE)  # 설정 파일의 최종 수정 시간 확인
        if config_modified_time > last_modified_time:
            print("설정 파일이 변경되었습니다. 변경 사항을 적용합니다.")
            # main_bot_process()  # 설정 파일 변경 시 main 함수 호출
            last_modified_time = config_modified_time

        time.sleep(interval_seconds)  # 일정 시간 간격으로 설정 파일 변경 확인

def run_flask_app():
    logging.info("run_flask_app 함수")
    app.run(debug=False, host='0.0.0.0', port=34224)
    # app.run(debug=True, port=80)

def main_bot_process():
    logging.info("main_bot_process 함수")
    # 설정 파일 읽어오기
    config = read_config()
    INDIVIDUAL_CONFIGS = config.get('individual_configs', {})
    DEFAULT_CONFIGS = config.get('default_config', {})
    GLOBAL_CONFIGS = config.get('global_config', {})

    # DEFAULT_CONFIGS와 GLOBAL_CONFIGS 병합    
    # 전역 설정 적용
    APPLIED_GLOBAL_CONFIG = {**DEFAULT_CONFIGS, **GLOBAL_CONFIGS}
    
    # 개별 알림 설정 처리
    for CONFIG in INDIVIDUAL_CONFIGS:
        logging.info(CONFIG)
        APPLIED_CONFIG = {**APPLIED_GLOBAL_CONFIG, **CONFIG}
        process_individual_config(APPLIED_CONFIG)


if __name__ == '__main__':
    # 설정 파일 변경을 모니터링하는 스레드 시작
    monitor_thread = threading.Thread(target=monitor_config_changes)
    monitor_thread.daemon = True  # 메인 프로세스 종료 시 함께 종료되도록 설정
    monitor_thread.start()
    logging.info("__main__ 함수")
    # 디스코드 챗봇 스레드 시작
    discord_thread = threading.Thread(target=main_bot_process)
    discord_thread.daemon = True  # 메인 프로세스 종료 시 함께 종료되도록 설정
    discord_thread.start()

    # Flask 애플리케이션 시작
    run_flask_app()




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