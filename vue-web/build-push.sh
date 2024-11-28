#!/bin/bash

# 设置变量
DOCKER_USERNAME="registry.cn-shenzhen.aliyuncs.com/okeeper"
IMAGE_NAME="audio-to-video-vue"
LATEST_TAG="latest"

# 显示构建信息
echo "======================================"
echo "开始构建和推送 Docker 镜像"
echo "镜像名称: $DOCKER_USERNAME/$IMAGE_NAME"
echo "版本标签: $LATEST_TAG"
echo "======================================"

# 登录到阿里云 Docker Registry
echo "正在登录到阿里云 Docker Registry..."
docker login registry.cn-shenzhen.aliyuncs.com

# 检查登录是否成功
if [ $? -ne 0 ]; then
    echo "Docker Hub 登录失败！"
    exit 1
fi


# 使用 buildx 构建多架构镜像
echo "Building multi-arch Docker image: $DOCKER_USERNAME/$IMAGE_NAME:$LATEST_TAG"
docker buildx create --use --name mybuilder || true
docker buildx inspect mybuilder --bootstrap

# 构建镜像（添加 --no-cache 参数）
echo "正在构建 Docker 镜像..."
#docker build --no-cache -t $DOCKER_USERNAME/$IMAGE_NAME:$LATEST_TAG .
#docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$LATEST_TAG .
docker buildx build --platform linux/amd64,linux/arm64 -t $DOCKER_USERNAME/$IMAGE_NAME:$LATEST_TAG  --push .

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "镜像构建成功！"
else
    echo "镜像构建失败！"
    exit 1
fi


# 推送最新版本标签
# echo "正在推送镜像 $DOCKER_USERNAME/$IMAGE_NAME:$LATEST_TAG ..."
# docker push $DOCKER_USERNAME/$IMAGE_NAME:$LATEST_TAG

# 完成提示
echo "======================================"
echo "构建和推送完成！"
echo "镜像标签："
echo "- $DOCKER_USERNAME/$IMAGE_NAME:$LATEST_TAG"
echo "======================================" 