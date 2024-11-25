import hashlib
import random
import shutil
from moviepy.editor import *
import requests
import os
import time
from http import HTTPStatus
import json
import dashscope
from openai import OpenAI
import re  # 确保导入re模块
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
from config import *

current_file_path = os.path.abspath(__file__)
root_directory = os.path.dirname(current_file_path)
print("当前应用根目录:", root_directory)


def get_caption(audio_url):
    # 获取语音识别结果
    transcribe_audio_res = get_transcription(audio_url)
    # 提取句子
    return extract_sentences_without_words(transcribe_audio_res)



def split_text_list_by_length(text_list, max_length=2000):
    text_list_group = []  # 存放分组后的列表
    current_group = []    # 当前分组
    current_length = 0    # 当前分组的总长度

    for text in text_list:
        text_length = len(text)
        # 如果加上当前文本长度超过限制，则新开一个分组
        if current_length + text_length > max_length:
            text_list_group.append(current_group)  # 保存当前分组
            current_group = []  # 开始新的分组
            current_length = 0  # 重置当前长度

        # 添加当前文本到分组
        current_group.append(text)
        current_length += text_length

    # 将最后一个分组加入结果（如果有内容）
    if current_group:
        text_list_group.append(current_group)

    return text_list_group

def optimize_sentence(title, sentences_list):
    """
        1. 将sentences_list的text提取出来传入大语言模型修改错别字后，重新将修改好的text替换到sentences_list中
        2. 将修改好的text传入大语言模型提取关键字，并重新将提取的关键字替换到sentences_list中
        3. 传入大语言模型的text上下文不得超过2000字，要适当的截断
    """
    i = 0
    text_list = [sentence["text"] for sentence in sentences_list]
    # 根据text_list里面的字符串长度总长度，如果超过list总字符长度超过2000则进行list分组
    text_list_group = split_text_list_by_length(text_list, 2000)

    for text_list in text_list_group:
        text_list_str = "\n".join(text_list)
        optimize_prompt = f"""
这是一段关于《{title}》的视频的字幕列表，其中可能有很多错别字，也有很多无意义的语气词，

## 要求如下：
1. 请结合全文主体内容推断错别字并修复它们后按原格式原顺序返回
2. 要求返回{len(text_list)}行数据，在一行字幕中(没有换行符)，不管内容多长，返回内容都不需要换行，直接在一行中返回。行与行之间不需要空白行。
3. 只需按示例返回要求内容，其他无需返回。

## 示例
《金刚经》当中三句一，各位听说过吧？”修正之后返回示例如下：
《金刚经》当中有三句义，各位听说过吧？

## 字幕内容如下：
{text_list_str}

## 返回内容({len(text_list)}行)：
"""
        optimize_prompt_by_llm = prompt_by_llm(optimize_prompt)
        # 将结果按换行符分割成列表
        optimize_prompt_by_llm_list = optimize_prompt_by_llm.split("\n")
        # 将optimize_prompt_by_llm_list中的每个元素放入sentences_list的text字段中
        for optimize_sentence in optimize_prompt_by_llm_list:
            if(i < len(sentences_list)):
                sentences_list[i]["keys"] = optimize_sentence
                i += 1
            else:
                break
    return sentences_list


def keys_sentence(title, sentences_list):
    """
        1. 将sentences_list的text提取出来传入大语言模型修改错别字后，重新将修改好的text替换到sentences_list中
        2. 将修改好的text传入大语言模型提取关键字，并重新将提取的关键字替换到sentences_list中
        3. 传入大语言模型的text上下文不得超过2000字，要适当的截断
    """
    j = 0
    text_list = [sentence["text"] for sentence in sentences_list]
    # 根据text_list里面的字符串长度总长度，如果超过list总字符长度超过2000则进行list分组
    text_list_group = split_text_list_by_length(text_list, 2000)

    for text_list in text_list_group:
        text_list_str = "\n".join(text_list)
        keys_prompt = f"""
这是一段关于《{title}》的视频的字幕列表，现要为每一行字幕检索相关的视频剪辑画面素材，要求如下：
1. 用英文为每一行字幕提取相应的关键词，便于在图片库中检索相关图片检索
2. 关键词要足够简洁，具代表性即可，不要过于复杂，不要太长。
3. 按行逐一返回字幕对应的关键词，一行字幕对应一行关键词，且顺序一致，关键词用逗号分割。
4. 要求返回{len(text_list)}行数据，在一行字幕中(没有换行符)，不管内容多长，关键词都不需要换行，直接在一行中返回。行与行之间不需要空白行。
5. 只需按示例返回要求内容，其他无需返回。

## 示例
《金刚经》当中三句义，各位听说过吧？”取关键词返回示例如下：
Diamond Sutra, three sentences

## 字幕内容如下：
```
{text_list_str}
```

## 返回内容({len(text_list)}行)：
"""
        keys_prompt_by_llm = prompt_by_llm(keys_prompt)
        # 将结果按换行符分割成列表
        keys_prompt_by_llm_list = keys_prompt_by_llm.split("\n")
        # 将keys_prompt_by_llm_list中的每个元素放入sentences_list的keys字段中
        for keys_sentence in keys_prompt_by_llm_list:
            if(j < len(sentences_list)):
                sentences_list[j]["keys"] = keys_sentence
                j += 1
            else:
                break

    return sentences_list



