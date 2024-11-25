<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <div class="brand">
          <div class="logo">
            <el-icon class="logo-icon"><VideoCamera /></el-icon>
          </div>
          <h1 class="title">智能视频生成器</h1>
        </div>
        
        <div class="steps-wrapper">
          <el-steps :active="currentStep" finish-status="success" class="steps">
            <el-step 
              v-for="(step, index) in steps" 
              :key="index"
              @click="handleStepClick(step.route, index)"
              :class="{ 'step-clickable': canJumpToStep(index) }"
            >
              <template #icon>
                <div class="custom-icon">
                  <div class="icon-bg">
                    <el-icon><component :is="step.icon" /></el-icon>
                  </div>
                  <div class="step-number">{{ index + 1 }}</div>
                </div>
              </template>
              <template #title>{{ step.title }}</template>
              <template #description>{{ step.description }}</template>
            </el-step>
          </el-steps>
        </div>
      </div>
    </header>
    
    <main class="main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useVideoStore } from '../stores/video'
import {
  VideoCamera,
  Upload,
  Document,
  Picture,
  VideoPlay,
  Download
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const videoStore = useVideoStore()

const steps = [
  { 
    title: '输入音频',
    description: '上传音频链接',
    icon: Upload,
    route: '/'
  },
  { 
    title: '确认字幕',
    description: '编辑识别结果',
    icon: Document,
    route: '/subtitle'
  },
  { 
    title: '配置素材',
    description: '选择图片素材',
    icon: Picture,
    route: '/material'
  },
  { 
    title: '生成视频',
    description: '处理中',
    icon: VideoPlay,
    route: '/generating'
  }
]

const currentStep = computed(() => {
  const routeMap: Record<string, number> = {
    '/': 0,
    '/subtitle': 1,
    '/material': 2,
    '/generating': 3
  }
  return routeMap[route.path] ?? 0
})

const canJumpToStep = (stepIndex: number) => {
  // 只允许跳转到已完成的步骤或当前步骤的下一步
  if (stepIndex <= currentStep.value) return true
  if (stepIndex === currentStep.value + 1) {
    // 检查是否满足进入下一步的条件
    switch (stepIndex) {
      case 1: // 进入字幕确认
        return !!videoStore.audioUrl
      case 2: // 进入素材配置
        return videoStore.subtitles.length > 0
      case 3: // 进入视频生成
        return videoStore.materials.length > 0
      default:
        return false
    }
  }
  return false
}

const handleStepClick = (targetRoute: string, stepIndex: number) => {
  if (canJumpToStep(stepIndex)) {
    router.push(targetRoute)
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
  width: 100%;
}

.header {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  padding: 1rem 0;
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.header-content {
  width: 90%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.logo {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 0.6rem;
  margin-right: 0.8rem;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.logo-icon {
  font-size: 1.8rem;
  color: white;
}

.title {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(to right, #ffffff, #e2e8f0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.steps-wrapper {
  flex: 1;
  padding: 1rem 2rem;
  overflow: visible;
  margin: 0.5rem 0;
}

:deep(.el-steps) {
  justify-content: center;
  min-height: 120px;
}

:deep(.el-step) {
  cursor: default;
  padding-top: 8px;
}

:deep(.el-step__head) {
  margin-top: 8px;
}

:deep(.step-clickable .el-step__head):hover .custom-icon {
  transform: translateY(-2px);
}

.custom-icon {
  position: relative;
  width: 40px;
  height: 40px;
  transition: all 0.3s ease;
  margin: 8px 0;
}

.icon-bg {
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.step-number {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  background: #fff;
  border: 2px solid #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: #3b82f6;
  font-weight: 600;
}

:deep(.el-step__head.is-success .icon-bg) {
  background: linear-gradient(45deg, #10b981, #34d399);
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
}

:deep(.el-step__head.is-success .step-number) {
  border-color: #10b981;
  color: #10b981;
}

:deep(.el-step__head.is-process .icon-bg) {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
  }
}

/* 响应式处理 */
@media (max-width: 768px) {
  .custom-icon {
    width: 32px;
    height: 32px;
  }

  .step-number {
    width: 16px;
    height: 16px;
    font-size: 0.7rem;
  }

  :deep(.el-step__title) {
    font-size: 0.9rem;
  }

  :deep(.el-step__description) {
    font-size: 0.8rem;
  }
}

.main {
  flex: 1;
  padding: 1rem;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  box-sizing: border-box;
  display: flex;
  align-items: flex-start;
}

.footer {
  text-align: center;
  padding: 0.8rem;
  background: white;
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}

@media (max-width: 768px) {
  .header {
    padding: 1rem 0;
  }
  
  .brand {
    margin-bottom: 1rem;
  }
  
  .logo {
    padding: 0.5rem;
  }
  
  .logo-icon {
    font-size: 1.5rem;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .steps-wrapper {
    padding: 1rem;
  }
}

:deep(.el-step__icon-inner) {
  font-size: 1.5rem !important;  /* 增大图标尺寸 */
  color: #ffffff !important;  /* 确保图标颜色为白色 */
}

:deep(.el-step__icon) {
  width: 48px !important;  /* 增大图标容器 */
  height: 48px !important;
  background: rgba(255, 255, 255, 0.2) !important;
  border-radius: 50% !important;
  border: 2px solid rgba(255, 255, 255, 0.9) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-step__head.is-process .el-step__icon) {
  background: rgba(255, 255, 255, 0.3) !important;
  border-color: #ffffff !important;
  box-shadow: 
    0 0 0 4px rgba(255, 255, 255, 0.2),
    0 0 15px rgba(255, 255, 255, 0.3) !important;
}

:deep(.el-step__head.is-finish .el-step__icon) {
  background: #ffffff !important;
  border-color: #ffffff !important;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.4) !important;
}

:deep(.el-step__head.is-finish .el-step__icon-inner) {
  color: #1e40af !important;  /* 使用主题蓝色 */
  font-weight: bold !important;
  font-size: 1.5rem !important;
}

:deep(.el-step__line) {
  background-color: rgba(255, 255, 255, 0.3) !important;
  height: 3px !important;  /* 加粗连接线 */
  top: 24px !important;  /* 调整连接线位置以匹配更大的图标 */
}

:deep(.el-step.is-horizontal .el-step__line) {
  top: 24px !important;
}

:deep(.el-step__head.is-finish .el-step__line) {
  background-color: rgba(255, 255, 255, 0.9) !important;
}

/* 添加悬浮效果 */
:deep(.el-step__head:hover .el-step__icon) {
  transform: scale(1.1);
  box-shadow: 
    0 0 0 6px rgba(255, 255, 255, 0.2),
    0 0 20px rgba(255, 255, 255, 0.4) !important;
}

/* 调整步骤文字的间距 */
:deep(.el-step__main) {
  margin-top: 16px !important;
  padding-top: 8px;
}

:deep(.el-step__title) {
  margin-bottom: 4px !important;
  line-height: 1.4;
}

:deep(.el-step__description) {
  line-height: 1.4;
}

/* 调整移动端样式 */
@media (max-width: 768px) {
  :deep(.el-step__icon) {
    width: 40px !important;
    height: 40px !important;
  }

  :deep(.el-step__icon-inner) {
    font-size: 1.2rem !important;
  }

  :deep(.el-step__line),
  :deep(.el-step.is-horizontal .el-step__line) {
    top: 20px !important;
    height: 2px !important;
  }
}

/* 添加步骤图标的动画效果 */
:deep(.el-step__head.is-process .el-step__icon) {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}
</style> 