# 视频剪辑工具

这是一个自动化视频剪辑工具,可以根据音频内容自动生成短视频。

## 准备工作

在运行程序之前,你需要准备以下API密钥:

1. Unsplash API Key
   - 访问 [Unsplash Developer](https://unsplash.com/developers) 注册开发者账号
   - 创建应用获取 Access Key
   - 将获取的key填入 config.py 的 UNSPLASH_ACCESS_KEY

2. 阿里云语音识别 API Key
   - 访问[阿里云通义千问](https://dashscope.console.aliyun.com/)
   - 开通语音识别服务并创建API Key
   - 将获取的key填入 config.py 的 ALI_API_KEY

3. Coze API Token
   - 访问 [Coze](https://www.coze.cn/) 注册账号
   - 在设置中生成 API Token
   - 将token填入 config.py 的 COZE_AUTH_TOKEN

## 配置文件设置

1. 复制配置文件模板:
```bash
cp config.py.copy config.py
```

2. 编辑 config.py 文件，填入你的API密钥:
```python
UNSPLASH_ACCESS_KEY = "你的Unsplash Access Key"
UNSPLASH_ROOT = "https://api.unsplash.com"
ALI_API_KEY = "你的阿里云API Key" 
COZE_AUTH_TOKEN = "你的Coze API Token"
```

注意：config.py 文件包含敏感信息，已被添加到 .gitignore 中，不会被提交到版本控制系统。

## 运行程序

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行程序:
```bash
python video_clip.py
```

3. 根据提示输入视频URL和是否需要背景音乐

## 注意事项

- 请确保已复制 config.py.copy 到 config.py 并正确配置所有API密钥
- 不要直接修改 config.py.copy，它仅作为配置文件模板
- 临时文件会保存在 tmp 目录下
- 建议使用Python 3.7+版本运行
- 需要确保系统已安装ffmpeg
- 运行 `pip install -r requirements.txt` 前建议先创建并激活虚拟环境
- 如果安装过程中遇到问题，可能需要先安装系统级依赖（如 ffmpeg）
- Windows 用户可能需要额外安装 Visual C++ Build Tools