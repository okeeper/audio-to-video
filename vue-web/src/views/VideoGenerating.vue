<template>
  <div class="video-generating">
    <el-card class="generating-card">
      <div class="generating-content">
        <div class="status-section">
          <div class="status-icon" :class="{ success: progress === 100 }">
            <el-icon v-if="progress === 100"><Check /></el-icon>
            <div v-else class="processing-icon">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" class="circle-bg"/>
                <circle cx="50" cy="50" r="45" class="circle-progress"/>
              </svg>
            </div>
          </div>

          <div class="status-text">
            <h2>{{ progress === 100 ? '视频生成完成' : '正在生成视频' }}</h2>
            <p class="description">{{ getStatusDescription }}</p>
          </div>

          <div class="progress-info">
            <el-progress 
              :percentage="progress" 
              :status="progress === 100 ? 'success' : ''"
              :stroke-width="8"
              :show-text="false"
            />
            <span class="percentage">{{ progress }}%</span>
          </div>

          <div class="task-list">
            <div 
              v-for="(task, index) in tasks" 
              :key="index"
              class="task-item"
              :class="{ 
                'completed': task.completed,
                'current': task.current
              }"
            >
              <el-icon v-if="task.completed"><Check /></el-icon>
              <el-icon v-else-if="task.current"><Loading /></el-icon>
              <el-icon v-else><Clock /></el-icon>
              <span>{{ task.name }}</span>
            </div>
          </div>

          <div class="action-buttons" v-if="progress === 100">
            <el-button 
              type="primary" 
              size="large"
              @click="downloadVideo"
            >
              下载视频
              <el-icon class="el-icon--right"><Download /></el-icon>
            </el-button>
            
            <el-button 
              plain
              size="large"
              @click="regenerateVideo"
            >
              重新生成
              <el-icon class="el-icon--right"><RefreshRight /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="preview-section" v-if="progress === 100">
          <div class="preview-wrapper">
            <div 
              v-if="!isPlaying" 
              class="video-cover"
              @click="handlePlay"
            >
              <img 
                v-if="previewImageUrl" 
                :src="previewImageUrl" 
                class="preview-image"
                alt="视频预览"
              />
              <div class="play-overlay">
                <el-icon class="play-icon"><VideoPlay /></el-icon>
                <span class="play-text">点击播放预览</span>
              </div>
            </div>
            
            <video 
              v-show="isPlaying"
              ref="videoRef"
              :src="videoUrl"
              controls
              class="video-player"
              @pause="handlePause"
              @ended="handlePause"
            ></video>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVideoStore } from '../stores/video'
import { videoApi } from '../api'
import { ElMessage } from 'element-plus'
import {
  Check,
  Loading,
  Clock,
  Download,
  RefreshRight,
  VideoPlay
} from '@element-plus/icons-vue'
import { getConfig } from '@/config'

const router = useRouter()
const videoStore = useVideoStore()
const progress = ref(0)
const timer = ref<number>()
const videoRef = ref<HTMLVideoElement | null>(null)
const isPlaying = ref(false)
const videoUrl = ref('')
const previewImageUrl = ref('')
const videoBlob = ref<Blob | null>(null)

const tasks = ref([
  { name: '准备素材', completed: false, current: false },
  { name: '合成音频', completed: false, current: false },
  { name: '生成视频', completed: false, current: false },
  { name: '后期处理', completed: false, current: false }
])

const getStatusDescription = computed(() => {
  if (progress.value === 100) {
    return '您的视频已经准备就绪，可以预览和下载'
  }
  const currentTask = tasks.value.find(task => task.current)
  return currentTask ? `正在${currentTask.name}...` : '准备中...'
})

const generateVideo = async () => {
  try {
    const { data } = await videoApi.generateVideo({
      audio_data: {
        url: videoStore.audioUrl,
        title: videoStore.audioTitle
      },
      caption_list: videoStore.materials.map(item => ({
        text: item.subtitle.text,
        begin_time: item.subtitle.beginTime,
        end_time: item.subtitle.endTime,
        start_time: item.subtitle.startTime,
        image_urls: item.recommendImages,
        duration: item.subtitle.duration
      }))
    })
    
    if (data.preview_url) {
      // 这里加上后端baseURL
      videoUrl.value = getConfig().apiBaseUrl + data.preview_url
    }
    if (data.preview_image_url) {
      previewImageUrl.value = getConfig().apiBaseUrl + data.preview_image_url
    }
    
    progress.value = 100
    tasks.value[tasks.value.length - 1].completed = true
    tasks.value[tasks.value.length - 1].current = false
  } catch (error) {
    console.error('生成视频失败:', error)
    ElMessage.error('生成视频失败')
    clearInterval(timer.value)
  }
}