def prompt_by_llm(prompt):
     # 大语言模型改错别字优化句子和提取关键字
    client = OpenAI(
        api_key=ALI_API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-max-latest",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}],
    )

    model_dump_json = completion.model_dump_json()
    print(model_dump_json)
    model_dump_json = json.loads(model_dump_json)
    reseponse_content = model_dump_json["choices"][0]["message"]["content"]
    print(f"prompt_by_llm {prompt}  \n reseponse_content>>>\n" + reseponse_content)

    # 判断如果是```json开头的markdown格式，则提取json
    json_data = re.search(r'```json\n(.*?)```', model_dump_json["choices"][0]["message"]["content"], re.DOTALL)
    if json_data:
        json_data = json_data.group(1).strip()
    else:
        return reseponse_content


# Function to extract sentences without the "words" field
def extract_sentences_without_words(transcribe_response):
    sentences_list = []
    transcripts = transcribe_response.get("transcripts", [])
    for transcript in transcripts:
        sentences = transcript.get("sentences", [])
        for sentence in sentences:
            # Create a copy of the sentence dictionary without "words"
            sentence_copy = {k: v for k, v in sentence.items() if k != "words"}
            sentences_list.append(sentence_copy)
    return sentences_list


# 语音识别
def get_transcription(file_url, timeout=60):
    dashscope.api_key = ALI_API_KEY
    task_response = dashscope.audio.asr.Transcription.async_call(
        model='paraformer-v2',
        file_urls=[file_url],
        language_hints=['zh', 'en']  # “language_hints”只支持paraformer-v2和paraformer-realtime-v2模型
    )
    transcribe_response = dashscope.audio.asr.Transcription.wait(task=task_response.output.task_id)
    if transcribe_response.status_code == HTTPStatus.OK:
        response_str = json.dumps(transcribe_response.output, indent=4, ensure_ascii=False)
        print(f'transcription done! {response_str}')
        # response_str转成json
        response_json = json.loads(response_str)
        if response_json["task_status"] != 'SUCCEEDED':
            raise Exception(f"transcription FAIL: {response_json}")
        return fetch_transcription_content(response_json["results"][0]["transcription_url"])
    else:
        raise Exception(f"Failed to get transcription: {transcribe_response.status_code}")


def fetch_transcription_content(transcription_url):
    response = requests.get(transcription_url)
    if response.status_code != HTTPStatus.OK:
        raise Exception(f"Failed to fetch transcription content: {response.status_code}")
    fetch_transcription_content = response.json()
    print(f"fetch_transcription_content>>>{fetch_transcription_content}")
    return fetch_transcription_content


