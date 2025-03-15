// videoSearchController.js
class MusicSearchController {
  constructor(timelineController) { // timelines를 생성자에서 받거나 setter로 설정 가능
    this.timelineController = timelineController

    this.searchContainer = null
    this.isDragging = false
    this.currentX = 0
    this.currentY = 0
    this.initialX = 0
    this.initialY = 0
    
    this.storage = new StorageAdapter()
    this.createSearchUI()
  }

  // 검색 UI 생성
  createSearchUI() {
    // 컨테이너 생성
    this.searchContainer = document.createElement('div')
    this.searchContainer.className = 'video-search-container'

    // 검색 입력창
    this.searchInput = document.createElement('input')
    this.searchInput.type = 'text'
    this.searchInput.placeholder = '티뭉 노래 검색...'
    this.searchInput.className = 'search-input'
    this.searchContainer.appendChild(this.searchInput)

    // 결과 드롭다운
    this.resultsDropdown = document.createElement('div')
    this.resultsDropdown.className = 'search-results-dropdown'
    this.resultsDropdown.style.display = 'none'
    this.searchContainer.appendChild(this.resultsDropdown)

    // 이벤트 리스너 추가
    this.searchInput.addEventListener('input', this.handleSearch)

    // 드래그 이벤트 추가
    // this.searchContainer.addEventListener('mousedown', this.startDragging.bind(this))
    // document.addEventListener('mousemove', this.drag.bind(this))
    // document.addEventListener('mouseup', this.stopDragging.bind(this))

    // 페이지에 추가
    document.body.appendChild(this.searchContainer)

    // this.centerSearchContainer()
  }


  // 검색 컨테이너를 화면 가운데로 이동
  centerSearchContainer() {

    this.currentX = 250
    this.currentY = 7.5

    this.searchContainer.style.left = `${this.currentX}px`
    this.searchContainer.style.top = `${this.currentY}px`
  }

  async getTimelines() {
    const videos = await this.storage.get(STORAGE_KEYS.VIDEOS, [])
    return videos.flatMap((video) => {
      return video.timelines.map((timeline, idx) => ({
        ...timeline,
        ...video,
        timelineIndex: idx
      }))
    })

  }


  // 검색 처리
  handleSearch = debounce(async () => {
    const query = this.searchInput.value.trim().toLowerCase()
    this.resultsDropdown.innerHTML = '' // 기존 결과 초기화
    this.resultsDropdown.style.display = 'none'
    
    if (!query) {
      return
    }
    
    const timelines = await this.getTimelines()
    const filteredTimelines = timelines.filter(timeline =>
      timeline.title.toLowerCase().includes(query)
    )

    if (filteredTimelines.length === 0) {
      return
    }
    this.resultsDropdown.style.display = 'block'

    filteredTimelines.forEach((timeline) => {
      const item = document.createElement('div')
      item.className = 'search-result-item'
      item.innerHTML = `
        <div title="${timeline.title}">${timeline.title}</div>
        <div>${formatDate(timeline.publishDate)}</div>
      `

      item.addEventListener('click', () => {
        window.history.pushState({}, document.title, `/video/${timeline.videoNo}`)
        window.dispatchEvent(new Event('popstate'))

        // VideoTimelineController에 전달할 커스텀 이벤트 발생
        const event = new CustomEvent('videoSelected', {
          detail: {
            videoNo: timeline.videoNo,
            timelineIndex: timeline.timelineIndex
          }
        });
        window.dispatchEvent(event)
        this.searchInput.value = ''
        this.resultsDropdown.style.display = 'none'
      })

      this.resultsDropdown.appendChild(item)


    })
  }, 500)

  // 드래그 시작
  startDragging(e) {
    this.isDragging = true
    this.initialX = e.clientX - this.currentX
    this.initialY = e.clientY - this.currentY 
    this.searchContainer.style.cursor = 'grabbing'
  }

  // 드래그 중
  drag(e) {
    if (!this.isDragging) return
    e.preventDefault()
    this.currentX = e.clientX - this.initialX
    this.currentY = e.clientY - this.initialY
    this.searchContainer.style.left = `${this.currentX}px`
    this.searchContainer.style.top = `${this.currentY}px`
  }

  // 드래그 종료
  stopDragging() {
    this.isDragging = false
    this.searchContainer.style.cursor = 'grab'
  }

  // timelines 설정 메서드 (외부에서 데이터 주입용)
  setTimelines(timelines) {
    this.timelines = timelines
  }
}