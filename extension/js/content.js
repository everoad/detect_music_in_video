'use strict'

async function start() {
  const data = await sendMessage({ action: 'data' })
  
  const videoController = new VideoTimelineController(data)
  if (videoController.isValidVideoUrl()) {
    videoController.init()
  }
  
  new MusicSearchController()
}

// 페이지 로드 시 실행
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start)
} else {
  start()
}