
const CONSTANTS = Object.freeze({
  KEEPALIVE: 'keepalive',
  TARGET_URL: 'https://chzzk.naver.com/'
})

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.debug("📩 Receive message :", message)
  if (message.action === "wakeup") {
    initKeepaliveAlarm()
    sendResponse({ status: "ok" })
  }
  return true
})

function initKeepaliveAlarm() {
  console.debug(`✅ Init keepalive alarm : ${CONSTANTS.TARGET_URL}`)
  chrome.alarms.get(CONSTANTS.KEEPALIVE, (alarm) => {
    if (alarm) {
      chrome.alarms.clear(CONSTANTS.KEEPALIVE)
      chrome.alarms.onAlarm.removeListener(onAlarm)
    }
    chrome.alarms.create(CONSTANTS.KEEPALIVE, { periodInMinutes: 0.5 })
    chrome.alarms.onAlarm.addListener(onAlarm)
  })
}

function onAlarm(alarm) {
  if (alarm.name === CONSTANTS.KEEPALIVE) {
    console.debug("✅ Alarm triggered. Keeping service worker alive.")
    checkIfChzzkIsStillOpen()
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
    } else {
      console.debug("✅ Chzzk is still open in at least one tab.")
    }
  })
}