def download_vedio(url):
    """
    运行指定的工作流。
    """
    headers = {
        "Authorization": f"Bearer {COZE_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    parameters = {"url": url}
    # 构造请求体
    payload = {
        "workflow_id": "7437454680492359706",  # 将数字改为字符串
        "parameters": parameters
    }

    # 打印请求信息用于调试
    print("Request Headers:", headers)
    print("Request Payload:", json.dumps(payload, ensure_ascii=False))

    # 发送 POST 请求
    response = requests.post('https://api.coze.cn/v1/workflow/run', headers=headers, json=payload)
    
    # 打印完整的响应内容
    print(f"Response Status: {response.status_code}")
    print(f"Response Content: {response.text}")
    
    # 处理响应
    if response.status_code == 200:
        response_data = response.json()["data"]
        print("成功运行工作流！响应数据：", json.dumps(response_data, ensure_ascii=False))
        response_data_json = json.loads(response_data)
        return response_data_json["output"]
    else:
        print(f"请求失败，状态码: {response.status_code}，响应内容: {response.text}")
        return ""


# 获取 Unsplash 图片 URL
def get_images_from_unsplash(query, count=1):
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "per_page": count  # 根据传入的count获取指定数量的图片
    }
    response = requests.get(f"{UNSPLASH_ROOT}/search/photos", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            #print(f"成功获取关键词 '{query}' 的图片 {data['results']}")
            # 将图片本地，并返回本地图片路径列表
            image_urls = [result['urls']['regular'] for result in data['results']]  # 返回图片URL列表
            # for i, image_url in enumerate(image_urls):
            #     image_path = f"{clip_tmp_dir}/{int(time.time())}_{query.replace(' ', '_')}_{i}.jpg"
            #     download_image(image_url, image_path)
            #     image_paths.append(image_path)
            # download_urls = [result['links']['download_location'] for result in data['results']]  # 返回图片URL列表
            # for i,download_url in enumerate(download_urls):
            #     image_path = f"{clip_tmp_dir}/{int(time.time())}_{query.replace(' ', '_')}_{i}.jpg"
            #     download_unsplash_image(download_url, image_path)
            #     image_paths.append(image_path)
            return image_urls
        else:
            print(f"未找到与查询词 '{query}' 相关的图片。")
            return []
    else:
        print(f"Error: {response.status_code}")
        return []


# 保存图片到本地
def download_unsplash_image(download_location, filename):
    """
    从Unsplash下载图片的两步流程：
    1. 请求download_location获取实际的下载URL
    2. 下载实际的图片
    """
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    # 第一步：获取实际的下载URL
    response = requests.get(download_location, headers=headers)
    if response.status_code != 200:
        print(f"Error getting download URL: {response.status_code}")
        return
    
    try:
        # 从响应中获取实际的图片URL
        download_data = response.json()
        actual_image_url = download_data.get('url')
        if not actual_image_url:
            print("No download URL found in response")
            return
            
        # 第二步：下载实际的图片
        print(f"下载图片：{actual_image_url}")
        image_response = requests.get(actual_image_url)
        if image_response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(image_response.content)
            print(f"Image {filename} downloaded successfully.")
        else:
            print(f"Error downloading image {filename}: {image_response.status_code}")
            
    except Exception as e:
        print(f"Error processing download: {str(e)}")


# 保存图片到本地
def download_images_for_caption_list(caption_list, clip_tmp_dir):
    for caption in caption_list:
        image_paths = []
        for i, url in enumerate(caption["image_urls"]):
            image_path = download_image(url, clip_tmp_dir)
            if image_path != '':
                image_paths.append(image_path)
        caption["image_paths"] = image_paths
    return caption_list


# 保存图片到本地
def download_image(url, clip_tmp_dir):
    if url == '':
        return ""
    response = requests.get(url)
    if response.status_code == 200:
        filename = f"{clip_tmp_dir}/{int(time.time())}_{hashlib.md5(url.encode('utf-8')).hexdigest()}_{random.randint(0, 1000000)}.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Download Image from {url} to {filename} successfully.")
        return filename
    else:
        print(f"Error downloading Image from {url} to {filename}: {response.status_code}")
        return ""


# 创建字幕片段
def create_caption_clip(caption):
    duration = (caption["end_time"] - caption["begin_time"]) / 1000
    text_clip = TextClip(caption["text"], fontsize=24, color='white')
    text_clip = text_clip.set_duration(duration).set_position("bottom").set_opacity(0.8)
    return text_clip


