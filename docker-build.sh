#!/bin/bash

# 변수 설정
DOCKER_HUB_USERNAME="onevl"
IMAGE_NAME="chzzk-noti-bot"

# 파일 이름 설정
VERSION_FILE="version.txt"

# 초기 설정: 파일이 없으면 기본 버전 설정
if [ ! -f "$VERSION_FILE" ]; then
    echo "0.0.1" > "$VERSION_FILE"
fi

# 버전 읽어오기
OLD_VERSION=$(cat "$VERSION_FILE")

echo "도커 $OLD_VERSION 이미지 삭제 중..."
docker rmi $DOCKER_HUB_USERNAME/$IMAGE_NAME:$OLD_VERSION

# 버전 증가 로직
MAJOR=$(echo "$OLD_VERSION" | cut -d '.' -f 1)
MINOR=$(echo "$OLD_VERSION" | cut -d '.' -f 2)
PATCH=$(echo "$OLD_VERSION" | cut -d '.' -f 3)

# 증가
PATCH=$((PATCH + 1))

# 시맨틱 버전 설정
VERSION="$MAJOR.$MINOR.$PATCH"
echo "$VERSION" > "$VERSION_FILE"

# 도커 이미지 빌드
echo "도커 $VERSION 이미지 빌드 중..."
docker build -t $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION .

# 도커 이미지 푸시
echo "도커 $VERSION 이미지 푸시 중..."
docker tag $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest
docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION
docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest

echo "도커 $VERSION 이미지 빌드 및 푸시 완료!"