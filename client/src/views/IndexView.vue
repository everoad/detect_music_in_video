<script setup lang="ts">
import { fetchChzzkChannelVideos, fetchChzzkVideo } from '@/api/chzzk.api'
import ChzzkVideoDetail from '@/components/ChzzkVideoDetail.vue'
import ChzzkVideoSide from '@/components/ChzzkVideoSide.vue'
import { ChzzkVideoKey } from '@/composables/chzzk-video.keys'
import type { ChzzkVideo, ChzzkContent } from '@/types/chzzk'
import { onMounted, ref, onUnmounted, provide } from 'vue'

const videos = ref<ChzzkVideo[]>([])
const selectedVideo = ref<ChzzkVideo | null>(null)
const page = ref(0)
const isLoading = ref(false)
const hasMore = ref(true)

// 비디오 로드
const loadVideos = async (pageNum: number) => {
  if (isLoading.value || !hasMore.value) return

  isLoading.value = true
  try {
    const response: ChzzkContent<ChzzkVideo> = await fetchChzzkChannelVideos({ page: pageNum })
    const newVideos = response.data.filter((video) => video.videoCategory === 'music')

    if (newVideos.length === 0 || pageNum >= response.totalPages - 1) {
      hasMore.value = false
    } else {
      videos.value = [...videos.value, ...newVideos]
      page.value++
      if (!selectedVideo.value && newVideos.length > 0) {
        setSelectedVideo(newVideos[0]) // 첫 번째 비디오 기본 선택
      }
    }
  } catch (error) {
    console.error('Failed to load videos:', error)
  } finally {
    isLoading.value = false
  }
}

// 비디오 선택
const setSelectedVideo = async (video: ChzzkVideo) => {
  const res = await fetchChzzkVideo(video.videoNo)
  selectedVideo.value = res
}

// Intersection Observer
const observer = ref<IntersectionObserver | null>(null)
const loadMoreTrigger = ref<HTMLElement | null>(null)

const setupObserver = () => {
  observer.value = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && !isLoading.value && hasMore.value) {
        loadVideos(page.value)
      }
    },
    { threshold: 0.1 }
  )

  if (loadMoreTrigger.value) {
    observer.value.observe(loadMoreTrigger.value)
  }
}

onMounted(async () => {
  await loadVideos(0)
  setupObserver()
})

onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
  }
})

provide(ChzzkVideoKey, {
  videos,
  selectedVideo,
  setSelectedVideo
})
</script>

<<template>
  <div class="container">
    <!-- 왼쪽: 상세 보기 -->
    <ChzzkVideoDetail :selected-video="selectedVideo" />

    <!-- 오른쪽: 비디오 목록 -->
    <div class="list-view">
      <ChzzkVideoSide :videos="videos" @select-video="setSelectedVideo" :selected-video="selectedVideo" />
      <div ref="loadMoreTrigger" class="load-more-trigger" v-if="hasMore">
        <p v-if="isLoading">Loading more videos...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

</style>