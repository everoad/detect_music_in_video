<script setup lang="ts">
import { fetchVideoMetadata, fetchVideoTimeline } from '@/api/chzzk.api';
import { useChzzkVideo } from '@/composables/use-chzzk-video';
import type { ChzzkVideoTimeline, MyChzzkVideoMetadata } from '@/types/chzzk';
import { formatDate, formatDuration } from '@/utils/common-utils';
import { computed, nextTick, ref, watch } from 'vue';


const {videos, selectedVideo, setSelectedVideo } = useChzzkVideo()

const videoMetadatas = ref<MyChzzkVideoMetadata[]>([])
const selectedVideoUrl = ref<string | null>(null)
const videoTimeline = ref<ChzzkVideoTimeline>()
const currentSegmentIndex = ref<number>(0) // 현재 재생 중인 구간 인덱스
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
          baseURL: baseURL.value
      })}))
      .sort((a, b) => b.height - a.height)
    
    if (videoMetadatas.value.length > 0) {
      selectedVideoUrl.value = videoMetadatas.value[1].baseURL
    }
  }
}

const loadVideoTimeline = async () => {
  if (selectedVideo.value) {
    const { videoNo } = selectedVideo.value
    const timeline = await fetchVideoTimeline(videoNo)
    // videoTimeline.value = timeline || { videoNo, timelines: [] } // 기본값 설정
    const lines = {
      videoNo: videoNo,
      timelines: [
        {
          "start": 1854.3736410340623,
          "end": 2023.8620919131529
        },
        {
          "start": 2273.8450578115167,
          "end": 2423.334871418738
        },
        {
          "start": 2707.3155206792794,
          "end": 2889.303119853288
        },
        {
          "start": 3649.7513021161108,
          "end": 3904.733927332442
        },
        {
          "start": 4185.7147810022025,
          "end": 4449.196827059078
        },
        {
          "start": 4851.169436223647,
          "end": 5071.654412146004
        },
        {
          "start": 5183.146814936674,
          "end": 5399.632063404657
        },
        {
          "start": 5658.614416075362,
          "end": 5776.60637597939
        },
        {
          "start": 5945.594860926683,
          "end": 6253.073908981671
        },
        {
          "start": 6352.56712940922,
          "end": 6510.056397925188
        },
        {
          "start": 6632.548051215387,
          "end": 6867.0320732280525
        },
        {
          "start": 7008.522431926526,
          "end": 7172.511257555852
        },
        {
          "start": 7339.999844707756,
          "end": 7701.975179328587
        },
        {
          "start": 7946.458519977186,
          "end": 8097.448231379798
        },
        {
          "start": 8335.931980846837,
          "end": 8585.414980813404
        },
        {
          "start": 8732.404964761643,
          "end": 8928.39161002596
        },
        {
          "start": 9602.345686087949,
          "end": 9839.329537759597
        },
        {
          "start": 9940.322655982536,
          "end": 10109.811106861627
        },
        {
          "start": 10191.80551967629,
          "end": 10484.285589777375
        },
        {
          "start": 10592.778196977266,
          "end": 10797.764229013923
        },
        {
          "start": 11015.2494093455,
          "end": 11120.242255022813
        },
        {
          "start": 11185.737792088185,
          "end": 11477.717896257473
        },
        {
          "start": 11752.699158745672,
          "end": 11992.682806008102
        },
        {
          "start": 12183.169826022655,
          "end": 12432.152860057426
        },
        {
          "start": 12860.62366360722,
          "end": 13062.6099000531
        },
        {
          "start": 13119.106050346129,
          "end": 13298.593819861155
        },
        {
          "start": 13495.080431057268,
          "end": 13617.572084347466
        },
        {
          "start": 13729.564453069934,
          "end": 14019.544693512036
        },
        {
          "start": 14091.039821758968,
          "end": 14341.022787657332
        },
        {
          "start": 14644.502108257944,
          "end": 14906.984222451227
        }
      ]
    }
    lines.timelines = lines.timelines.map((segment) => {
      return {
        start: Math.floor(segment.start) - 1,
        end: Math.ceil(segment.end) + 1
      }
    })
    videoTimeline.value = lines
  }
}

const show = ref<boolean>(false)
watch(selectedVideo, async (newVideo, oldVideo) => {
  if (newVideo && newVideo.videoId !== oldVideo?.videoId) {
    show.value = false
    currentSegmentIndex.value = 0
    await Promise.all([loadVideoMetadata(), loadVideoTimeline()])
    nextTick(() => {
      show.value = true
      if (videoRef.value) {
        onPlay()
      }
    })
  }
})

const totalMusicDuration = computed(() => {
  return videoTimeline.value?.timelines.reduce((acc, segment) => acc + (segment.end - segment.start), 0) || 0
})

