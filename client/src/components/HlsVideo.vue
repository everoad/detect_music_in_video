<script setup lang="ts">
import Hls from 'hls.js';
import { onMounted, onUnmounted, ref } from 'vue';

interface VideoAttrs {
  src: string
}

const props = defineProps<VideoAttrs>()
const emits = defineEmits<{
    (e: 'play', payload: Event): void;
    (e: 'pause', payload: Event): void;
    (e: 'ended', payload: Event): void;
    (e: 'timeupdate', payload: Event): void;
    (e: 'loadeddata', payload: Event): void;
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const hlsInstance = ref<Hls | null>(null) // HLS 인스턴스 관리

onMounted(() => {
  if (videoRef.value && Hls.isSupported()) {
    const hls = new Hls({
        xhrSetup: function (xhr, url) {
            console.log('url')
          if (!url.startsWith("http")) {
            xhr.open("GET",  url); // ✅ baseURL 추가
          }
        }
      })
    hlsInstance.value = hls // 인스턴스 저장
    console.log('props.src ', props.src)
    hls.loadSource(props.src)
    hls.attachMedia(videoRef.value)
    hls.on(Hls.Events.MANIFEST_PARSED, () => {
      videoRef.value?.play().catch(err => console.error('Auto-play failed:', err))
    })
    hls.on(Hls.Events.ERROR, (event, data) => {
      console.error('HLS error:', data)
    })
  } else if (videoRef.value && videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
    // HLS 네이티브 지원 (Safari 등)
    videoRef.value.src = props.src
    videoRef.value.play().catch(err => console.error('Auto-play failed:', err))
  }
})

onUnmounted(() => {
  if (hlsInstance.value) {
    hlsInstance.value.destroy() // HLS 인스턴스 정리
    hlsInstance.value = null
  }
})
</script>

<template>
  <div class="video-container">
    <video
      ref="videoRef"
      class="video-player"
      v-bind="$attrs"
      @timeupdate="emits('timeupdate', $event)"
      @loadeddata="emits('loadeddata', $event)"
      @play="emits('play', $event)"
      @pause="emits('pause', $event)"
      @ended="emits('ended', $event)"
    ></video>
  </div>
</template>

<style scoped>
.video-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.video-player {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>