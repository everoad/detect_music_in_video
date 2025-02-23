<script setup lang="ts">
import { fetchVideoMetadata, fetchVideoTimeline } from '@/api/chzzk.api';
import { useChzzkVideo } from '@/composables/use-chzzk-video';
import type { ChzzkVideoTimeline, MyChzzkVideoMetadata } from '@/types/chzzk';
import { formatDate, formatDuration } from '@/utils/common-utils';
import { computed, nextTick, ref, watch } from 'vue';
import HlsVideo from './HlsVideo.vue';


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
          baseURL: baseURL.value,
          duration: 0
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
          "start": 1854.2910358656084,
          "end": 2023.7356995105888
        },
        {
          "start": 2274.782609103577,
          "end": 2423.1066914443672
        },
        {
          "start": 2707.2745126280174,
          "end": 2909.360074652201
        },
        {
          "start": 3648.100407087399,
          "end": 3904.907475217894
        },
        {
          "start": 4196.275494573427,
          "end": 4449.722470223709
        },
        {
          "start": 4851.493528214783,
          "end": 5072.299605485861
        },
        {
          "start": 5124.1410323234195,
          "end": 5426.069342331048
        },
        {
          "start": 5659.355763100058,
          "end": 5775.998973484562
        },
        {
          "start": 5945.923650341002,
          "end": 6253.612118886136
        },
        {
          "start": 6353.454866869582,
          "end": 6510.89920022809
        },
        {
          "start": 6633.302569150102,
          "end": 6867.549016342029
        },
        {
          "start": 7008.672900510936,
          "end": 7172.837418829869
        },
        {
          "start": 7338.921989994637,
          "end": 7702.77200428046
        },
        {
          "start": 7946.618715701565,
          "end": 8133.823868170523
        },
        {
          "start": 8334.46939056033,
          "end": 8574.956009501224
        },
        {
          "start": 8733.360369282651,
          "end": 9022.328322580888
        },
        {
          "start": 9603.144308446119,
          "end": 9840.270834906802
        },
        {
          "start": 9884.912063572476,
          "end": 10121.558576821697
        },
        {
          "start": 10192.60053211761,
          "end": 10523.32963481277
        },
        {
          "start": 10593.891576897224,
          "end": 10825.737958031857
        },
        {
          "start": 11016.303202981027,
          "end": 11120.946083079061
        },
        {
          "start": 11151.666928612429,
          "end": 11496.796427651356
        },
        {
          "start": 11753.60349578185,
          "end": 11994.090114722743
        },
        {
          "start": 12120.813602547883,
          "end": 12433.302203207608
        },
        {
          "start": 12861.954001040376,
          "end": 13299.246036679406
        },
        {
          "start": 13483.571109879611,
          "end": 13618.454822299553
        },
        {
          "start": 13730.297900569469,
          "end": 14021.185906713545
        },
        {
          "start": 14087.427729894867,
          "end": 14325.034269567008
        },
        {
          "start": 14645.683094821532,
          "end": 14908.250321489533
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
watch(selectedVideo, async (newVideo) => {
  if (newVideo) {
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