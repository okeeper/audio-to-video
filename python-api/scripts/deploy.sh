#!/bin/bash

# 设置变量
DOCKER_REGISTRY="registry.cn-shenzhen.aliyuncs.com/okeeper"  # 替换为你的Docker仓库地址
IMAGE_NAME="audio-to-video-python"
CONTAINER_NAME="audio-to-video-python"

# 拉取最新镜像
# echo "Pulling latest image..."
# docker pull $DOCKER_REGISTRY/$IMAGE_NAME:latest

# 停止并删除旧容器
echo "Stopping and removing old container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 启动新容器
echo "Starting new container..."
docker run -d \
    --name $CONTAINER_NAME \
    --network my-network \
    -p 17778:17778 \
    --restart unless-stopped \
    -v /data/logs/$CONTAINER_NAME:/app/logs \
    -v /data/logs/$CONTAINER_NAME/tmp:/app/tmp \
    -v /data/logs/$CONTAINER_NAME/output:/app/output \
    $DOCKER_REGISTRY/$IMAGE_NAME:latest

# 检查容器状态
echo "Checking container status..."
docker ps | grep $CONTAINER_NAME

echo "Deployment completed!" 