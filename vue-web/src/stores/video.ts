import { defineStore } from 'pinia'

interface Subtitle {
  text: string
  startTime: number
  endTime: number
  beginTime: number
  duration: number
}

interface Material {
  subtitle: Subtitle
  imageUrl: string
  recommendImages: string[]
}

export const useVideoStore = defineStore('video', {
  state: () => ({
    videoUrl: '',
    audioUrl: '',
    audioTitle: '',
    subtitles: [] as Subtitle[],
    materials: [] as Material[],
    videoId: '',
    generateProgress: 0,
    downloadUrl: '',
    previewPath: ''
  }),
  
  actions: {
    setVideoUrl(url: string) {
      this.videoUrl = url
    },

    setAudioUrl(url: string) {
      this.audioUrl = url
    },

    setAudioTitle(title: string) {
      this.audioTitle = title
    },
    
    setSubtitles(subtitles: Subtitle[]) {
      this.subtitles = subtitles
    },
    
    setMaterials(materials: Material[]) {
      this.materials = materials
    },
    
    setVideoId(id: string) {
      this.videoId = id
    },
    
    setProgress(progress: number) {
      this.generateProgress = progress
    },
    
    setDownloadUrl(url: string) {
      this.downloadUrl = url
    },
    setPreviewPath(path: string) {
      this.previewPath = path
    }
  }
}) 