def extract_audio_from_url(url, clip_tmp_dir="clip_tmp_" + str(time.time()) ):
    """从URL中提取音频，支持视频和音频文件"""
    temp_path = f"{clip_tmp_dir}/temp_media_{int(time.time())}"
    os.makedirs(clip_tmp_dir, exist_ok=True)
    audio_temp_path = f"{temp_path}.mp3"
    wav_temp_path = f"{temp_path}.wav"
    
    try:
        # 添加常用的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.bilibili.com/'  # 如果是B站视频，添加对应的Referer
        }
        
        # 下载文件
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code != HTTPStatus.OK:
            # 如果第一次请求失败，尝试不同的请求头
            alternative_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=alternative_headers, stream=True)
            if response.status_code != HTTPStatus.OK:
                raise Exception(f"Failed to download media file: {response.status_code}")
        
       
        media_temp_path = f"{temp_path}_original.mp4"
        print(f"下载文件成功，开始保存到本地：{media_temp_path}")
        # 使用流式下载
        with open(media_temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"下载文件成功，保存到本地：{media_temp_path}")
        # 尝试作为视频文件加载
        try:
            video = VideoFileClip(media_temp_path)
            # 如果是视频文件，提取频
            audio = video.audio
            audio.write_audiofile(audio_temp_path)
            video.close()
            print(f"创建视频剪辑成功，视频路径：{media_temp_path}, 提取音频路径：{audio_temp_path}")
        except Exception as e:
            print(f"视频处理失败，尝试作为音频文件处理: {str(e)}")
            # 如果不是视频文件，直接作为音频文使用
            os.rename(media_temp_path, audio_temp_path)
        
        # 尝试将 MP3 转换为 WAV
        try:
            os.system(f"ffmpeg -i {audio_temp_path} {wav_temp_path}")
            print(f"ffmpeg -i {audio_temp_path} {wav_temp_path} success!!!")
            return wav_temp_path
        except Exception as e:
            print(f"转换音频格式时出错: {str(e)}")
            # 如果转换失败，返回 MP3 文件
            return audio_temp_path
            
    except Exception as e:
        print(f"处理媒体文件时出错: {str(e)}")
        # 清理临时文件
        for path in [audio_temp_path, wav_temp_path]:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        raise e


def create_blurred_background(image_path, blur_amount=5):
    """创建模糊背景"""
    # 使用 PIL 打开图片
    with Image.open(image_path) as img:
        # 调整图片大小，保持高度为1920
        aspect_ratio = img.size[0] / img.size[1]
        new_height = 1920
        new_width = int(new_height * aspect_ratio * 1.1)  # 放大1.1倍
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 应用模糊效果
        blurred = img.filter(ImageFilter.GaussianBlur(blur_amount))
        
        # 保存模糊后的图片
        blur_path = image_path.rsplit('.', 1)[0] + '_blurred.jpg'
        blurred.save(blur_path)
        return blur_path


def prepare_image_materials(caption_list):
    """
    为每个字幕准备图片素材
    返回添加了 image_paths 字段的 caption_list
    """
    for i, caption in enumerate(caption_list):
        # 计算这个字幕片段的时长（秒）
        if i == 0:
            start_time = 0
        else:
            start_time = caption["begin_time"] / 1000

        if i < len(caption_list) - 1:
            end_time = caption_list[i + 1]["begin_time"] / 1000
        else:
            end_time = caption["end_time"] / 1000

        duration = end_time - start_time
        
        # 根据时长确定需要的图片数量（每3秒一张图）
        image_count = max(1, int(duration / 3))
        
        # 获取多张图片，优先使用keys，如果keys不存在或为空则使用text
        query = caption.get("keys") if caption.get("keys") and caption["keys"].strip() else caption["text"]
        image_urls = get_images_from_unsplash(query, image_count)
        
        caption["image_urls"] = image_urls
        caption["start_time"] = start_time
        caption["duration"] = duration
        
    return caption_list

def prepare_audio_material(audio_url, clip_tmp_dir):
    """
    准备音频素材
    返回本地音频文件路径
    """
    return extract_audio_from_url(audio_url, clip_tmp_dir)

def create_cover(title, cover_image_path, output_size=(1080, 1920)):
    # 打开封面图片
    cover = Image.open(cover_image_path)
    
    # 调整图片大小以适应视频尺寸
    cover = cover.resize(output_size, Image.Resampling.LANCZOS)
    
    # 创建绘图对象
    draw = ImageDraw.Draw(cover)
    
    # 尝试多个字体，确保至少有一个可用
    font = None
    font_size = 100
    try:
        # 尝试使用系统字体
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS
            "C:\\Windows\\Fonts\\msyh.ttc",  # Windows
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
                
        if font is None:
            font = ImageFont.load_default()
            font_size = 40
            
    except Exception as e:
        print(f"加载字体出错: {str(e)}")
        font = ImageFont.load_default()
        font_size = 40

    # 设置最大宽度（图片宽度的80%）
    max_width = int(output_size[0] * 0.8)
    
    # 处理中文和英文混合文本
    lines = []
    current_line = ""
    
    # 按字符遍历文本
    for char in title:
        test_line = current_line + char
        # 获取当前测试行的宽度
        test_width = draw.textlength(test_line, font=font)
        
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
    
    # 添加最后一行
    if current_line:
        lines.append(current_line)
    
    # 计算所有行的总高度
    line_height = font_size * 1.5  # 行高为字体大小的1.5倍
    total_height = len(lines) * line_height
    
    # 计算起始y坐标（居中）
    y = (output_size[1] - total_height) // 2
    
    # 绘制每一行文字
    for line in lines:
        # 计算当前行的度和x坐标（居中）
        line_width = draw.textlength(line, font=font)
        x = (output_size[0] - line_width) // 2
        
        # 添加文字阴影效果
        shadow_offset = 3
        draw.text((x + shadow_offset, y + shadow_offset), line.strip(), font=font, fill='black')
        
        # 添加主要文字
        draw.text((x, y), line.strip(), font=font, fill='white')
        
        # 移动到下一行
        y += line_height
    
    return np.array(cover)

