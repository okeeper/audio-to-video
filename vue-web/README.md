## 项目说明

用Vue3实现一个根据音频链接生成视频的网页应用。该应用允许用户通过输入音频链接，自动生成字幕，配置相关图片素材，最终生成完整视频。

## 需求说明

### 功能流程
1. **音频输入**
   - 用户输入音频链接
   - 验证链接有效性
   - 点击下一步进入字幕确认环节

2. **字幕确认**
   - 自动请求后台接口识别音频内容
   - 展示识别出的字幕和对应时间信息
   - 允许用户确认或编辑字幕内容

3. **素材配置**
   - 展示系统根据字幕内容推荐的图片素材
   - 允许用户确认或替换每个场景的图片
   - 预览图片效果

4. **视频生成**
   - 提交生成视频请求
   - 显示生成进度
   - 处理异步生成流程

5. **视频下载**
   - 视频生成完成后提供下载链接
   - 支持视频预览
   - 提供重新生成选项

## 技术栈
- Vue 3
- TypeScript
- Vite
- Vue Router (页面路由)
- Pinia (状态管理)
- Axios (接口请求)

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

## 快速启动

### 本地开发
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### Docker 快速启动

1. **单行命令启动（使用默认配置）**
```bash
docker run -d --name audio-to-video -p 17777:17777 registry.cn-shenzhen.aliyuncs.com/okeeper/audio-to-video-vue:latest
```

2. **自定义 API 地址启动**
```bash
docker run -d --name audio-to-video \
  -p 17777:17777 \
  -e API_BASE_URL=http://your-api-server:17778 \
  registry.cn-shenzhen.aliyuncs.com/okeeper/audio-to-video-vue:latest
```

3. **停止和删除容器**
```bash
# 停止容器
docker stop audio-to-video

# 删除容器
docker rm audio-to-video
```

4. **查看容器日志**
```bash
# 查看实时日志
docker logs -f audio-to-video

# 查看最近100行日志
docker logs --tail 100 audio-to-video
```

### 常见问题处理

1. **端口冲突**
如果 17777 端口被占用，可以修改映射端口：
```bash
docker run -d --name audio-to-video -p 18888:17777 ...
```

2. **容器自动重启**
添加 --restart 参数：
```bash
docker run -d --name audio-to-video -p 17777:17777 --restart always ...
```

3. **查看容器状态**
```bash
docker ps | grep audio-to-video
```

## Docker 部署说明

### 构建并推送镜像
```bash
# 添加执行权限
chmod +x build-push.sh

# 执行构建和推送脚本
./build-push.sh
```

### 服务器部署
```bash
# 登录到 Docker 仓库
docker login registry.cn-shenzhen.aliyuncs.com

# 拉取镜像
docker pull registry.cn-shenzhen.aliyuncs.com/okeeper/audio-to-video-vue:latest

# 运行容器（使用默认 API 地址）
docker run -d \
  --name audio-to-video \
  -p 17777:17777 \
  --restart always \
  registry.cn-shenzhen.aliyuncs.com/okeeper/audio-to-video-vue:latest

# 或者指定自定义 API 地址
docker run -d \
  --name audio-to-video \
  -p 17777:17777 \
  -e API_BASE_URL=http://your-api-server:17778 \
  --restart always \
  registry.cn-shenzhen.aliyuncs.com/okeeper/audio-to-video-vue:latest
```

### 环境变量说明
- `API_BASE_URL`: API 服务器地址，默认为 `http://localhost:17778`
