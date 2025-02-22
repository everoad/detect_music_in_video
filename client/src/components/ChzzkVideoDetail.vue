<script setup lang="ts">
import { fetchVideoMetadata, fetchVideoTimeline } from '@/api/chzzk.api';
import { useChzzkVideo } from '@/composables/use-chzzk-video';
import type { ChzzkVideoTimeline, MyChzzkVideoMetadata } from '@/types/chzzk';
import { formatDate, formatDuration } from '@/utils/common-utils';
import { nextTick, ref, watch } from 'vue';


const {videos, selectedVideo, setSelectedVideo } = useChzzkVideo()

const videoMetadatas = ref<MyChzzkVideoMetadata[]>([])
const selectedVideoUrl = ref<string | null>(null)
const videoTimeline = ref<ChzzkVideoTimeline>()
const currentSegmentIndex = ref<number>(0) // 현재 재생 중인 구간 인덱스
const isPlaying = ref<boolean>(false) // 재생 상태 추적
const videoRef = ref<HTMLVideoElement | null>(null)

const loadVideoMetadata = async () => {
  if (selectedVideo.value) {
    const { videoId, inKey } = selectedVideo.value
    const metadata = await fetchVideoMetadata(videoId, inKey)
    videoMetadatas.value = metadata.period
      .flatMap((period) => period.adaptationSet)
      .flatMap((adaptationSet) => adaptationSet.representation)
      .filter((representation) => representation.mimeType === "video/mp4")
      .flatMap((representation) => representation.baseURL.map((baseURL) => {
        return ({
          frameRate: representation.frameRate,
          height: representation.height,
          width: representation.width,
          mimeType: representation.mimeType,
          bandwidth: representation.bandwidth,
          baseURL: baseURL.value,
          duration: 0
      })}))
      .sort((a, b) => b.height - a.height)
    
    if (videoMetadatas.value.length > 0) {
      selectedVideoUrl.value = videoMetadatas.value[0].baseURL
    }
  }
}

const loadVideoTimeline = async () => {
  if (selectedVideo.value) {
    const { videoNo } = selectedVideo.value
    const timeline = await fetchVideoTimeline(videoNo)
    // videoTimeline.value = timeline || { videoNo, timelines: [] } // 기본값 설정
    videoTimeline.value = {
      videoNo: videoNo,
      timelines: [
        {"start": 60, "end": 80},
        {"start": 120, "end": 130}
      ]
    }
  }
}

const show = ref<boolean>(false)
watch(selectedVideo, async (newVideo) => {
  if (newVideo) {
    show.value = false
    currentSegmentIndex.value = 0
    isPlaying.value = false
    await Promise.all([loadVideoMetadata(), loadVideoTimeline()])
    nextTick(() => {
      show.value = true
      if (videoRef.value) {
        onPlay()
      }
    })
  }
})

const onTimeUpdate = () => {
  if (videoRef.value && videoTimeline.value && isPlaying.value) {
    const currentTime = videoRef.value.currentTime
    const timelines = videoTimeline.value.timelines
    const currentSegment = timelines[currentSegmentIndex.value]
    if (videoRef.value.currentTime >= videoRef.value.duration) {
      return
    }
    // 현재 구간의 끝에 도달했는지 확인
    if (currentSegment && currentTime >= currentSegment.end) {
      const nextIndex = currentSegmentIndex.value + 1
      if (nextIndex < timelines.length) {
        // 다음 구간으로 이동
        currentSegmentIndex.value = nextIndex
        const nextSegment = timelines[nextIndex]
        videoRef.value.currentTime = nextSegment.start
      } else {
        videoRef.value.currentTime = videoRef.value.duration
      }
    }
  }
}

const onEnded = () => {
  const currentIdx = videos.value.findIndex(video => video.videoNo === selectedVideo.value?.videoNo)
  const nextIdx = currentIdx + 1
  if (nextIdx < videos.value.length) {
    setSelectedVideo(videos.value[nextIdx])
  } else {
    setSelectedVideo(videos.value[0])
  }
}

const onloadeddata = () => {
  if (videoRef.value) {
    videoRef.value?.play().catch((error) => {
      console.error('Failed to play video:', error)
    })
  }
}

const onPlay = () => {
  if (videoRef.value && videoTimeline.value && videoTimeline.value.timelines.length > 0) {
    isPlaying.value = true
    const firstSegment = videoTimeline.value.timelines[0]
    videoRef.value.currentTime = firstSegment.start // 첫 구간 시작점으로 이동
    console.log(`Playing segment 0: ${firstSegment.start} to ${firstSegment.end}`)
  }
}