def create_background_music(bg_music_path, video_duration, volume=0.3):
    """
    创建背景音乐
    Args:
        bg_music_path: 背景音乐路径，可以为None
        video_duration: 视频时长
        volume: 音量大小，默认0.3
    Returns:
        AudioClip or None: 返回处理后的背景音乐片段，如果没有背景音乐则返回None
    """
    if not bg_music_path or not os.path.exists(bg_music_path):
        return None
        
    try:
        # 加载背景音乐
        bg_music_clip = AudioFileClip(bg_music_path).volumex(volume)
        
        # 循环播放背景音乐直到视频结束
        bg_music_clips = []
        while sum(clip.duration for clip in bg_music_clips) < video_duration:
            bg_music_clips.append(bg_music_clip)
        return concatenate_audioclips(bg_music_clips).subclip(0, video_duration)
    except Exception as e:
        print(f"处理背景音乐时出错: {str(e)}")
        return None

def create_video(title, cover_image_path, caption_list, audio_path, clip_tmp_dir, bg_music_path=None):
    """
    创建视频
    Args:
        title: 视频标题
        cover_image_path: 封面图片路径
        caption_list: 字幕列表
        audio_path: 音频路径
        clip_tmp_dir: 临时目录
        bg_music_path: 背景音乐路径，可选参数
    Returns:
        tuple: (视频路径, 预览图路径)
    """
    video_clips = []
    
    # 获取总时长
    total_duration = caption_list[-1]["end_time"] / 1000

    # 创建背景视频
    background = ColorClip(size=(1080, 1920), color=(0, 0, 0))
    background = background.set_duration(total_duration)

    # 处理每个字幕片段
    for caption in caption_list:
        if not caption.get("image_paths"):
            continue
            
        # 计算每张图片的显示时长
        image_duration = caption["duration"] / len(caption["image_paths"])
        
        # 处理每张图片
        for j, image_path in enumerate(caption["image_paths"]):
            # 创建模糊背景
            blurred_bg_path = create_blurred_background(image_path)
            background_clip = ImageClip(blurred_bg_path)
            
            # 创建主图片剪辑
            image_clip = ImageClip(image_path)
            image_clip = image_clip.resize(width=1080)
            
            # 计算这张图片的开始时间
            image_start_time = caption["start_time"] + (j * image_duration)
            
            # 设置背景和主图片的时长和开始时间
            background_clip = (background_clip
                             .set_position('center')
                             .set_start(image_start_time)
                             .set_duration(image_duration))
            
            image_clip = (image_clip
                        .set_position('center')
                        .set_start(image_start_time)
                        .set_duration(image_duration))
            
            # 添加到视频剪辑列表
            video_clips.extend([background_clip, image_clip])
            
            # 删除临时的模糊背景图片
            os.remove(blurred_bg_path)

        # 创建字幕剪辑
        try:
            # 创建带描边的文字剪辑
            txt_clip = TextClip(
                caption["text"],
                fontsize=70,
                color='white',
                bg_color='transparent',
                font='PingFang-SC-Regular',
                size=(900, None),
                method='caption',
                stroke_color='black',
                stroke_width=2.5
            )

            # 创建阴影效果
            shadow = TextClip(
                caption["text"],
                fontsize=70,
                color='black',
                bg_color='transparent',
                font='PingFang-SC-Regular',
                size=(900, None),
                method='caption',
            ).set_opacity(0.3)

            # 设置位置和时间
            shadow = shadow.set_position(('center', 1402))
            txt_clip = txt_clip.set_position(('center', 1400))
            
            duration = caption["duration"]
            start_time = caption["start_time"]
            
            txt_clip = txt_clip.set_start(start_time).set_duration(duration)
            shadow = shadow.set_start(start_time).set_duration(duration)

            video_clips.extend([shadow, txt_clip])

        except Exception as e:
            print(f"创建字幕时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    # 创建主视频
    main_video = CompositeVideoClip([background] + video_clips, size=(1080, 1920))
    
    # 创建封面
    cover_frame = create_cover(title, cover_image_path)
    cover_clip = (ImageClip(cover_frame)
                 .set_duration(1)  # 封面显示1秒
                 .crossfadeout(0.5))  # 添加0.5秒的淡出效果
    
    # 给主视频添加淡入效果
    main_video = main_video.crossfadein(1)

    # 添加音频
    audio_clip = AudioFileClip(audio_path)
    
    # 处理背景音乐
    bg_music_clip = create_background_music(bg_music_path, audio_clip.duration)

    # 合并音频和背景音乐
    if bg_music_clip:
        final_audio = CompositeAudioClip([audio_clip, bg_music_clip])
    else:
        final_audio = audio_clip
    
    # 先连接封面和主视频
    final_video = concatenate_videoclips([cover_clip, main_video])
    
    # 然后设置最终的音频
    final_video = final_video.set_audio(final_audio)
    
    # 生成输出文件名（使用时间戳和标题的哈希值）
    file_basename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
    
    # 保存预览图（使用封面帧）
    preview_image_path = f"{clip_tmp_dir}/{file_basename}_preview.jpg"
    Image.fromarray(cover_frame).save(preview_image_path)
    
    # 保存视频
    output_path = f"{clip_tmp_dir}/{file_basename}.mp4"
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        preset="medium",
        bitrate="1000k",
        audio_codec="aac",
        audio_bitrate="128k",
        threads=8,
        ffmpeg_params=[
            "-crf", "28",
            "-movflags", "+faststart",
            "-profile:v", "main",
            "-level", "3.1"
        ]
    )
    
    print(f"视频已保存到: {output_path}")
    print(f"预览图已保存到: {preview_image_path}")
    
    return output_path, preview_image_path

