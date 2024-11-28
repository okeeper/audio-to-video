import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getConfig } from '@/config'

const api = axios.create({
  baseURL: getConfig().apiBaseUrl,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
})

api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求错误，未找到该资源')
          break
        case 500:
          ElMessage.error('服务器端出错')
          break
        default:
          ElMessage.error('连接错误')
      }
    } else {
      if (error.message.includes('Network Error')) {
        ElMessage.error('网络错误，请检查您的网络连接')
      } else {
        ElMessage.error('请求超时，请重试')
      }
    }
    return Promise.reject(error)
  }
)

interface AudioData {
  url: string
  title?: string
}

interface CaptionItem {
  text: string
  begin_time: number
  end_time: number
  keys?: string
  image_urls?: string[]
}

interface VideoRequest {
  audio_data: AudioData
  caption_list: CaptionItem[]
  bg_music_path?: string
}

interface VideoInfo {
  title?: string
  url?: string
  duration?: number
  // 其他可能的视频信息字段
}

interface CaptionsResponse {
  caption_list: CaptionItem[]
  audio_data?: VideoInfo
}

export const videoApi = {
  // 获取字幕
  getCaptions(videoUrl: string) {
    return api.post<CaptionsResponse>('/api/v1/captions', {
      vedeo_url: videoUrl
    })
  },
  
  // 获取推荐素材
  getImageMaterials(data: {
    caption_list: CaptionItem[]
    audio_data: AudioData
  }) {
    return api.post('/api/v1/image-materials', data, {
      timeout: 600000
    })
  },
  
  // 生成视频
  generateVideo(params: VideoRequest) {
    return api.post('/api/v1/generate-video', params, {
      timeout: 600000
    })
  },
  
  // 预览视频
  previewVideo(previewPath: string) {
    return api.post('/api/v1/preview-video', {
      preview_path: previewPath
    }, {
      responseType: 'blob',
      timeout: 300000
    })
  }
}

// 导出类型定义
export type {
  AudioData,
  CaptionItem,
  VideoRequest,
  VideoInfo,
  CaptionsResponse
} 