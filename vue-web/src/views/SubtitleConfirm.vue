<template>
  <div class="subtitle-confirm">
    <el-card class="subtitle-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">确认字幕</h2>
          <p class="description">
            请检查并编辑自动识别的字幕内容
          </p>
        </div>
      </template>

      <div v-if="loading" class="loading-wrapper">
        <el-skeleton :rows="6" animated />
        <div class="loading-text">
          <el-icon class="loading-icon"><Loading /></el-icon>
          正在识别音频内容...
        </div>
      </div>

      <template v-else>
        <div class="audio-info">
          <div class="info-item">
            <el-icon><Timer /></el-icon>
            <span>音频时长：{{ formatDuration(audioDuration) }}</span>
          </div>
          <div class="info-item">
            <el-icon><Document /></el-icon>
            <span>字幕数量：{{ subtitles.length }} 条</span>
          </div>
        </div>

        <div class="subtitle-list">
          <el-table 
            :data="subtitles" 
            border 
            stripe
            height="400"
            class="subtitle-table"
          >
            <el-table-column label="序号" type="index" width="60" align="center" />
            <el-table-column label="开始时间" width="120">
              <template #default="{ row }">
                <el-input-number 
                  v-model="row.startTime" 
                  :min="0" 
                  :max="audioDuration"
                  :step="0.1"
                  size="small"
                  controls-position="right"
                />
              </template>
            </el-table-column>
            <el-table-column label="结束时间" width="120">
              <template #default="{ row }">
                <el-input-number 
                  v-model="row.endTime" 
                  :min="row.startTime" 
                  :max="audioDuration"
                  :step="0.1"
                  size="small"
                  controls-position="right"
                />
              </template>
            </el-table-column>
            <el-table-column label="字幕内容">
              <template #default="{ row }">
                <el-input
                  v-model="row.text"
                  type="textarea"
                  :rows="2"
                  resize="none"
                  placeholder="请输入字幕内容"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ $index }">
                <el-button 
                  type="danger" 
                  size="small" 
                  circle
                  @click="removeSubtitle($index)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
                <el-button 
                  type="primary" 
                  size="small" 
                  circle
                  @click="insertSubtitle($index)"
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="actions">
          <el-button @click="router.back()">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <div class="right-buttons">
            <el-button @click="resetSubtitles" plain>
              <el-icon><RefreshRight /></el-icon>
              重新识别
            </el-button>
            <el-button type="primary" @click="handleNext">
              下一步
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVideoStore } from '../stores/video'
import { ElMessage } from 'element-plus'
import {
  Timer,
  Document,
  Loading,
  Delete,
  Plus,
  ArrowLeft,
  ArrowRight,
  RefreshRight
} from '@element-plus/icons-vue'
import { videoApi } from '../api'

const router = useRouter()
const videoStore = useVideoStore()
const loading = ref(true)
const audioDuration = ref(0)
const subtitles = ref<any[]>([])

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const removeSubtitle = (index: number) => {
  subtitles.value.splice(index, 1)
}

const insertSubtitle = (index: number) => {
  const currentSubtitle = subtitles.value[index]
  const nextSubtitle = subtitles.value[index + 1]
  
  const startTime = currentSubtitle.endTime
  const endTime = nextSubtitle 
    ? Math.min(nextSubtitle.startTime, startTime + 5)
    : startTime + 5
  
  const newSubtitle = {
    startTime,
    endTime,
    text: ''
  }
  
  subtitles.value.splice(index + 1, 0, newSubtitle)
}

// 获取字幕数据
const getSubtitles = async () => {
  try {
    loading.value = true
    const { data } = await videoApi.getCaptions(videoStore.videoUrl)
    
    if (data.caption_list && data.caption_list.length > 0) {
      // 更新字幕列表
      subtitles.value = data.caption_list.map(item => ({
        text: item.text,
        startTime: item.begin_time,
        endTime: item.end_time
      }))
      
      // 更新音频时长
      audioDuration.value = Math.max(...data.caption_list.map(item => item.end_time))
      
      // 如果返回了视频信息，也更新到 store 中
      if (data.audio_data) {
        videoStore.setAudioTitle(data.audio_data.title || '')
        videoStore.setAudioUrl(data.audio_data.url || '')
      }
      
      ElMessage.success('字幕识别成功')
    } else {
      ElMessage.warning('未识别到字幕内容')
      subtitles.value = []
    }
  } catch (error) {
    console.error('获取字幕失败:', error)
    ElMessage.error('获取字幕失败，请检查音频链接是否有效')
  } finally {
    loading.value = false
  }
}

// 重新识别字幕
const resetSubtitles = async () => {
  try {
    await getSubtitles()
  } catch (error) {
    ElMessage.error('重新识别失败')
  }
}

// 验证字幕数据
const validateSubtitles = () => {
  if (subtitles.value.length === 0) {
    ElMessage.warning('请至少添加一条字幕')
    return false
  }

  for (let i = 0; i < subtitles.value.length; i++) {
    const subtitle = subtitles.value[i]
    
    if (subtitle.startTime >= subtitle.endTime) {
      ElMessage.warning(`第 ${i + 1} 条字幕的开始时间必须小于结束时间`)
      return false
    }
    
    if (i > 0) {
      const prevSubtitle = subtitles.value[i - 1]
      if (subtitle.startTime < prevSubtitle.endTime) {
        ElMessage.warning(`第 ${i + 1} 条字幕与前一条字幕时间重叠`)
        return false
      }
    }
    
    if (!subtitle.text.trim()) {
      ElMessage.warning(`第 ${i + 1} 条字幕内容不能为空`)
      return false
    }
  }
  
  return true
}

const handleNext = () => {
  if (validateSubtitles()) {
    videoStore.setSubtitles(subtitles.value)
    router.push('/material')
  }
}

onMounted(async () => {
  if (!videoStore.videoUrl) {
    ElMessage.warning('请先输入音频或视频链接')
    router.push('/')
    return
  }
  
  await getSubtitles()
})
</script>

<style scoped>
.subtitle-confirm {
  width: 100%;
}

.subtitle-card {
  width: 100%;
  margin-top: 0;
  background: #fff;
  border-radius: 12px;
  box-sizing: border-box;
}

.card-header {
  text-align: center;
}

.page-title {
  font-size: 1.3rem;
  color: #1e293b;
  margin: 0;
  font-weight: 600;
}

.description {
  color: #64748b;
  margin: 0.3rem 0 0;
  font-size: 0.9rem;
}

.loading-wrapper {
  padding: 2rem;
}

.loading-text {
  text-align: center;
  color: #64748b;
  margin-top: 1rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

.audio-info {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
}

.subtitle-list {
  margin: 1rem 0;
}

.subtitle-table {
  width: 100%;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-textarea__inner) {
  font-size: 0.9rem;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.right-buttons {
  display: flex;
  gap: 1rem;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 