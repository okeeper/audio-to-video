#!/bin/sh
# 替换配置文件中的环境变量
sed -i "s|{API_BASE_URL}|${API_BASE_URL:-http://localhost:17778}|g" /app/dist/config.js

exec "$@" 