# Stage 1: Build
FROM python:3.13.0b4-slim-bullseye AS builder

WORKDIR /app

COPY requirements.txt .
# Install build dependencies and compile dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc-dev libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc libc-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Run
FROM python:3.13.0b4-slim-bullseye

WORKDIR /app

# 설치된 패키지 및 실행 파일 복사
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Supervisor 설치 및 설정 파일 복사
RUN apt-get update && \
    apt-get install -y --no-install-recommends supervisor dos2unix bash procps && \
    rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# 애플리케이션 파일 복사
COPY config.json /app/data/config.json
COPY . .

# Convert line endings from DOS to UNIX
RUN dos2unix /app/entrypoint.sh
RUN dos2unix /app/config.json
RUN dos2unix /app/data/config.json
RUN dos2unix /etc/supervisor/conf.d/supervisord.conf
RUN dos2unix /app/supervisord.conf

# gunicorn 설치
RUN pip install gunicorn && \
    rm -rf /root/.cache

# 로그 파일 디렉토리 생성 및 파일 생성
RUN mkdir -p /app/logs /app/data && \
    touch /app/logs/flask_out.log /app/logs/flask_err.log /app/logs/discord_out.log /app/logs/discord_err.log /app/logs/supervisord.log /app/supervisord.pid && \
    chown -R nobody:nogroup /app && \
    chmod -R 755 /app

# 기본 타임존 Asia/Seoul로 설정
ENV TZ=Asia/Seoul

# Flask 포트 노출
EXPOSE 34224

USER nobody

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/bin/bash"]