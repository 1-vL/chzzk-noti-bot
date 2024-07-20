#!/bin/bash

# 변수 설정
DOCKER_HUB_USERNAME="onevl"
IMAGE_NAME="chzzk-noti-bot"
VERSION="dev"

echo "도커 $VERSION 이미지 삭제 중..."
docker rmi $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION

echo "도커 Buildx 세팅..."
# Buildx 설정 및 QEMU 설치
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker buildx create --use --name mybuilder

# 도커 이미지 빌드
echo "도커 $VERSION 멀티 아키텍처 이미지 빌드 중... amd64"
BUILD_STATUS=0
docker buildx build --platform linux/amd64 -t $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION --push . || BUILD_STATUS=1

if [ $BUILD_STATUS -eq 0 ]; then
    # 도커 이미지 푸시
    echo "도커 $VERSION 이미지 빌드 및 푸시 완료!"
fi

# 성공적으로 빌드 및 푸시가 완료되면 버전 증가
echo "도커 Buildx 클린업..."
# Buildx 클린업
docker buildx rm mybuilder || { echo "Buildx 클린업 실패"; exit 1; }