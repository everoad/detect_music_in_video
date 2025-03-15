'use strict'

function debounce(callback, time) {
  let timeoutId = null
  return (...args) => {
    if (timeoutId) clearTimeout(timeoutId)
    timeoutId = setTimeout(() => callback(...args), time)
  }
}

function throttle(callback, time) {
  let lastTime = 0
  return (...args) => {
    const now = Date.now()
    if (now - lastTime >= time) {
      lastTime = now
      return callback(...args)
    }
  }
}

function formatTime(seconds) {
  if (seconds < 0) seconds = 0
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

function getIcon(type) {
  let path = ''
  switch (type) {
    case ICONS.PLAY:
      path = 'icons/play_arrow_24dp.svg'
      break
    case ICONS.NEXT:
      path = 'icons/chevron_right_24dp.svg'
      break
    case ICONS.PREV:
      path = 'icons/chevron_left_24dp.svg'
      break
    case ICONS.STOP:
      path = 'icons/pause_24dp.svg'
      break
    case ICONS.AUTOPLAY:
      path = 'icons/autoplay_24dp.svg'
      break
    case ICONS.AUTOPLAY_ACTIVE:
      path = 'icons/autoplay_24dp_active.svg'
      break
    case ICONS.AUTOMOVE:
      path = 'icons/skip_next_24dp.svg'
      break
    case ICONS.AUTOMOVE_ACTIVE:
      path = 'icons/skip_next_24dp_active.svg'
  }
  return chrome.runtime.getURL(path)
}


function createIconImg(type) {
  const img = document.createElement('img')
  img.src = getIcon(type)
  img.alt = type
  return img
}

function sendMessage(message) {
  if (!chrome.runtime) return
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(message, (response) => {
      resolve(response)
    })
  })
}
