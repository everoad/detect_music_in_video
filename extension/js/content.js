async function start() {
  const data = await sendMessage({ action: 'data' })
  const controller = new VideoTimelineController(data)
  if (controller.isValidVideoUrl()) {
    controller.init()
  }
  new MusicSearchController()
}

// 페이지 로드 시 실행
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start)
} else {
  start()
}