const CONSTANTS = Object.freeze({
  KEEPALIVE: 'keepalive',
  TARGET_URL: 'https://chzzk.naver.com/',
  API_KEY: 'S2tZV0dXY2U4MDdaUXlBbHU4UVE=',
  BASE_URL: 'https://172-237-27-244.ip.linodeusercontent.com',
  TIMELINE_API_URL: '/api/chzzk/videos/timeline'
})


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.debug("📩 Receive message :", message)
  if (message.action === "wakeup") {
    initKeepaliveAlarm()
    sendResponse({ status: "ok" })
  }
  if (message.action === 'data') {
    initKeepaliveAlarm()
    sendResponse({
      API_KEY: CONSTANTS.API_KEY,
      BASE_URL: CONSTANTS.BASE_URL,
      TIMELINE_API_URL: CONSTANTS.TIMELINE_API_URL
    })
  }
  return true
})

function initKeepaliveAlarm() {
  console.debug(`✅ Init keepalive alarm : ${CONSTANTS.TARGET_URL}`)
  chrome.alarms.get(CONSTANTS.KEEPALIVE, (alarm) => {
    if (alarm) {
      chrome.alarms.clear(CONSTANTS.KEEPALIVE)
      chrome.alarms.onAlarm.removeListener(onAlarm)
      // chrome.tabs.onUpdated.removeListener(opUpdatedTabs)
    }
    chrome.alarms.create(CONSTANTS.KEEPALIVE, { periodInMinutes: 0.5 })
    chrome.alarms.onAlarm.addListener(onAlarm)
    // chrome.tabs.onUpdated.addListener(opUpdatedTabs)
  })
}

function onAlarm(alarm) {
  if (alarm.name === CONSTANTS.KEEPALIVE) {
    console.debug("✅ Alarm triggered. Keeping service worker alive.")
    checkIfChzzkIsStillOpen()
  }
}

function opUpdatedTabs(tabId, changeInfo, tab) {
  if (changeInfo.url) {
    console.log('탭 URL 변경:', changeInfo)
    chrome.tabs.sendMessage(tabId, {
      action: 'changeUrl',
      url: changeInfo.url
    })
  }
}

// ✅ 현재 열려 있는 모든 탭 확인 후 `https://chzzk.naver.com/`가 없으면 KeepAlive Alarm 종료 및 이벤트 삭제
function checkIfChzzkIsStillOpen() {
  chrome.tabs.query({}, (tabs) => {
    const isChzzkOpen = tabs.some(tab => tab.url && tab.url.startsWith(CONSTANTS.TARGET_URL))
    if (!isChzzkOpen) {
      console.debug("❌ No Chzzk tabs open. Stopping service worker.")
      chrome.alarms.clear(CONSTANTS.KEEPALIVE)
      chrome.alarms.onAlarm.removeListener(onAlarm)
      // chrome.tabs.onUpdated.removeListener(opUpdatedTabs)
    } else {
      console.debug("✅ Chzzk is still open in at least one tab.")
    }
  })
}