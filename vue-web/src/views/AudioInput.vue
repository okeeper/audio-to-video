<template>
  <div class="audio-input">
    <el-card class="input-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">输入视频网页地址链接</h2>
          <p class="description">
            请输入有效的视频网页链接，视频连接支持抖音、快手、B站等平台
          </p>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" class="input-form">
        <el-form-item prop="videoUrl">
          <el-input
            v-model="form.videoUrl"
            placeholder="请输入音频链接，例如：https://www.bilibili.com/video/BV1bG411p7Wy"
            clearable
            size="large"
            class="url-input"
          >
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="action-item">
          <el-button 
            type="primary" 
            size="large" 
            @click="validateAndNext"
            class="next-button"
          >
            下一步
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="tips">
        <h3>使用说明：</h3>
        <ul>
          <li>确保视频网页地址可以公开访问</li>
          <li>建议视频时长在1-10分钟之间,否则容易超时失败</li>
          <li>视频视频质量将影响字幕识别准确度</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useVideoStore } from '../stores/video'
import { ElMessage } from 'element-plus'
import { Document, ArrowRight } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'

const router = useRouter()
const videoStore = useVideoStore()
const formRef = ref<FormInstance>()

const form = reactive({
  videoUrl: ''
})

const rules = {
  videoUrl: [
    { required: true, message: '请输入音频或视频链接', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ]
}

const validateAndNext = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        videoStore.setVideoUrl(form.videoUrl)
        await router.push('/subtitle')
      } catch (error) {
        ElMessage.error('跳转失败，请重试')
      }
    }
  })
}
</script>

<style scoped>
.audio-input {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  box-sizing: border-box;
}

.input-card {
  width: 100%;
  margin-top: 0;
  background: #fff;
  border-radius: 12px;
  box-sizing: border-box;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.card-header {
  text-align: center;
  padding: 0.8rem 0;
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

.input-form {
  margin: 1rem 0;
}

.url-input {
  width: 100%;
}

.url-input :deep(.el-input__wrapper) {
  padding: 0 1rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.url-input :deep(.el-input__inner) {
  font-size: 1rem;
  height: 42px;
}

.action-item {
  margin-top: 1.5rem;
  text-align: center;
}

.next-button {
  width: 180px;
  height: 42px;
  font-size: 1rem;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  border: none;
  transition: all 0.3s ease;
}

.next-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
}

.tips {
  margin-top: 1rem;
  padding: 0.8rem;
  background: #f1f5f9;
  border-radius: 8px;
  color: #64748b;
}

.tips h3 {
  color: #1e293b;
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
}

.tips ul {
  padding-left: 1.2rem;
  margin: 0;
  line-height: 1.6;
  font-size: 0.9rem;
}

.tips li {
  margin: 0.3rem 0;
}

:deep(.el-card__header) {
  padding: 0.8rem;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.el-card__body) {
  padding: 1rem;
}
</style> 