const onTimeUpdate = () => {
  if (videoRef.value && videoTimeline.value) {
    const currentTime = videoRef.value.currentTime
    const timelines = videoTimeline.value.timelines
    const totalDuration = videoRef.value.duration

    // 전체 시간을 초과하면 바로 종료
    if (currentTime >= totalDuration - 5) {
      return
    }

    // 현재 구간 찾기
    const currentIndex = timelines.findIndex((segment) => {
      return currentTime >= segment.start && currentTime <= segment.end
    })

    if (currentIndex !== -1) {
      // 현재 시간이 구간 내에 있음
      currentSegmentIndex.value = currentIndex
      const currentSegment = timelines[currentSegmentIndex.value]
      if (currentTime >= currentSegment.end) {
        const nextIndex = currentSegmentIndex.value + 1
        if (nextIndex < timelines.length) {
          currentSegmentIndex.value = nextIndex
          const nextSegment = timelines[nextIndex]
          videoRef.value.currentTime = nextSegment.start
          console.log(`Moved to segment ${nextIndex}: ${nextSegment.start} to ${nextSegment.end}`)
        } else {
          videoRef.value.currentTime = totalDuration
          console.log('Moved to end of video')
        }
      }
    } else {
      // 구간 외부에 있는 경우
      const previousSegmentIndex = timelines.findIndex(segment => currentTime < segment.start) - 1
      const nextSegmentIndex = timelines.findIndex(segment => currentTime < segment.start)

      if (nextSegmentIndex === -1) {
        // 마지막 구간 이후로 이동
        videoRef.value.currentTime = totalDuration
        console.log('Moved to end of video (beyond last segment)')
      } else if (previousSegmentIndex >= 0 && currentTime > timelines[previousSegmentIndex].end) {
        // 구간 사이에 있는 경우 다음 구간으로 이동
        currentSegmentIndex.value = nextSegmentIndex
        const nextSegment = timelines[nextSegmentIndex]
        videoRef.value.currentTime = nextSegment.start
        console.log(`Moved between segments to ${nextSegmentIndex}: ${nextSegment.start} to ${nextSegment.end}`)
      } else if (previousSegmentIndex < 0) {
        // 첫 구간 이전에 있는 경우 첫 구간으로 이동
        currentSegmentIndex.value = 0
        const firstSegment = timelines[0]
        videoRef.value.currentTime = firstSegment.start
        console.log(`Moved before first segment to 0: ${firstSegment.start} to ${firstSegment.end}`)
      } else {
        // 이전 구간으로 이동 시 인덱스 업데이트
        currentSegmentIndex.value = previousSegmentIndex
        console.log(`Moved to previous segment ${previousSegmentIndex}: ${timelines[previousSegmentIndex].start} to ${timelines[previousSegmentIndex].end}`)
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

const onLoadedData = () => {
  if (videoRef.value) {
    videoRef.value?.play().catch((error) => {
      console.error('Failed to play video:', error)
    })
  }
}

const onPlay = () => {
  if (videoRef.value && videoRef.value.currentTime <= 1 && videoTimeline.value && videoTimeline.value.timelines.length > 0) {
    // if (videoRef.value.currentTime === videoRef.value.duration) {
    //   return
    // }
    const firstSegment = videoTimeline.value.timelines[0]
    videoRef.value.currentTime = firstSegment.start // 첫 구간 시작점으로 이동
    console.log(`Playing segment 0: ${firstSegment.start} to ${firstSegment.end}`)
  }
}

const moveTimeline = (index: number) => {
  if (videoRef.value && videoTimeline.value && videoTimeline.value.timelines.length > 0) {
    const segment = videoTimeline.value.timelines[index]
    videoRef.value.currentTime = segment.start
    currentSegmentIndex.value = index
    console.log(`Moved to segment ${index}: ${segment.start} to ${segment.end}`)
  }
}
</script>
<template>
  <div class="detail-view">
    <div v-if="selectedVideo && selectedVideoUrl && show" class="video-detail">
      <div class="thumbnail-wrapper">
        <video 
          ref="videoRef" 
          :src="selectedVideoUrl" 
          class="detail-thumbnail"
          @timeupdate="onTimeUpdate"
          @loadeddata="onLoadedData"
          @play="onPlay"
          @ended="onEnded"
          controls
          controlslist="nodownload noremoteplayback"
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
            <i class="icon-clock"></i> {{ formatDuration(totalMusicDuration) }}
          </span>
          <span class="meta-item">
            <i class="icon-calendar"></i> {{ formatDate(selectedVideo.publishDate) }}
          </span>
        </div>
        <!-- 타임라인 목록 UI -->
        <div class="timeline-list" v-if="videoTimeline && videoTimeline.timelines.length > 0">
          <div class="timeline-title">노래 타임라인 ({{ currentSegmentIndex + 1 }} / {{ videoTimeline.timelines.length }})</div>
          <ul>
            <li 
              v-for="(segment, index) in videoTimeline.timelines" 
              :key="index" 
              :class="{ active: index === currentSegmentIndex }"
              @click="moveTimeline(index)"
            >
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

.timeline-list .timeline-title {
  font-size: 14px;
  color: #333;
  margin: 0 0 8px;
  
  /* font-weight: 500; */
}

.timeline-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.timeline-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  font-size: 14px;
  color: #666;
  background: #f5f5f5;
  border-radius: 6px;
  margin-bottom: 4px;
  transition: background-color 0.2s;
  cursor: pointer;
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