const downloadVideo = () => {
  if (!videoUrl.value) {
    ElMessage.warning('视频还未生成完成')
    return
  }
  
  window.open(videoUrl.value, '_blank')
  ElMessage.success('开始下载视频')
}

const regenerateVideo = async () => {
  progress.value = 0
  tasks.value.forEach(task => {
    task.completed = false
    task.current = false
  })
  
  videoUrl.value = ''
  previewImageUrl.value = ''
  isPlaying.value = false
  
  ElMessage.info('开始重新生成视频')
  await generateVideo()
}

const updateProgress = () => {
  if (progress.value < 95) {
    progress.value += 1
    
    const taskIndex = Math.floor((progress.value / 95) * (tasks.value.length - 1))
    tasks.value.forEach((task, index) => {
      if (index < taskIndex) {
        task.completed = true
        task.current = false
      } else if (index === taskIndex) {
        task.completed = false
        task.current = true
      } else {
        task.completed = false
        task.current = false
      }
    })
  } else {
    clearInterval(timer.value)
  }
}

const handlePause = () => {
  isPlaying.value = false
}

const handlePlay = async () => {
  try {
    if (videoRef.value) {
      isPlaying.value = true
      await videoRef.value.play()
    }
  } catch (error) {
    console.error('视频播放失败:', error)
    ElMessage.error('视频播放失败')
    isPlaying.value = false
  }
}

onMounted(async () => {
  if (!videoStore.materials.length) {
    router.push('/material')
    return
  }
  
  timer.value = setInterval(updateProgress, 100)
  
  await generateVideo()
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped>
.video-generating {
  width: 100%;
}

.generating-card {
  width: 100%;
  margin-top: 0;
  background: #fff;
  border-radius: 12px;
  box-sizing: border-box;
}

.generating-content {
  display: flex;
  gap: 2rem;
  min-height: 600px;
}

.status-section {
  flex: 1;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 320px;
}

.preview-section {
  flex: 1.5;
  padding: 2rem 2rem 2rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 0 12px 12px 0;
}

.preview-wrapper {
  width: 100%;
  max-width: 450px;
  aspect-ratio: 9/16;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  background: #000;
  position: relative;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

.status-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  position: relative;
}

.status-icon.success {
  background: #10b981;
  color: white;
  font-size: 3rem;
}

.processing-icon {
  width: 100%;
  height: 100%;
  animation: rotate 2s linear infinite;
}

.circle-bg,
.circle-progress {
  fill: none;
  stroke-width: 5;
  stroke-linecap: round;
}

.circle-bg {
  stroke: #e2e8f0;
}

.circle-progress {
  stroke: #3b82f6;
  stroke-dasharray: 283;
  stroke-dashoffset: 283;
  animation: progress 2s ease-out infinite;
}

.status-text {
  text-align: center;
  margin-bottom: 2rem;
}

.status-text h2 {
  font-size: 1.5rem;
  color: #1e293b;
  margin: 0 0 0.5rem;
}

.description {
  color: #64748b;
  margin: 0;
}

.progress-info {
  width: 100%;
  max-width: 400px;
  margin-bottom: 2rem;
  position: relative;
}

.percentage {
  position: absolute;
  right: 0;
  top: -1.5rem;
  color: #64748b;
  font-size: 0.9rem;
}

.task-list {
  width: 100%;
  max-width: 400px;
  margin-bottom: 2rem;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  color: #64748b;
  transition: all 0.3s ease;
}

.task-item.completed {
  color: #10b981;
}

.task-item.current {
  color: #3b82f6;
  font-weight: 500;
}

.task-item :deep(.el-icon) {
  font-size: 1.2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: auto;
  padding-top: 2rem;
}

.action-buttons .el-button {
  min-width: 140px;
}

.preview-section {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(10px); }
  to { opacity: 1; transform: translateX(0); }
}

@media (max-width: 1024px) {
  .generating-content {
    flex-direction: column;
  }
  
  .preview-section {
    padding: 0 2rem 2rem 2rem;
    background: none;
  }
  
  .status-section {
    padding-bottom: 1rem;
  }
  
  .preview-wrapper {
    max-width: 360px;
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes progress {
  0% {
    stroke-dashoffset: 283;
  }
  50% {
    stroke-dashoffset: 141;
  }
  100% {
    stroke-dashoffset: 283;
  }
}

.video-cover {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  cursor: pointer;
  transition: all 0.3s ease;
}

.video-cover:hover {
  background: rgba(0, 0, 0, 0.7);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  transition: background-color 0.3s ease;
}

.video-cover:hover .play-overlay {
  background: rgba(0, 0, 0, 0.6);
}

.play-icon {
  font-size: 3rem;
  color: white;
  margin-bottom: 1rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.play-text {
  color: white;
  font-size: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
</style> 