def create_video_with_captions(title, caption_list, audio_url, bg_music_path=None):
    """
    主函数：协调整个视频制作流程
    Args:
        title: 视频标题
        caption_list: 字幕列表
        audio_url: 音频URL
        bg_music_path: 背景音乐路径，可选参数
    """
    # 创建临时目录
    clip_tmp_dir = f"{root_directory}/tmp/clip_tmp_{int(time.time())}"
    os.makedirs(clip_tmp_dir, exist_ok=True)
    
    try:
        # 大语言模型改错别字优化句子
        caption_list = optimize_sentence(title, caption_list)
        # 大语言模型提取关键字
        caption_list = keys_sentence(title, caption_list)
        # 1. 准备图片素材url列表
        caption_list = prepare_image_materials(caption_list)
        # 2. 下载图片素材
        caption_list = download_images_for_caption_list(caption_list, clip_tmp_dir)
        # 3. 下载并提取音频素材
        audio_path = extract_audio_from_url(audio_url, clip_tmp_dir)
        # 4. 准备封面图片
        cover_image_urls = get_images_from_unsplash(title)
        if len(cover_image_urls) > 0:
            cover_image_url = cover_image_urls[0]
            cover_image_path = download_image(cover_image_url, clip_tmp_dir)
        else:
            cover_image_path = ""
        
        print(f"标题：{title}, \n封面图片路径：{cover_image_path}, \n音频路径：{audio_path}, \n临时目录：{clip_tmp_dir}, \n字幕列表：{caption_list}")
        # 5. 制作视频
        output_path, preview_image_path = create_video(title, cover_image_path[0], caption_list, audio_path, clip_tmp_dir, bg_music_path)
        # 6. 返回视频路径
        return output_path, preview_image_path
    finally:
        # 清理临时目录
        # if os.path.exists(clip_tmp_dir):
        #     shutil.rmtree(clip_tmp_dir)
        pass


if __name__ == '__main__':
    url = input("请输入一个视频URL: ")
    # 从控制台让用户选择是否需要背景音乐
    bg_music_choice = input("是否需要背景音乐？(y/n): ")
    if bg_music_choice == "y":
        bg_music_path = os.path.join(root_directory, "static", "bg_music.mp3")
    else:
        bg_music_path = None
    # 从控制台中输入一个音频文件的URL
    vedeo_info = download_vedio(url)
    # 音视频URL
    audio_url = vedeo_info["url"]
    # 标题
    title = vedeo_info["title"]
    # 获取字幕
    caption_list = get_caption(title, audio_url)
    # 生成带音频的视频
    create_video_with_captions(title, caption_list, audio_url, bg_music_path)
