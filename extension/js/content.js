'use strict'

async function start() {
  const data = await sendMessage({ action: 'data' })

  const storage = new StorageAdapter()
  const api = new ApiService(data, storage)

  const videoController = new VideoTimelineController(api, storage)
  if (videoController.isValidVideoUrl()) {
    videoController.init()
  }
  
  new MusicSearchController(api, storage)
}

// 페이지 로드 시 실행
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start)
} else {
  start()
}