#!/bin/bash

# 필요한 파일 경로 설정
REQUIRED_FILES=(
    "/app/data/config.json"
    "/app/supervisord.conf"
    "/app/logs/supervisord.log"
    "/app/logs/flask_out.log"
    "/app/logs/discord_out.log"
    "/app/logs/flask_err.log"
    "/app/logs/discord_err.log"
)

# 필요한 파일이 없으면 생성
for FILE in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$FILE" ]; then
        echo "파일이 존재하지 않습니다: $FILE. 생성 중..."
        if [ "$FILE" == "/app/data/config.json" ]; then
            echo "기본 config.json 설정 파일을 복사합니다..."
            # /config.json 파일을 /app/data/config.json으로 복사
            cp /app/config.json /app/data/config.json
        else
            # 파일 생성, 기본 내용 추가 (필요에 따라 수정 가능)
            touch "$FILE"
            # 기본 설정 파일이 필요하면 추가 내용을 작성할 수 있습니다.
            # echo "{}" > "$FILE"
        fi
    fi
done

# 로그 파일을 모니터링 (백그라운드에서 실행)
echo "Run supervisord from /app/supervisord.conf"
exec /usr/bin/supervisord -c /app/supervisord.conf &
tail -f /app/logs/supervisord.log /app/logs/flask_out.log /app/logs/discord_out.log /app/logs/flask_err.log /app/logs/discord_err.log

# 애플리케이션 실행
# echo "Executing command: $@" &
# exec "$@"
