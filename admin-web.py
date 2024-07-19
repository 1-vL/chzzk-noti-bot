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
cache = TTLCache(maxsize=200, ttl=86400)  # 최대 200개의 방송기록을 24시간 동안 유지

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
    return render_template('individual_configs.html', individual_configs=config['individual_configs'], default_config={**config['default_config'], **config['global_config']})

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


# dev mode
# def run_flask_app():
#     logging.info("run_flask_app 함수")
#     app.run(debug=False, host='0.0.0.0', port=34224)
    
# if __name__ == '__main__':
#     # Flask 애플리케이션 시작
#     run_flask_app()




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