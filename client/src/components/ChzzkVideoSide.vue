<script setup lang="ts">
import { useChzzkVideo } from '@/composables/use-chzzk-video';
import type { ChzzkVideo } from '@/types/chzzk'
import { formatDate, formatDuration } from '@/utils/common-utils';

const { videos, selectedVideo, setSelectedVideo } = useChzzkVideo()

const isSelected = (video: ChzzkVideo) => {
  return selectedVideo.value?.videoNo === video.videoNo
}
</script>

<template>
  <div class="video-list">
    <div 
      v-for="video in videos" 
      :key="video.videoId" 
      :class="`video-card ${isSelected(video) ? 'selected' : ''}`" 
      @click="setSelectedVideo(video)"
    >
      <!-- 썸네일 -->
      <div class="thumbnail">
        <img :src="video.thumbnailImageUrl" alt="Video Thumbnail" />
        <span class="duration">{{ formatDuration(video.duration) }}</span>
      </div>
      <!-- 비디오 정보 -->
      <div class="video-info">
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
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px;
}

.video-card {
  display: flex;
  /* flex-direction: column; */
  align-items: center;
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  max-width: 400px;
  cursor: pointer;
}
.video-card.selected { background: #e0f0ff; }

.video-card:hover {
  transform: translateY(-3px);
}

.thumbnail {
  position: relative;
  width: 120px;
  padding-top: 67.5px; /* 16:9 비율 */
  flex-shrink: 0;
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
  bottom: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 10px;
}

.video-info {
  padding: 8px;
  flex: 1;
}

.video-title {
  font-size: 14px;
  margin: 0 0 4px;
  line-height: 1.3;
}

.meta {
  font-size: 11px;
  color: #888;
  margin-bottom: 4px;
}

.separator {
  margin: 0 5px;
}

.channel {
  display: flex;
  align-items: center;
  gap: 6px;
}

.channel-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
}

.channel-name {
  font-size: 12px;
  color: #555;
}
</style>