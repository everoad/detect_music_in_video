<script setup lang="ts">
import type { ChzzkVideoTimeline, ChzzkVideoTimelineEdit } from '@/types/chzzk';
import { ref, watch } from 'vue';

const props = defineProps<{
  selectedVideo: ChzzkVideoTimeline | null
}>()

const emit = defineEmits(['update-video', 'save-video'])

const localDeploy = ref<boolean>(false)
const localTimelines = ref<ChzzkVideoTimelineEdit[]>([])
const draggingIndex = ref<number | null>(null)

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
  console.log(localDeploy.value, localDeploy.value ? 1: 0)
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
</script>

<template>
  <div class="timeline-editor">
    <div class="timeline-control">
      <div style="display: flex; align-items: center; gap: 2px;">
        <input type="checkbox"  v-model="localDeploy" @change="updateTimeline" /> 배포
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
            <input
              v-model="timeline.start"
              @change="updateTimeline()"
              class="input"
            />
          </td>
          <td>
            <input
              v-model="timeline.end"
              @change="updateTimeline()"
              class="input"
            />
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
  </div>
</template>
