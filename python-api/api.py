from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from video_clip import (
    download_image,
    download_images_for_caption_list,
    extract_audio_from_url,
    get_caption,
    get_images_from_unsplash,
    keys_sentence,
    optimize_sentence,
    prepare_image_materials,
    download_vedio,
    create_video
)
import os
import time
import json
import logging
from datetime import datetime
import traceback
import shutil
import hashlib
from fastapi import BackgroundTasks
import asyncio
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/api_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建日志目录
os.makedirs('logs', exist_ok=True)

app = FastAPI(title="视频处理服务")

current_file_path = os.path.abspath(__file__)
root_directory = os.path.dirname(current_file_path)

# 创建静态资源目录
STATIC_DIR = os.path.join(root_directory, "static")
VIDEOS_DIR = os.path.join(STATIC_DIR, "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# 配置静态文件服务
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 添加日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 记录请求开始时间
    start_time = time.time()
    
    # 获取请求体
    body = await request.body()
    body_str = body.decode() if body else ""
    
    # 记录请求信息
    request_info = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host,
        "headers": dict(request.headers),
        "body": body_str if len(body_str) < 1000 else f"{body_str[:1000]}...(truncated)"
    }
    
    logger.info(f"Request: {json.dumps(request_info, ensure_ascii=False, indent=2)}")
    
    try:
        # 执行请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        response_info = {
            "status_code": response.status_code,
            "process_time": f"{process_time:.2f}s",
            "headers": dict(response.headers)
        }
        
        logger.info(f"Response: {json.dumps(response_info, ensure_ascii=False, indent=2)}")
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # 记录错误信息
        error_info = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        logger.error(f"Error: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
        raise HTTPException(status_code=500, detail=str(e))

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量获取 WEB_HOST，如果没有则使用默认值
WEB_HOST = os.getenv("WEB_HOST", "http://localhost:8000")

# 定义请求和响应模型
class VideoData(BaseModel):
    url: str
    title: Optional[str] = None

class CaptionItem(BaseModel):
    text: str
    begin_time: int
    end_time: int
    keys: Optional[str] = None
    image_urls: List[str] = None

class VideoRequest(BaseModel):
    video_data: VideoData
    caption_list: List[CaptionItem]
    bg_music_path: Optional[str] = None

class VideoResponse(BaseModel):
    output_path: str

@app.post("/api/v1/captions", response_model=dict)
async def get_video_captions(request: dict):
    """
    解析视频/音频的字幕信息
    """
    # 获取视频信息
    audio_data = download_vedio(request["vedeo_url"])
    # 获取字幕列表
    caption_list = get_caption(audio_data["url"])
    # 大语言模型改错别字优化句子和提取关键字
    caption_list = optimize_sentence(audio_data["title"], caption_list)
    # 返回字幕列表和标题
    return {"caption_list": caption_list, "audio_data": audio_data}

@app.post("/api/v1/image-materials", response_model=dict)
async def get_image_materials(request: dict):
    """
    根据字幕列表和标题获取图片素材
    """
    # 创建临时目录
    clip_tmp_dir = f"{root_directory}/tmp/clip_tmp_{int(time.time())}"
    os.makedirs(clip_tmp_dir, exist_ok=True)
    
    # 大语言模型提取关键字
    caption_list = keys_sentence(request["audio_data"]["title"], request["caption_list"])
    # 准备图片素材
    caption_list = prepare_image_materials(caption_list)
    return {"caption_list": caption_list, "audio_data": request["audio_data"]}

@app.post("/api/v1/generate-video", response_model=dict)
async def generate_video(request: dict):
    """
    根据字幕和图片素材生成合成视频
    """
    # 创建临时目录
    clip_tmp_dir = f"{root_directory}/tmp/clip_tmp_{int(time.time())}"
    os.makedirs(clip_tmp_dir, exist_ok=True)

    try:
        # 1. 下载图片素材
        caption_list = download_images_for_caption_list(request["caption_list"], clip_tmp_dir)
        # 2. 下载并提取音频素材
        audio_path = extract_audio_from_url(request["audio_data"]["url"], clip_tmp_dir)
        # 3. 准备封面图片
        cover_image_urls = get_images_from_unsplash(request["audio_data"]["title"], clip_tmp_dir)
        cover_image_path = download_image(cover_image_urls[0], clip_tmp_dir) if cover_image_urls else ""
        # 4. 制作视频
        tmp_output_path, preview_image_path = create_video(
            request["audio_data"]["title"],
            cover_image_path,
            request["caption_list"],
            audio_path,
            clip_tmp_dir
        )
        
        # 5. 将视频和预览图移动到静态资源目录
        video_filename = os.path.basename(tmp_output_path)
        preview_filename = os.path.basename(preview_image_path)
        
        # 确保目录存在
        os.makedirs(os.path.join(STATIC_DIR, "previews"), exist_ok=True)
        
        # 移动文件
        static_video_path = os.path.join(VIDEOS_DIR, video_filename)
        static_preview_path = os.path.join(STATIC_DIR, "previews", preview_filename)
        
        shutil.move(tmp_output_path, static_video_path)
        shutil.move(preview_image_path, static_preview_path)
        
        # 6. 生成完整的可访问URL
        video_path = f"/static/videos/{video_filename}"
        preview_path = f"/static/previews/{preview_filename}"
        
        # 使用 urljoin 拼接完整的 URL
        video_url = urljoin(WEB_HOST, video_path)
        preview_url = urljoin(WEB_HOST, preview_path)
        
        return {
            "preview_url": video_url,
            "preview_image_url": preview_url
        }
        
    finally:
        # 清理临时目录
        if os.path.exists(clip_tmp_dir):
            shutil.rmtree(clip_tmp_dir)

async def cleanup_old_videos(days=7):
    """清理指定天数之前的视频文件"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for filename in os.listdir(VIDEOS_DIR):
        if filename.endswith('.mp4'):
            file_path = os.path.join(VIDEOS_DIR, filename)
            file_date = datetime.fromtimestamp(os.path.getctime(file_path))
            
            if file_date < cutoff_date:
                try:
                    os.remove(file_path)
                    print(f"Removed old video: {filename}")
                except Exception as e:
                    print(f"Error removing {filename}: {e}")

@app.on_event("startup")
async def startup_event():
    """应用启动时开始定期清理任务"""
    async def cleanup_task():
        while True:
            await cleanup_old_videos()
            await asyncio.sleep(24 * 60 * 60)  # 每24小时执行一次
    
    asyncio.create_task(cleanup_task())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 