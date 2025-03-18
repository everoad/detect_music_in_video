<script setup lang="ts">
import type { ChzzkVideoTimeline, ChzzkVideoTimelineEdit } from '@/types/chzzk';
import { cleanText } from '@/utils/common-utils';
import { computed, ref, watch } from 'vue';
import VideoPlayer from './VideoPlayer.vue';

const props = defineProps<{
  selectedVideo: ChzzkVideoTimeline | null
  videos: ChzzkVideoTimeline[]
}>()

const emit = defineEmits(['update-video', 'save-video'])

const localDeploy = ref<boolean>(false)
const localTimelines = ref<ChzzkVideoTimelineEdit[]>([])
const draggingIndex = ref<number | null>(null)
const playerRef = ref<typeof VideoPlayer>()

const musics = computed(() => props.videos.reduce<Record<string, number[][]>>((acc, video) => {
  if (video.deploy === 1 && video.videoNo !== props.selectedVideo?.videoNo) {
    video.timelines.forEach((timeline)=> {
      if (timeline.title) {
        const title = cleanText(timeline.title)
        const currentDuration = timeline.end - timeline.start
        if (!acc[title]) {
          acc[title] = [[currentDuration, 1]]
        } else {
          const items = acc[title]
          for (let i = 0; i < items.length; i++) {
            const [duration, count] = items[i]
            if (Math.abs(duration - currentDuration) <= 5) {
              const nextCount = count + 1
              const nextDuration = ((duration * count) + (currentDuration)) / nextCount
              items[i] = [nextDuration, nextCount]
              return
            }
          }
          acc[title].push([currentDuration, 1])
        }
      }
    })
  }
  return acc
}, {}))

watch(() => props.selectedVideo, (newVideo) => {
  if (newVideo) {
    localDeploy.value = newVideo.deploy ? true :false
    console.log(localDeploy.value)
    localTimelines.value = newVideo.timelines.map(timeline => ({
      start: secondsToTime(timeline.start),
      end: secondsToTime(timeline.end),
      title: timeline.title
    }))

  } else {
    localTimelines.value = []
  }
}, { deep: true })

function secondsToTime(seconds: number) {
  const hours = Math.floor(seconds / 3600).toString().padStart(2, '0')
  const minutes = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0')
  const secs = Math.round(seconds % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}:${secs}`
}

function timeToSeconds(time: string) {
  const [hours, minutes, seconds] = time.split(':').map(Number)
  return (hours * 3600) + (minutes * 60) + seconds
}

function updateTimeline() {
  const updated = localTimelines.value.map(({ start, end, title }) => ({ start: timeToSeconds(start), end: timeToSeconds(end), title }))
  emit('update-video', {
    deploy: localDeploy.value ? 1 : 0,
    timelines: updated
  })
}

function deleteTimeline(index: number) {
  localTimelines.value.splice(index, 1)
  updateTimeline()
}

function addTimeline() {
  localTimelines.value.push({ title: '', start: '00:00:00', end: '00:00:00' })
  updateTimeline()
}

function handleDragStart(event: DragEvent, index: number) {
  draggingIndex.value = index;
  event.dataTransfer?.setData('text/plain', String(index));
  (event.target as HTMLElement)?.classList.add('opacity-50', 'bg-gray-200');
}

function handleDrop(event: DragEvent, toIndex: number) {
  event.preventDefault()
  const fromIndex = Number(event.dataTransfer?.getData('text/plain'))
  const [movedItem] = localTimelines.value.splice(fromIndex, 1)
  localTimelines.value.splice(toIndex, 0, movedItem)
  updateTimeline()
}

function handleDragEnd(event: Event) {
  draggingIndex.value = null;
  (event.target as HTMLElement)?.classList.remove('opacity-50', 'bg-gray-200')
}

function saveVideo() {
  emit('save-video')
}

function findEndTime(timeline: ChzzkVideoTimelineEdit) {
  if (timeline.title) {
    const title = cleanText(timeline.title)
    const items = musics.value[title]
    if (items !== undefined) {
      return items.map((item) => {
        const [duration, count] = item
        const start = timeToSeconds(timeline.start)
        return `${secondsToTime(start + duration)}, ${count}곡`
      })
    }
  }
  return []
}

function copyEndTime(timeline: ChzzkVideoTimelineEdit, time: string) {
  if (time) {
    timeline.end = time.split(',')[0].trim()
    updateTimeline()
  }
}

function goTime(time: string, buffer: number) {
  playerRef.value?.timeAt(timeToSeconds(time) + buffer)
}
</script>

<template>
  <div class="timeline-editor">
    <div class="timeline-control">
      <div style="display: flex; align-items: center; gap: 2px;">
        <input type="checkbox" v-model="localDeploy" @change="updateTimeline" /> 배포
      </div>
      <button class="button button-primary" @click="saveVideo">
        저장
      </button>
    </div>
    <table v-if="selectedVideo" class="table">
      <thead>
        <tr>
          <th>No</th>  
          <th>Title</th>
          <th>Start (HH:MM:SS)</th>
          <th>End (HH:MM:SS)</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody ref="tbody" @dragover.prevent>
        <tr
          v-for="(timeline, index) in localTimelines"
          :key="index"
          draggable="true"
          @dragstart="handleDragStart($event, index)"
          @drop="handleDrop($event, index)"
          @dragend="handleDragEnd"
          :class="{ 'dragging': draggingIndex === index }"
        >
          <td class="text-center">
            {{ index + 1 }}
          </td>
          <td>
            <input
              v-model="timeline.title"
              @change="updateTimeline()"
              class="input"
            />
          </td>
          <td>
            <div class="input-wrapper">
              <input
                v-model="timeline.start"
                @change="updateTimeline()"
                class="input"
              />
              <button class="button" @click="goTime(timeline.start, -2)">▶</button>
            </div>
          </td>
          <td>
            <div class="input-wrapper">
              <input
                v-model="timeline.end"
                @change="updateTimeline()"
                class="input"
              />
              <button class="button" @click="goTime(timeline.end, -5)">▶</button>
            </div>
            <div class="expect-time-box">
              <template v-for="(item, idx) in findEndTime(timeline)" :key="idx">
                <span 
                  class="expect-time" 
                  @click="copyEndTime(timeline, item)"
                >
                  <span>{{ item }}</span>
                </span>
              </template>
            </div>
          </td>
          <td class="text-center">
            <button @click="deleteTimeline(index)" class="button button-danger">
              삭제
            </button>
          </td>
        </tr>
        <tr>
          <td colspan="5">
            <button
              v-if="selectedVideo"
              @click="addTimeline"
              class="add-button button button-primary"
            >
              새 구간 추가
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <template v-if="selectedVideo">
      <VideoPlayer
        ref="playerRef"
        :video="selectedVideo"
      />
    </template>
  </div>
</template>

<style scoped>
.input-wrapper {
  display: flex;
}
.expect-time-box {
  padding-top: 4px;
  display: grid;
  gap: 4px;
  grid-template-columns: repeat(3, 1fr);
}
.expect-time {
  padding: 2px;
  flex: 1;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  background-color: #eee;
  border: 1px solid #ddd;
  text-align: center;
}
</style>