const onPause = () => {
  isPlaying.value = false
}

</script>
<template>
  <div class="detail-view">
    <div v-if="selectedVideo && videoMetadatas.length > 0 && selectedVideoUrl && show" class="video-detail">
      <div class="thumbnail-wrapper">
        <video 
          ref="videoRef" 
          :src="selectedVideoUrl" 
          class="detail-thumbnail"
          @timeupdate="onTimeUpdate"
          @loadeddata="onloadeddata"
          @play="onPlay"
          @pause="onPause"
          @ended="onEnded"
          controls 
        />
      </div>
      <div class="detail-content">
        <h2>{{ selectedVideo.videoTitle }}</h2>
        <div class="channel-info-wrapper">
          <div class="channel-info">
            <img :src="selectedVideo.channel.channelImageUrl" alt="Channel Icon" class="channel-icon" />
            <span class="channel-name">{{ selectedVideo.channel.channelName }}</span>
            <span class="verified" v-if="selectedVideo.channel.verifiedMark">✔</span>
          </div>
          <div class="resolution-select">
            <select id="resolution" v-model="selectedVideoUrl">
              <option v-for="metadata in videoMetadatas" :key="metadata.baseURL" :value="metadata.baseURL">
                {{ metadata.height }}p ({{ metadata.width }}x{{ metadata.height }})
              </option>
            </select>
          </div>
        </div>
        <div class="meta-info">
          <span class="meta-item">
            <i class="icon-clock"></i> {{ formatDuration(selectedVideo.duration) }}
          </span>
          <span class="meta-item">
            <i class="icon-calendar"></i> {{ formatDate(selectedVideo.publishDate) }}
          </span>
          <span class="meta-item">
            <i class="icon-eye"></i> {{ selectedVideo.readCount }} views
          </span>
        </div>
        <!-- 타임라인 목록 UI -->
        <div class="timeline-list" v-if="videoTimeline && videoTimeline.timelines.length > 0">
          <h3>노래 타임라인</h3>
          <ul>
            <li v-for="(segment, index) in videoTimeline.timelines" :key="index" :class="{ active: index === currentSegmentIndex }">
              <span class="segment-time">{{ formatDuration(segment.start) }} - {{ formatDuration(segment.end) }}</span>
              <span class="segment-duration">({{ formatDuration(segment.end - segment.start) }})</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div v-else class="no-selection">
      <p>Select a video from the list</p>
    </div>
  </div>
</template>
<style scoped>
.detail-view {
  flex: 2;
  padding: 20px;
  background: #f9f9f9;
  overflow-y: auto;
}

.video-detail {
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.thumbnail-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 비율 */
}

.detail-thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}

.duration-display {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.detail-content {
  padding: 20px;
}

h2 {
  font-size: 24px;
  margin: 0 0 12px;
  color: #333;
  line-height: 1.3;
}

.channel-info-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.channel-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #eee;
}

.channel-name {
  font-size: 16px;
  color: #555;
  font-weight: 500;
}

.verified {
  color: #007bff;
  font-size: 14px;
}

.meta-info {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon-clock,
.icon-calendar,
.icon-eye {
  display: inline-block;
  width: 16px;
  height: 16px;
  background: #888;
  mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>') no-repeat center;
}
.icon-calendar {
  mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10z"/></svg>');
}
.icon-eye {
  mask: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>');
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #888;
  font-size: 16px;
}

/* 타임라인 목록 스타일 */
.timeline-list {
  margin-bottom: 16px;
}

.timeline-list h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 8px;
  font-weight: 500;
}

.timeline-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.timeline-list li {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 14px;
  color: #666;
  background: #f5f5f5;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: background-color 0.2s;
}

.timeline-list li.active {
  background: #e0f0ff;
  color: #007bff;
  font-weight: 500;
}

.timeline-list li:hover {
  background: #ececec;
}

.timeline-list .segment-time {
  flex: 1;
}

.timeline-list .segment-duration {
  color: #888;
  font-size: 12px;
}

/* 해상도 선택 스타일 */
.resolution-select {
  display: flex;
  align-items: center;
  gap: 10px;
}

.resolution-select label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.resolution-select select {
  padding: 6px 12px;
  font-size: 14px;
  color: #333;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
}

.resolution-select select:hover {
  background: #ececec;
  border-color: #bbb;
}

.resolution-select select:focus {
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

/* 드롭다운 화살표 커스터마이징 (선택적) */
.resolution-select select {
  appearance: none;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"><path fill="%23666" d="M7 10l5 5 5-5z"/></svg>');
  background-repeat: no-repeat;
  background-position: right 8px center;
  padding-right: 28px;
}
</style>