<script setup lang="ts">
import type { ChzzkVideoTimeline } from '@/types/chzzk'
defineProps<{
  videos: ChzzkVideoTimeline[],
  selectedIndex: number
}>()

defineEmits(['select-video'])

const formatDate = (dateStr: string) => {
  if (!dateStr) {
    return ''
  }
  return dateStr.split('T')[0].split('-').join('.')
}

</script>

<template>
  <div class="video-list">
    <h2 class="video-list-title" style="color: var(--color-heading);">비디오 목록</h2>
    <div
      v-for="(video, index) in videos"
      :key="video.videoNo"
      @click="$emit('select-video', index)"
      :class="['video-item', { 'selected': selectedIndex === index }]"
    >
      <div>{{ formatDate(video.publishDate) }}</div>
      <div>{{ video.videoNo }}</div>
      <div>{{ video.deploy ? 'D' : '' }}</div>
    </div>
  </div>
</template>
