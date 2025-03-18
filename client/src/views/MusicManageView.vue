<script setup lang="ts">
import { editVideoTimelines, fetchVideoTimelines } from '@/api/chzzk.api'
import TimelineEditor from '@/components/admin/TimelineEditor.vue'
import VideoList from '@/components/admin/VideoList.vue'
import VideoPlayer from '@/components/admin/VideoPlayer.vue'
import type { ChzzkTimeline, ChzzkVideoTimeline } from '@/types/chzzk'
import { cleanText } from '@/utils/common-utils'
import { computed, onMounted, ref } from 'vue'


const videos = ref<ChzzkVideoTimeline[]>([])

const selectedVideoIndex = ref<number>(-1)

const selectedVideo = computed<ChzzkVideoTimeline | null>(() => {
  return selectedVideoIndex.value !== -1 ? videos.value[selectedVideoIndex.value] : null
})

function selectVideo(index: number) {
  selectedVideoIndex.value = index
}

function updateVideo({ deploy, timelines }: { deploy: number, timelines: ChzzkTimeline[]}) {
  if (selectedVideoIndex.value !== -1) {
    videos.value[selectedVideoIndex.value].deploy = deploy
    videos.value[selectedVideoIndex.value].timelines = timelines
  }
}

async function loadVideoTimelines() {
  videos.value = await fetchVideoTimelines()
}

async function saveVideoTimelines() {
  await editVideoTimelines(videos.value[selectedVideoIndex.value])
  await loadVideoTimelines()
}

onMounted(async () => {
  await loadVideoTimelines()
  if (videos.value.length > 0) {
    selectedVideoIndex.value = 0
  }
})
</script>
<template>
  <div class="video-cotainer">
    <VideoList :videos="videos" @select-video="selectVideo" :selected-index="selectedVideoIndex" />
    <TimelineEditor 
      :selected-video="selectedVideo"
      :videos="videos"
      @update-video="updateVideo" 
      @save-video="saveVideoTimelines"
    />
  </div>
</template>