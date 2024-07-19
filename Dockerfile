# Stage 1: Build
FROM python:3.9-alpine AS builder

WORKDIR /app

COPY requirements.txt .
# Install build dependencies and compile dependencies
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

# Stage 2: Run
FROM python:3.9-alpine

WORKDIR /app

# 비루트 사용자 및 그룹 생성
RUN addgroup -S chzzknoti && adduser -S chzzknoti -G chzzknoti

# 설치된 패키지 및 실행 파일 복사
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Supervisor 설치 및 설정 파일 복사
RUN apk add --no-cache supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 애플리케이션 파일 복사
COPY . .

# gunicorn 설치
RUN pip install gunicorn && \
    rm -rf /root/.cache

# 로그 파일 디렉토리 생성 및 파일 생성
RUN mkdir -p /app/logs && \
    touch /app/logs/flask_out.log /app/logs/flask_err.log /app/logs/discord_out.log /app/logs/discord_err.log && \
    chown -R chzzknoti:chzzknoti /app/logs /app/data && \
    chmod -R 755 /app/logs /app/data

# Adjust permissions for mounted volumes
RUN echo "Adjusting permissions for mounted volumes..." && \
    chmod -R 777 /app/logs

# 권한 설정
RUN chown -R chzzknoti:chzzknoti /app

# 기본 타임존 Asia/Seoul로 설정
ENV TZ=Asia/Seoul

# Flask 포트 노출
EXPOSE 34224

# 비루트 사용자로 전환
USER chzzknoti

# supervisord 실행 및 로그 파일과 도커 컨테이너로 로그 출력
CMD ["sh", "-c", "supervisord -c /etc/supervisor/conf.d/supervisord.conf && \
    tail -f /app/logs/supervisord.log /app/logs/flask_out.log /app/logs/discord_out.log /app/logs/flask_err.log /app/logs/discord_err.log"]
