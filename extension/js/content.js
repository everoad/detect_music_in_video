
(function () {

  const ICONS = Object.freeze({
    PLAY: 'play',
    STOP: 'stop',
    NEXT: 'next',
    PREV: 'prev',
    AUTOPLAY: 'autoplay',
    AUTOPLAY_ACTIVE: 'autoplay_active',
    AUTOMOVE: 'automove',
    AUTOMOVE_ACTIVE: 'automove_active'
  })

  const STOREAGE_KEYS = Object.freeze({
    AUTO_MOVE_VIDEO: 'automove',
    AUTOPLAY: 'autoplay',
    VIDEOS: 'videos',
    LAST_CALL_API_TIME: 'lastCallApiTime'
  })

  const TIMOONG_CHANNEL_ID = '26253bf7ed6b95832c40f4f43f6d049d'

  const CHZZK_CONSTANTS = Object.freeze({
    CHZZK_VIDEO_API_URL: 'https://api.chzzk.naver.com/service/v3/videos/',
    CHZZK_VIDEO_LIST_API_URL: `https://api.chzzk.naver.com/service/v1/channels/${TIMOONG_CHANNEL_ID}/videos?sortType=LATEST&pagingType=PAGE&size=40&publishDateAt=&videoType=`,
    CHZZK_VIDEO_PAGE_URL: 'https://chzzk.naver.com/video/',
  })

  const APP_CONSTANTS = Object.freeze({
    MAX_RETRY_COUNT: 10,
    LOCAL_BASE_URL: 'http://127.0.0.1:8000'
  })

  const TEXT = Object.freeze({
    PLAY: '시작',
    PAUSE: '정지',
    NEXT: '다음 노래',
    PREV: '이전 노래',
    AUTOPLAY: '자동 시작 OFF',
    AUTOPLAY_ACTIVE: '자동 시작 ON',
    AUTOMOVE: '다음 영상 지동 재생 OFF',
    AUTOMOVE_ACTIVE: '다음 영상 자동 재생 ON',
    PLAYABLE: '다시듣기'
  })

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

  class VideoTimelineController {
    constructor({ API_KEY, BASE_URL, TIMELINE_API_URL }) {
      this.videoElement = null
      this.controller = null
      this.timelines = []
      this.currentIndex = 0
      this.retryCount = 0
      this.isDev = !chrome.runtime
      this.isPlaying = false
      this.isProgrammaticSeek = false
      this.storage = this.isDev ? this.localStorageAdapter() : this.chromeStorageAdapter()
      this.videoNo = -1
      this.videos = []
      this.isAutoMoveVideo = false
      this.isAutoPlayVideo = false
      this.baseUrl = this.isDev ? APP_CONSTANTS.LOCAL_BASE_URL : BASE_URL
      this.isAdPlaying = false
      this.observer = null
      this.apiKey = API_KEY
      this.timeLineApiUrl = TIMELINE_API_URL
    }

    // URL에서 videoNo 추출
    getVideoNoFromUrl() {
      const url = window.location.href
      if (this.isDev) {
        return 'test'
      }
      const match = url.match(/\/video\/(\d+)$/)
      if (!match) {
        console.warn('Invalid URL format: videoNo not found')
        return null
      }
      return Number(match[1])
    }

    // localStorage 어댑터 (비동기 래퍼)
    localStorageAdapter() {
      return {
        set: (data) => {
          return new Promise((resolve) => {
            Object.entries(data).forEach(([key, value]) => {
              window.localStorage.setItem(key, JSON.stringify(value))
            })
            resolve()
          })
        },
        get: (keys) => {
          return new Promise((resolve) => {
            const result = {}
            keys.forEach((key) => {
              const value = window.localStorage.getItem(key)
              result[key] = value ? JSON.parse(value) : null
            })
            resolve(result)
          })
        }
      }
    }

    // chrome.storage 어댑터
    chromeStorageAdapter() {
      return {
        set: async (data) => {
          await wakeup()
          return new Promise((resolve) => {
            chrome.storage.local.set(data, resolve)
          })
        },
        get: async (keys) => {
          await wakeup()
          return new Promise((resolve) => {
            chrome.storage.local.get(keys, resolve)
          })
        }
      }
    }

    // 공통 저장 함수
    async saveStorageData(key, value) {
      try {
        await this.storage.set({ [key]: value })
      } catch (e) {
        console.warn(e)
      }
    }

    // 공통 불러오기 함수
    async loadStorageData(key, defaultValue = null) {
      try {
        const result = await this.storage.get([key])
        return result[key] !== undefined && result[key] !== null ? result[key] : defaultValue
      } catch (e) {
        console.warn(e)
        return defaultValue
      }
    }

    async fetchVideos() {
      try {
        const response = await fetch(`${this.baseUrl}${this.timeLineApiUrl}`, { headers: { Authorization: `Bearer ${this.apiKey}` } })
        if (!response.ok) {
          throw new Error(`Failed to fetch timelines: ${response.status}`)
        }
        let videos = await response.json()
        // videos = videos.filter((video) => video.deploy === 1)
        this.saveStorageData(STOREAGE_KEYS.VIDEOS, videos)
        this.saveStorageData(STOREAGE_KEYS.LAST_CALL_API_TIME, Date.now())
        return videos
      } catch (error) {
        console.warn('Failed to fetch timelines:', error)
        return this.videos
      }
    }

    async setVideoData() {
      this.videos = await this.loadStorageData(STOREAGE_KEYS.VIDEOS, this.videos)

      const callApiTime = await this.loadStorageData(STOREAGE_KEYS.LAST_CALL_API_TIME, 0)
      const currentTime = Date.now()
      const oneHourInMs = 60 * 60 * 1000

      if (this.videos.length <  1 || currentTime - callApiTime >= oneHourInMs) {
        this.videos = await this.fetchVideos()
      }
    }

    async setTimelines() {
      await this.setVideoData()
      
      const findVideo = this.videos.find((video) => video.videoNo === this.videoNo)
      const timelines = findVideo ? findVideo.timelines : []

      this.timelines = timelines.map((timeline) => ({
        start: Math.max(timeline.start - 2, 0),
        end: timeline.end + 2,
        title: timeline.title || '-'
      }))
    }

    async isTimoong() {
      if (this.isDev) {
        return true
      }
      try {
        const response = await fetch(`${CHZZK_CONSTANTS.CHZZK_VIDEO_API_URL}${this.videoNo}`)
        if (!response.ok) {
          throw new Error(`API request failed: ${response.status}`)
        }

        const data = await response.json()
        return data.code === 200 && data.content.channel.channelId === TIMOONG_CHANNEL_ID
      } catch (error) {
        console.error('Failed to check Timoong:', error)
        return false
      }
    }

    // 서버에서 타임라인 데이터 가져오기
    async loadTimelineData() {
      this.videoNo = this.getVideoNoFromUrl()
      if (!this.videoNo || !await this.isTimoong()) return

      try {
        await this.setTimelines(this.videoNo)
        this.createController()
      } catch (error) {
        console.error('Failed to fetch timeline data:', error)
      }
    }

    // 비디오 요소 찾기
    async findVideoElement() {
      if (this.retryCount >= APP_CONSTANTS.MAX_RETRY_COUNT) {
        console.warn(`Video element not found after ${CHZZK_CONSTANTS.MAX_RETRY_COUNT} retries`)
        return
      }
      this.videoElement = document.querySelector('video.webplayer-internal-video')
      if (!this.videoElement) {
        this.retryCount++
        this.findVideoTimer = setTimeout(() => this.findVideoElement(), 500)
      } else {
        await this.loadTimelineData()
        await Promise.all([this.loadAutoPlaySetting(), this.loadAutoMoveSetting()])
        if (this.isAutoPlayVideo) {
          let timer = setInterval(() => {
            if (!this.videoElement) {
              clearInterval(timer)
              return
            }
            if (this.videoElement.readyState >= 3) {
              clearInterval(timer)
              this.canPlay()
            }
          }, 100)
        }
      }
    }

    canPlay = () => {
      setTimeout(() => {
        const currentTimeline = this.timelines[this.currentIndex]
        if (currentTimeline) {
          this.videoElement.currentTime = currentTimeline.start
        }
        this.play()
      }, 500)
    }

    async loadAutoPlaySetting() {
      this.isAutoPlayVideo = await this.loadStorageData(STOREAGE_KEYS.AUTOPLAY, false)
      if (this.isAutoPlayVideo) {
        this.updateAutoPlayButtonStyle()
      }
    }

    async loadAutoMoveSetting() {
      this.isAutoMoveVideo = await this.loadStorageData(STOREAGE_KEYS.AUTO_MOVE_VIDEO, false)
      if (this.autoMoveButton) {
        this.updateAutoMoveButtonStyle()
      }
    }

    getStaticPath(path) {
      if (this.isDev) {
        return path
      } else {
        return chrome.runtime.getURL(path)
      }
    }

    getIcon(type) {
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
      return this.getStaticPath(path)
    }

    createIconImg(type) {
      const img = document.createElement('img')
      img.src = this.getIcon(type)
      img.alt = type
      return img
    }

    createController() {
      if (!this.videoElement || this.timelines.length === 0) return

      this.controller = document.createElement('div')
      this.controller.className = 'timeline-controller'
      this.controller.addEventListener('click', this.preventControllerEvent)

      // 이전 버튼
      this.prevButton = document.createElement('button')
      this.prevButton.className = 'control-btn prev-btn'
      this.prevButton.appendChild(this.createIconImg(ICONS.PREV))
      this.prevButton.title = TEXT.PREV
      this.prevButton.addEventListener('click', this.prevTimeline)
      this.controller.appendChild(this.prevButton)

      // 재생/멈춤 버튼
      this.playButton = document.createElement('button')
      this.playButton.className = 'control-btn play-btn'
      this.playButtonImg = this.createIconImg(ICONS.PLAY)
      this.playButton.appendChild(this.playButtonImg)
      this.playButton.title = `${TEXT.PLAY}/${TEXT.PAUSE}`
      this.playButton.addEventListener('click', this.togglePlay)
      this.controller.appendChild(this.playButton)

      // 다음 버튼
      this.nextButton = document.createElement('button')
      this.nextButton.className = 'control-btn next-btn'
      this.nextButton.appendChild(this.createIconImg(ICONS.NEXT))
      this.nextButton.title = TEXT.NEXT
      this.nextButton.addEventListener('click', this.nextTimeline)
      this.controller.appendChild(this.nextButton)

      // 구간 표시 (예: 1 / 3)
      this.timelineIndicator = document.createElement('div')
      this.timelineIndicator.className = 'timeline-indicator'
      this.updateIndicator()
      this.controller.appendChild(this.timelineIndicator)

      // 진행 시간 표시 요소 추가
      this.progressIndicator = document.createElement('div')
      this.progressIndicator.className = 'progress-indicator'
      this.updateProgressIndicator(true) // 초기 업데이트
      this.controller.appendChild(this.progressIndicator)

      // 자동 실행행
      this.autoPlayButton = document.createElement('button')
      this.autoPlayButton.className = 'control-btn autoplay-btn'
      this.autoPlayButtonImg = this.createIconImg(ICONS.AUTOPLAY)
      this.autoPlayButton.appendChild(this.autoPlayButtonImg)
      this.autoPlayButton.title = TEXT.AUTOPLAY
      this.autoPlayButton.addEventListener('click', this.toggleAutoPlay)
      this.controller.appendChild(this.autoPlayButton)

      // 다음 영상 이동 토글 버튼
      this.autoMoveButton = document.createElement('button')
      this.autoMoveButton.className = 'control-btn auto-move-btn'
      this.autoMoveButtonImg = this.createIconImg(ICONS.AUTOMOVE)
      this.autoMoveButton.appendChild(this.autoMoveButtonImg)
      this.autoMoveButton.title = TEXT.AUTOMOVE
      this.autoMoveButton.addEventListener('click', this.toggleAutoMove)
      this.controller.appendChild(this.autoMoveButton)

      // 타임라인 드롭다운 컨테이너 추가
      this.timelineDropdown = document.createElement('div')
      this.timelineDropdown.className = 'timeline-dropdown'
      this.timelineDropdown.style.display = 'none'
      this.createTimelineList()
      this.controller.appendChild(this.timelineDropdown)

      // 마우스 이벤트 추가 (컨트롤러 전체에 적용)
      this.controller.addEventListener('mouseenter', this.showTimelineDropdown)
      this.controller.addEventListener('mouseleave', this.hideTimelineDropdown)

      this.videoElement.parentElement.style.position = 'relative'
      this.videoElement.parentElement.appendChild(this.controller)
      this.videoElement.addEventListener('timeupdate', this.timeupdate)
      this.videoElement.addEventListener('pause', this.stop)
      this.videoElement.addEventListener('seeked', this.seeked)
    }

    preventControllerEvent = (event) => {
      event.preventDefault()
      event.stopPropagation()
    }

    timeupdate = () => {
      this.checkTimelineEnd()
      this.updateProgressIndicator()
    }

    toggleAutoPlay = async () => {
      this.isAutoPlayVideo = !this.isAutoPlayVideo
      await this.saveStorageData(STOREAGE_KEYS.AUTOPLAY, this.isAutoPlayVideo)
      this.updateAutoPlayButtonStyle()
    }


    updateAutoPlayButtonStyle() {
      if (this.autoPlayButtonImg) {
        this.autoPlayButtonImg.src = this.isAutoPlayVideo ? this.getIcon(ICONS.AUTOPLAY_ACTIVE) : this.getIcon(ICONS.AUTOPLAY)
      }
      if (this.autoPlayButton) {
        this.autoPlayButton.title = this.isAutoPlayVideo ? TEXT.AUTOPLAY_ACTIVE : TEXT.AUTOPLAY
      }
    }


    toggleAutoMove = async () => {
      this.isAutoMoveVideo = !this.isAutoMoveVideo
      await this.saveStorageData(STOREAGE_KEYS.AUTO_MOVE_VIDEO, this.isAutoMoveVideo)
      this.updateAutoMoveButtonStyle()
    }

    updateAutoMoveButtonStyle() {
      if (this.autoMoveButtonImg) {
        this.autoMoveButtonImg.src = this.isAutoMoveVideo ? this.getIcon(ICONS.AUTOMOVE_ACTIVE) : this.getIcon(ICONS.AUTOMOVE)
      }
      if (this.autoMoveButton) {
        this.autoMoveButton.title = this.isAutoMoveVideo ? TEXT.AUTOMOVE_ACTIVE : TEXT.AUTOMOVE
      }
    }

    formatTime(seconds) {
      if (seconds < 0) seconds = 0
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = Math.floor(seconds % 60)
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    updateIndicator() {
      if (this.timelineIndicator) {
        this.timelineIndicator.textContent = `${this.currentIndex + 1} / ${this.timelines.length}`
      }
    }

    updateProgressIndicator(initial) {
      const currentTimeline = this.timelines[this.currentIndex]
      if (!initial && (!this.isPlaying || !this.videoElement || !currentTimeline))  {
        return
      }
      let currentTime = this.videoElement.currentTime - currentTimeline.start
      if (currentTime < 0 || currentTime > currentTimeline.end) {
        currentTime = 0
      }
      const duration = currentTimeline.end - currentTimeline.start
      if (this.progressIndicator) {
        this.progressIndicator.textContent = `${this.formatTime(currentTime)} / ${this.formatTime(duration)}`
      }
    }

    prevTimeline = () => {
      if (this.currentIndex > 0) {
        this.currentIndex--
        this.moveToCurrentTimeline()
        if (!this.isPlaying) {
          this.togglePlay()
        }
      }
    }

    nextTimeline = () => {
      if (this.currentIndex < this.timelines.length - 1) {
        this.currentIndex++
        this.moveToCurrentTimeline()
        if (!this.isPlaying) {
          this.togglePlay()
        }
      } else if (this.isAutoMoveVideo) {
        this.moveToNextVideo()
      } else {
        this.currentIndex = 0
        this.moveToCurrentTimeline()
      }
    }

    stop = () => {
      if (this.videoElement) {
        this.videoElement.pause()
      }
      if (this.autoPlayButtonImg) {
        this.playButtonImg.src = this.getIcon(ICONS.PLAY)
      }
      this.isPlaying = false
    }

    play = async () => {
      await wakeup()
      const currentTime = this.videoElement.currentTime
      const currentTimeline = this.timelines[this.currentIndex]
      if (!currentTimeline) return

      if (currentTime < currentTimeline.start || currentTime > currentTimeline.end) {
        this.moveToCurrentTimeline()
      }
      try {
        if (this.videoElement) {
          await this.videoElement.play()
        }
        if (this.playButtonImg) {
          this.playButtonImg.src = this.getIcon(ICONS.STOP)
        }
        this.isPlaying = true
      } catch (e) {
      }
    }

    togglePlay = () => {
      if (this.isPlaying) {
        this.stop()
      } else {
        this.play()
      }
    }

    seeked = () => {
      if (this.isProgrammaticSeek) {
        this.isProgrammaticSeek = false
        return
      }
      this.isPlaying = false
      this.playButtonImg.src = this.getIcon(ICONS.PLAY)
    }

    moveToCurrentTimeline = () => {
      if (!this.timelines || this.currentIndex < 0 || this.currentIndex >= this.timelines.length) {
        console.warn('Invalid timeline index or empty timelines')
        this.stop()
        return
      }
      this.activeTimelineList()
      if (this.videoElement) {
        const currentTimeline = this.timelines[this.currentIndex]
        this.isProgrammaticSeek = true
        this.videoElement.currentTime = currentTimeline.start
        this.updateIndicator()
      }
    }

    checkTimelineEnd = () => {
      setTimeout(() => {
        const currentTimeline = this.timelines[this.currentIndex]
        if (this.isPlaying && this.videoElement.currentTime >= currentTimeline.end) {
          if (this.currentIndex < this.timelines.length - 1) {
            this.nextTimeline()
          } else if (this.isAutoMoveVideo) {
            this.moveToNextVideo()
          } else {
            this.currentIndex = 0
            this.moveToCurrentTimeline()
          }
        }
      }, 0)
    }

    async fetchChannelVideos() {
      let page = 0
      let videos = []
      let totalPages = 1 // 초기값 설정

      while (page < totalPages) {
        const response = await fetch(`${CHZZK_CONSTANTS.CHZZK_VIDEO_LIST_API_URL}&page=${page}`)
        const data = await response.json()
        videos.push(...data.content.data)
        totalPages = data.content.totalPages // 마지막 페이지 정보 업데이트
        page++
      }

      return videos
    }

    async moveToNextVideo() {
      await wakeup()
      const totalVideos = await this.fetchChannelVideos()

      let currentIndex = this.videos.findIndex(video => video.videoNo === this.videoNo)

      let nextVideo
      for (let i = 1; i <= this.videos.length; i++) {
        const nextIndex = (currentIndex + i) % this.videos.length
        const candidateVideo = this.videos[nextIndex]

        if (totalVideos.some(video => video.videoNo === candidateVideo.videoNo)) {
          nextVideo = candidateVideo
          break
        }
      }
      if (nextVideo) {
        window.history.pushState({}, document.title, `/video/${nextVideo.videoNo}`)
        window.dispatchEvent(new Event('popstate'))
      }
    }

    checkAdPlaying() {
      if (this.controller === null) return
      const adVideo = document.querySelector('video[data-role="videoEl"]')
      const newAdState = !!adVideo
      if (newAdState !== this.isAdPlaying) {
        this.isAdPlaying = newAdState
        if (this.isAdPlaying) {
          this.stop()
        } else {
          this.play()
        }
      }
    }

    markPlayableRecommendVideos() {
      const videoItems = document.querySelectorAll('a[class^="vod_recommend_link__"]')
      videoItems.forEach((item) => {
        const href = item.getAttribute('href')
        const videoNoMatch = href.match(/\/video\/(\d+)/)
        if (!videoNoMatch) return

        const videoNo = Number(videoNoMatch[1])
        const isPlayable = this.videos.some((video) => video.videoNo === videoNo)
        const container = item.querySelector('div[class^="vod_recommend_thumbnail__"]')
        const existedIndicator = container.querySelector('.playable-indicator')
        if (isPlayable) {
          if (!existedIndicator) {
            const indicator = document.createElement('span')
            indicator.className = 'playable-indicator'
            indicator.textContent = TEXT.PLAYABLE
            container.appendChild(indicator)
          }
        } else {
          if (existedIndicator) {
            existedIndicator.remove()
          }
        }
      })
    }


    markPlayableVideos() {
      const videoItems = document.querySelectorAll('a[class^="video_card_thumbnail__"]')
      videoItems.forEach((item) => {
        const href = item.getAttribute('href')
        const videoNoMatch = href.match(/\/video\/(\d+)/)
        if (!videoNoMatch) return

        const videoNo = Number(videoNoMatch[1])
        const isPlayable = this.videos.some((video) => video.videoNo === videoNo)
        if (isPlayable) {
          if (!item.querySelector('.playable-indicator')) {
            const indicator = document.createElement('span')
            indicator.className = 'playable-indicator'
            indicator.textContent = TEXT.PLAYABLE
            item.appendChild(indicator)
          }
        } else {
          const indicator = item.querySelector('.playable-indicator')
          if (indicator) indicator.remove()
        }
      })
    }

    init() {
      this.destroy()
      this.findVideoElement()
    }

    destroy() {
      if (this.findVideoTimer) {
        clearTimeout(this.findVideoTimer)
      }
      if (this.videoElement) {
        this.videoElement.removeEventListener('timeupdate', this.timeupdate)
        this.videoElement.removeEventListener('pause', this.stop)
        this.videoElement.removeEventListener('seeked', this.seeked)
        this.videoElement = null
      }
      if (this.autoPlayButton) {
        this.autoPlayButton.removeEventListener('click', this.toggleAutoPlay)
        this.autoPlayButton.remove()
        this.autoPlayButton = null
        this.autoPlayButtonImg = null
      }
      if (this.autoMoveButton) {
        this.autoMoveButton.removeEventListener('click', this.toggleAutoMove)
        this.autoMoveButton.remove()
        this.autoMoveButton = null
        this.autoMoveButtonImg = null
      }
      if (this.nextButton) {
        this.nextButton.removeEventListener('click', this.nextTimeline)
        this.nextButton.remove()
        this.nextButton = null
      }
      if (this.playButton) {
        this.playButton.removeEventListener('click', this.togglePlay)
        this.playButton.remove()
        this.playButton = null
        this.playButtonImg = null
      }
      if (this.prevButton) {
        this.prevButton.removeEventListener('click', this.prevTimeline)
        this.prevButton.remove()
        this.prevButton = null
      }

      if (this.timelineIndicator) this.timelineIndicator = null
      if (this.progressIndicator) this.progressIndicator = null
      if (this.timelineDropdown) this.timelineDropdown = null

      if (this.controller) {
        this.controller.removeEventListener('click', this.preventControllerEvent)
        this.controller.removeEventListener('mouseenter', this.showTimelineDropdown)
        this.controller.removeEventListener('mouseleave', this.hideTimelineDropdown)
        this.controller.remove()
        this.controller = null
      }

      this.videoElement = null
      this.currentIndex = 0
      this.retryCount = 0
      this.videoNo = -1
      this.isPlaying = false
      this.isAdPlaying = false
      this.isProgrammaticSeek = false
      this.isAutoMoveVideo = false
      this.isAutoPlayVideo = false
    }

    activeTimelineList() {
      if (this.timelineDropdown) {
        this.timelineDropdown.querySelectorAll('.timeline-item').forEach((option, idx) => {
          if (idx === this.currentIndex) {
            option.classList.add('active')
          } else {
            option.classList.remove('active')
          }
        })
      }

    }

    createTimelineList() {
      this.timelineDropdown.innerHTML = ''
      this.timelines.forEach((timeline, index) => {
        const item = document.createElement('div')
        item.className = 'timeline-item'
        item.innerHTML = `<div>${index + 1}.</div><div title="${timeline.title}">${timeline.title}</div><div>${this.formatTime(timeline.end - timeline.start)}</div>`
        item.addEventListener('click', () => {
          this.currentIndex = index
          this.moveToCurrentTimeline()
          if (!this.isPlaying) this.togglePlay()
        })
        if (index === this.currentIndex) {
          item.classList.add('active') // 현재 선택된 타임라인 강조
        }
        this.timelineDropdown.appendChild(item)
      })
    }

    showTimelineDropdown = () => {
      this.timelineDropdown.style.display = 'block'
    }
    
    hideTimelineDropdown = () => {
      this.timelineDropdown.style.display = 'none'
    }

    checkContext() {
      return !!(chrome.runtime && chrome.runtime.id)
    }

    handleExtensionDisabled() {
      if (this.observer) {
        this.observer.disconnect()
      }
    }

    isValidVideoUrl() {
      const pattern = /^https:\/\/chzzk\.naver\.com\/video\/.*/
      return this.isDev || pattern.test(location.href)
    }

    isValidChannelVideosUrl() {
      const pattern = new RegExp(`^https:\\/\\/chzzk\\.naver\\.com\\/${TIMOONG_CHANNEL_ID}\\/videos(?:\\?.*|$)`)
      return pattern.test(window.location.href)
    }

    changeUrl() {
      const isPipMode = this.isPipModeActive()
      const isValidVideoUrl = this.isValidVideoUrl()
      const isValidChannelVideosUrl = this.isValidChannelVideosUrl()
      // let lastPipMode = isPipMode

      if (isValidVideoUrl && !isPipMode) {
        if (this.getVideoNoFromUrl() !== this.videoNo) {
          this.init()
        }
      } else if (!isValidVideoUrl && !isPipMode) {
        this.destroy()
      }

      if (isValidChannelVideosUrl) {
        setTimeout(() => {
          this.markPlayableVideos()
        }, 500)
      }
      if (isValidVideoUrl) {
        setTimeout(() => {
          this.markPlayableRecommendVideos()
        }, 500)
      }

      // if (!isValidVideoUrl && lastPipMode && !isPipMode) {
      //   this.destroy()
      //   lastPipMode = false
      // }

    }

    initObserver() {
      const excludedClasses = ['vod_chatting', 'progress-indicator', 'timeline-dropdown']
      let lastUrl = location.href
      let lastPipMode = false

      // chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      //   if (message.action === 'changeUrl') {
      //     console.log('Service Worker로부터 메시지:', message.url)
      //     this.changeUrl()
      //   }
      // })

      this.observer = new MutationObserver(debounce((items) => {
        const isPipMode = this.isPipModeActive()
        const isValidVideoUrl = this.isValidVideoUrl()
        const isValidChannelVideosUrl = this.isValidChannelVideosUrl()

        if (location.href !== lastUrl) {
          lastUrl = location.href
          lastPipMode = isPipMode

          if (isValidVideoUrl && !isPipMode) {
            if (this.getVideoNoFromUrl() !== this.videoNo) {
              this.init()
            }
          } else if (!isValidVideoUrl && !isPipMode) {
            this.destroy()
          }
        }

        if (!isValidVideoUrl && lastPipMode && !isPipMode) {
          this.destroy()
          lastPipMode = false
        }

        const filtered = items.filter((item) => !excludedClasses.some((clazz) => {
          return typeof item.target.className === 'string' && item.target.className.includes(clazz)
        }))
        if (filtered.length < 1) {
          return
        }

        if (isValidChannelVideosUrl) {
          this.markPlayableVideos()
        }
        if (isValidVideoUrl) {
          this.checkAdPlaying()
          this.markPlayableRecommendVideos()
        }
      }, 500))

      this.observer.observe(document, { subtree: true, childList: true })
    }

    
    // PIP 모드 감지 메서드
    isPipModeActive() {
      // 1. 기존 videoElement가 여전히 DOM에 존재하는지 확인
      if (this.videoElement && document.body.contains(this.videoElement)) {
        return !!document.querySelector('section[class*="vod_type_pip__"]')
      }
      if (document.pictureInPictureElement) {
        return true
      }
      return false
    }
  }

  const wakeup = throttle(() => {
    if (!chrome.runtime) return
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: "wakeup" }, async (response) => {
        resolve(response.status === 'ok')
      })
    })
  }, 10000)

  const getData = () => {
    if (!chrome.runtime) return
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ action: "data" }, (response) => {
        resolve(response)
      })
    })
  }

  async function start() {
    const data = await getData()
    const controller = new VideoTimelineController(data)
    await controller.setVideoData()
    if (controller.isDev || controller.isValidVideoUrl()) {
      controller.init()
    }
    controller.initObserver()
  }

  // 페이지 로드 시 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start)
  } else {
    start()
  }

})()
