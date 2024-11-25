<template>
  <div class="material-config">
    <el-card class="material-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">配置素材</h2>
          <p class="description">
            为每段字幕选择合适的图片素材，鼠标悬停可预览或更换图片
          </p>
        </div>
      </template>

      <div v-if="loading" class="loading-wrapper">
        <el-skeleton :rows="3" animated />
        <div class="loading-text">
          <el-icon class="loading-icon"><Loading /></el-icon>
          正在获取推荐素材...
        </div>
      </div>

      <template v-else>
        <div class="materials-scroll">
          <div class="materials-container">
            <div 
              v-for="(item, index) in materials" 
              :key="index"
              class="material-item"
            >
              <div class="image-wrapper" @mouseenter="activeIndex = index" @mouseleave="activeIndex = -1">
                <el-image
                  :src="item.imageUrl"
                  fit="cover"
                  :preview-src-list="item.recommendImages"
                >
                  <template #error>
                    <div class="image-error">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
                
                <div class="image-overlay" v-show="activeIndex === index">
                  <div class="overlay-content">
                    <el-upload
                      class="upload-area"
                      action="#"
                      :auto-upload="false"
                      :show-file-list="false"
                      accept="image/*"
                      @change="(file) => handleImageChange(file, index)"
                    >
                      <el-button type="primary" plain>
                        <el-icon><Upload /></el-icon>
                        上传图片
                      </el-button>
                    </el-upload>
                    
                    <div class="recommend-images">
                      <div 
                        v-for="(img, imgIndex) in item.recommendImages" 
                        :key="imgIndex"
                        class="recommend-image"
                        :class="{ active: img === item.imageUrl }"
                        @click="selectImage(index, img)"
                      >
                        <el-image
                          :src="img"
                          fit="cover"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="subtitle-info">
                <div class="time-info">{{ formatTime(item.subtitle.startTime) }}</div>
                <div class="subtitle-text" :title="item.subtitle.text">
                  {{ truncateText(item.subtitle.text, 20) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="actions">
          <el-button @click="router.back()">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button type="primary" @click="handleNext">
            下一步
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
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
  Picture,
  Upload,
  Loading,
  ArrowLeft,
  ArrowRight
} from '@element-plus/icons-vue'
import { videoApi } from '../api/index'

const router = useRouter()
const videoStore = useVideoStore()
const loading = ref(true)
const activeIndex = ref(-1)

interface MaterialItem {
  subtitle: {
    text: string
    startTime: number
    endTime: number
  }
  imageUrl: string
  recommendImages: string[]
}

const materials = ref<MaterialItem[]>([])

const formatTime = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const truncateText = (text: string, length: number) => {
  return text.length > length ? text.slice(0, length) + '...' : text
}

const handleImageChange = (file: any, index: number) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    if (e.target?.result) {
      materials.value[index].imageUrl = e.target.result as string
    }
  }
  reader.readAsDataURL(file.raw)
}

const handleNext = () => {
  if (materials.value.some(item => !item.imageUrl)) {
    ElMessage.warning('请为所有场景选择图片')
    return
  }
  
  videoStore.setMaterials(materials.value)
  router.push('/generating')
}

const selectImage = (index: number, imageUrl: string) => {
  materials.value[index].imageUrl = imageUrl
}

const initMaterials = async () => {
  const subtitles = videoStore.subtitles
  if (!subtitles.length) {
    ElMessage.warning('请先完成字幕确认')
    router.push('/subtitle')
    return
  }

  try {
    const { data } = await videoApi.getImageMaterials({
      caption_list: subtitles.map(item => ({
        text: item.text,
        begin_time: item.startTime,
        end_time: item.endTime
      })),
      audio_data: {
        url: videoStore.audioUrl,
        title: videoStore.audioTitle
      }
    })
    
    materials.value = data.caption_list.map(item => ({
      subtitle: {
        text: item.text,
        beginTime: item.begin_time,
        endTime: item.end_time,
        duration: item.duration,
        startTime: item.start_time
      },
      imageUrl: item.image_urls?.[0] || '',  // 使用第一张图片作为默认图片
      recommendImages: item.image_urls || []  // 保存所有推荐图片
    }))
    
    loading.value = false
  } catch (error) {
    ElMessage.error('获取素材��败')
    loading.value = false
  }
}

onMounted(() => {
  initMaterials()
})
</script>

<style scoped>
.material-config {
  width: 100%;
}

.material-card {
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

.materials-scroll {
  overflow-x: auto;
  padding: 1rem 0;
  margin: 0 -1rem;
}

.materials-container {
  display: flex;
  gap: 1rem;
  padding: 0 1rem;
  min-width: min-content;
}

.material-item {
  width: 240px;
  flex-shrink: 0;
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 180px;
  border-radius: 8px;
  overflow: hidden;
  background: #f1f5f9;
}

.image-wrapper :deep(.el-image) {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.image-wrapper:hover :deep(.el-image) {
  transform: scale(1.05);
}

.image-error {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 2rem;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-wrapper:hover .image-overlay {
  opacity: 1;
}

.subtitle-info {
  margin-top: 0.5rem;
  text-align: center;
}

.time-info {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 0.2rem;
}

.subtitle-text {
  font-size: 0.9rem;
  color: #1e293b;
  line-height: 1.4;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

/* 自定义滚动条样式 */
.materials-scroll {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.materials-scroll::-webkit-scrollbar {
  height: 6px;
}

.materials-scroll::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.materials-scroll::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.overlay-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  padding: 1rem;
}

.recommend-images {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  width: 100%;
}

.recommend-image {
  aspect-ratio: 1;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.recommend-image:hover {
  transform: scale(1.05);
}

.recommend-image.active {
  border-color: #3b82f6;
}

.recommend-image :deep(.el-image) {
  width: 100%;
  height: 100%;
}
</style> 