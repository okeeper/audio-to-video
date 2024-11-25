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
