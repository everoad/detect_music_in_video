'use strict'

class MusicSearchController {
  constructor(api, storage) { // timelines를 생성자에서 받거나 setter로 설정 가능
    this.searchContainer = null
    this.isDragging = false
    this.currentX = 0
    this.currentY = 0
    this.initialX = 0
    this.initialY = 0
    this.youtubeVideos = []
    this.api = api
    this.storage = storage
    this.createSearchUI()
    this.initObserver()
  }

  initObserver() {
    new MutationObserver(() => {
      const container = this.getToolbarContainerElmement()
      if (container) {
        if (this.searchContainer) {
          container.append(this.searchContainer)
        }
      } else {
        if (this.searchContainer && this.searchContainer.parentElement) {
          this.searchContainer.parentElement.removeChild(this.searchContainer)
        }
      }

    })
    .observe(document.querySelector('div[class^="layout_glive__"'), { childList: true })
  }

  getToolbarContainerElmement() {
    return document.querySelector('div[class^="toolbar_container__"')
  }

  // 검색 UI 생성
  createSearchUI() {
    // 컨테이너 생성
    this.searchContainer = document.createElement('div')
    this.searchContainer.className = 'video-search-container'

    // 검색 입력창
    this.searchInput = document.createElement('input')
    this.searchInput.type = 'text'
    this.searchInput.placeholder = '티뭉 노래 검색'
    this.searchInput.className = 'search-input'
    this.searchContainer.appendChild(this.searchInput)

    // 결과 드롭다운
    this.resultsDropdown = document.createElement('div')
    this.resultsDropdown.className = 'search-results-dropdown'
    this.resultsDropdown.style.display = 'none'
    this.searchContainer.appendChild(this.resultsDropdown)

    // 이벤트 리스너 추가
    this.searchInput.addEventListener('click', this.handleSearch)
    this.searchInput.addEventListener('blur', debounce(this.handleBlurSearch, 300))
    this.searchInput.addEventListener('input', debounce(this.handleSearch, 500))

    // 페이지에 추가
    this.getToolbarContainerElmement().appendChild(this.searchContainer)
  }

  async getTimelines() {
    const videos = await this.storage.get(STORAGE_KEYS.VIDEOS, [])
    const y_videos = await this.storage.get(STORAGE_KEYS.Y_VIDOES, [])

    const chzzkTimelines = videos.flatMap((video) => {
      return video.timelines.map((timeline, idx) => ({
        ...timeline,
        ...video,
        timelineIndex: idx
      }))
    })
    return [...y_videos, ...chzzkTimelines]
  }

  cleanText = (text) => {
    if (!text) {
      return ''
    }
    return text.replace(/[^가-힣a-zA-Z0-9]/g, '').toLowerCase()
  }

  handleBlurSearch = () => {
    this.resultsDropdown.innerHTML = ''
    this.resultsDropdown.style.display = 'none'
  }

  // 검색 처리
  handleSearch = async () => {
    const query = this.searchInput.value.trim().toLowerCase()
    this.resultsDropdown.innerHTML = ''
    this.resultsDropdown.style.display = 'none'

    if (!query) {
      return
    }
    
    const timelines = await this.getTimelines()
    const filteredTimelines = timelines.filter(timeline => 
      this.cleanText(timeline.title).includes(this.cleanText(query)))

    if (filteredTimelines.length === 0) {
      return
    }
    this.resultsDropdown.style.display = 'block'

    filteredTimelines.forEach((timeline) => {
      const item = document.createElement('div')
      item.className = 'search-result-item'
      if (timeline.url) {
        item.innerHTML = `
          <div title="${timeline.title}">${timeline.title}</div>
          <div>Youtube</div>
        `
        item.addEventListener('click',() => {
          window.open(timeline.url, "_blank")

          const event = new CustomEvent(EVENTS.VIDEO_STOP)
          window.dispatchEvent(event)
          this.searchInput.value = ''
          this.resultsDropdown.style.display = 'none'
        })
      } else {
        item.innerHTML = `
          <div title="${timeline.title}">${timeline.title}</div>
          <div>${formatDate(timeline.publishDate)}</div>
        `
        item.addEventListener('click', () => {
          window.history.pushState({}, document.title, `/video/${timeline.videoNo}`)
          window.dispatchEvent(new Event('popstate'))
  
          const event = new CustomEvent(EVENTS.VIDEO_SELECTED, {
            detail: {
              videoNo: timeline.videoNo,
              timelineIndex: timeline.timelineIndex
            }
          })
          window.dispatchEvent(event)
          this.searchInput.value = ''
          this.resultsDropdown.style.display = 'none'
        })
      }



      this.resultsDropdown.appendChild(item)


    })
  }
}