import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          name: 'audioInput',
          component: () => import('../views/AudioInput.vue')
        },
        {
          path: 'subtitle',
          name: 'subtitle',
          component: () => import('../views/SubtitleConfirm.vue')
        },
        {
          path: 'material',
          name: 'material',
          component: () => import('../views/MaterialConfig.vue')
        },
        {
          path: 'generating',
          name: 'generating',
          component: () => import('../views/VideoGenerating.vue')
        },
        {
          path: 'download',
          name: 'download',
          component: () => import('../views/VideoDownload.vue')
        }
      ]
    }
  ]
})

export default router 