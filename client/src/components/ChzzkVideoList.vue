<script setup lang="ts">
import type { ChzzkVideo } from '@/types/chzzk';

defineProps<{
  videos: ChzzkVideo[]
}>()
const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  } else {
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>

<template>
  <div class="video-list">
    <div v-for="video in videos" :key="video.videoId" class="video-card">
      <div class="thumbnail">
        <img :src="video.thumbnailImageUrl" alt="Video Thumbnail" />
        <span class="duration">{{ formatDuration(video.duration) }}</span>
      </div>
      <div class="video-info">
        <div class="channel">
          <img :src="video.channel.channelImageUrl" alt="Channel Icon" class="channel-icon" />
          <span class="channel-name">{{ video.channel.channelName }}</span>
        </div>
        <h3 class="video-title">{{ video.videoTitle }}</h3>
        <div class="meta">
          <span>{{ formatDate(video.publishDate) }}</span>
          <span class="separator">•</span>
          <span>{{ video.readCount }} views</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.video-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.video-card:hover {
  transform: translateY(-5px);
}

.thumbnail {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 비율 */
}

.thumbnail img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap; /* 텍스트가 줄바꿈되지 않도록 */
}

.video-info {
  padding: 15px;
}

.channel {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.channel-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.channel-name {
  font-size: 14px;
  color: #555;
}

.video-title {
  font-size: 16px;
  margin: 0 0 8px;
  line-height: 1.4;
}

.meta {
  font-size: 12px;
  color: #888;
}

.separator {
  margin: 0 5px;
}
</style>