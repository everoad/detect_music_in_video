<script setup lang="ts">
import { addVideo, fetchChzzkVideo, fetchVideoMetadata, isCompletedProccess as isProccessCompleted } from '@/api/chzzk.api'
import type { ChzzkMusicRegister } from '@/types/chzzk'
import { ref } from 'vue'

const editVideo = ref<ChzzkMusicRegister>({})
const loading = ref<boolean>(false)

const saveVideo = async () => {
  const { video_no, video_url } = editVideo.value 
  if (!video_no || !video_url) {
    alert('입력해 주세요.')
    return
  }
  try {
    await addVideo({
      video_no: Number(video_no),
      video_url
    })
    isCompleted()
  } catch(e) {
    alert('에러')
  }
}

const loadVideoMetadata = async () => {
  const { video_no } = editVideo.value
  if (!video_no || String(video_no).length < 7) {
    return
  }
  
  if (video_no) {

    const isExisted = await isProccessCompleted(Number(video_no))
    if (isExisted.length > 0) {
      alert('이미 등록된 영상입니다.')
      return
    }

    const findVideo = await fetchChzzkVideo(video_no)

    const { videoId, inKey } = findVideo
    const metadata = await fetchVideoMetadata(videoId, inKey)
    const videoMetadatas = metadata.period
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
    
    if (videoMetadatas.length > 0) {
      editVideo.value.video_url = videoMetadatas[2].baseURL
    }
    loading.value = false
  }
}



const isCompleted = () => {
  loading.value = true
  const videoNo = Number(editVideo.value.video_no)
  setTimeout(async () => {
    const data = await isProccessCompleted(videoNo)
    if (data.length < 1) {
      isCompleted()
    } else {
      editVideo.value = {
        video_no: undefined,
        video_url: undefined
      }
      loading.value = false
      alert("완료!")
    }
  }, 10000)
}
</script>

<template>
  <div class="add-container">
    <div class="add-title">영상 등록</div>
    <div class="input-container">
      <div>
        <div class="label">영상 번호</div>
        <input type="text" class="input" v-model="editVideo.video_no" @input="loadVideoMetadata" maxlength="7" />
      </div>
      <div>
        <div class="label">영상 URL</div>
        <input type="text" class="input" v-model="editVideo.video_url" />
      </div>
      <div class="action">
        <button class="button button-primary" @click="saveVideo">저장</button>
      </div>
    </div>
    <div v-show="loading" class="loading">Loading...</div>
  </div>
</template>

<style>
.add-container {
  background: white;
  padding: 20px;
}
.add-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
}
.input-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.label {
  font-weight: 600;
  padding-bottom: 2px;
}
.action {
  margin-top: 15px;
  display: flex;
  justify-content: end;
  align-items: center;
}
.loading {
  text-align: center;
  font-weight: 600;
  font-size: 18px;
}
</style>
