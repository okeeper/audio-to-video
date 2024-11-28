#!/bin/bash

# 设置变量
DOCKER_REGISTRY="registry.cn-shenzhen.aliyuncs.com/okeeper"  # 替换为你的Docker仓库地址
IMAGE_NAME="audio-to-video-python"
LATEST_IMAGE_NAME="$DOCKER_REGISTRY/$IMAGE_NAME:latest"

# 使用 buildx 构建多架构镜像
echo "Building multi-arch Docker image: $LATEST_IMAGE_NAME"
docker buildx create --use --name mybuilder || true
docker buildx inspect mybuilder --bootstrap

# docker build  -t registry.cn-shenzhen.aliyuncs.com/okeeper/audio-to-video-python:latest     -f Dockerfile ..

# 构建并推送多架构镜像
docker buildx build --platform linux/amd64,linux/arm64 \
    --cache-from type=registry,ref=$LATEST_IMAGE_NAME \
    --cache-to type=inline \
    -t $LATEST_IMAGE_NAME \
    -f Dockerfile \
    .. \
    --push

# 完成提示
echo "======================================"
echo "构建和推送完成！"
echo "镜像标签："
echo "- $LATEST_IMAGE_NAME"
echo "======================================" 