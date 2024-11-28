#!/bin/bash

# 设置变量
DOCKER_REGISTRY="registry.cn-shenzhen.aliyuncs.com/okeeper"  # 替换为你的Docker仓库地址
IMAGE_NAME="audio-to-video-vue"
CONTAINER_NAME="audio-to-video-vue"
API_BASE_URL="http://localhost:17778"

# 拉取最新镜像
# echo "Pulling latest image..."
# docker pull $DOCKER_REGISTRY/$IMAGE_NAME:latest

# 停止并删除旧容器
echo "Stopping and removing old container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 启动新容器
echo "Starting new container..."
# 或者指定自定义 API 地址
docker run -d \
  --name $CONTAINER_NAME \
  -p 17777:17777 \
  -e API_BASE_URL=$API_BASE_URL \
  --restart always \
  $DOCKER_REGISTRY/$IMAGE_NAME:latest

# 检查容器状态
echo "Checking container status..."
docker ps | grep $CONTAINER_NAME

echo "Deployment completed!" 