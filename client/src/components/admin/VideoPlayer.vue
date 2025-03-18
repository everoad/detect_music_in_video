<script setup lang="ts">
import type { ChzzkVideoTimeline } from '@/types/chzzk';
import { computed, nextTick, ref, watch } from 'vue';


const show = ref<boolean>(false)
const videoUrl = ref<string>('')
const videoRef = ref<HTMLVideoElement | null>(null)

const props = defineProps<{
  video: ChzzkVideoTimeline
}>()

watch(() => props.video.videoNo, () => {
  show.value = false
  nextTick(() => {
    videoUrl.value = `/videos/${props.video.videoNo}.mp4`
    show.value = true
  })
}, { immediate: true })

watch(videoRef, () => {
  if (videoRef.value) {
    videoRef.value.volume = 0.5
  }
}, { immediate: true })

function timeAt(time: number) {
  if (videoRef.value) {
    videoRef.value.currentTime = time
    videoRef.value.play()
  }
}

function secondsToTime(seconds: number) {
  const hours = Math.floor(seconds / 3600).toString().padStart(2, '0')
  const minutes = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
  const secs = Math.round(seconds % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}:${secs}`
}

const currentTime = ref<string>('')

function timeupdate() {
  if (videoRef.value) {
    currentTime.value = secondsToTime(videoRef.value.currentTime)
  }
}

function prev() {
  if (videoRef.value) {
    videoRef.value.currentTime = Math.max(videoRef.value.currentTime - 5, 0)
  }
} 

function next() {
  if (videoRef.value) {
    videoRef.value.currentTime = Math.min(videoRef.value.currentTime + 5, videoRef.value.duration)
  }
} 

const size = ref<boolean>(false)
function clickSize() {
  size.value = !size.value
}
defineExpose({
  timeAt
})
</script>

<template>
  <div class="container" v-if="show">
    <div class="header">
      <button @click="clickSize">size</button>
      <div>{{ currentTime }}</div>
      <div>
        <button @click="prev">－</button>
        <button @click="next">＋</button>
      </div>
    </div>
    <video ref="videoRef" controls :class="['webplayer-internal-video', size && 'sm']" @timeupdate="timeupdate" >
      <source :src="videoUrl" type="video/mp4">
    </video>
  </div>
</template>

<style scoped>
.container {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 100;
}
.header {
  padding: 5px 5px;
  background: #333;
  color: white;
  text-align: center;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.webplayer-internal-video {
  width: 600px;
  height: 337.5px;
  transition: 100ms;
  image-rendering: smooth;
}
.webplayer-internal-video.sm {
  width: 300px;
  height: 168.75px;
  transition: 100ms;
}
</style>