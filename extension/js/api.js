
class ApiService {
  constructor(baseUrl, apiKey, timeLineApiUrl, storage) {
    this.baseUrl = baseUrl
    this.apiKey = apiKey
    this.timeLineApiUrl = timeLineApiUrl
    this.storage = storage
  }

  async fetchVideos() {
    try {
      const response = await fetch(`${this.baseUrl}${this.timeLineApiUrl}`, {
        headers: { Authorization: `Bearer ${this.apiKey}` }
      })
      if (!response.ok) {
        throw new Error(`Failed to fetch timelines: ${response.status}`)
      }
      let videos = await response.json()
      
      videos = videos.filter((video) => video.deploy === 1)
      
      await this.storage.set(STORAGE_KEYS.VIDEOS, videos)
      await this.storage.set(STORAGE_KEYS.LAST_CALL_API_TIME, Date.now())
      return videos
    } catch (error) {
      console.warn('Failed to fetch timelines:', error)
      return await this.storage.get(STORAGE_KEYS.VIDEOS, [])
    }
  }

  async fetchChannelVideos() {
    let page = 0
    let videos = []
    let totalPages = 1

    while (page < totalPages) {
      const response = await fetch(`${CHZZK_CONSTANTS.CHZZK_VIDEO_LIST_API_URL}&page=${page}`)
      const data = await response.json()
      videos.push(...data.content.data)
      totalPages = data.content.totalPages
      page++
    }
    return videos
  }

  async isTimoong(videoNo) {
    try {
      const response = await fetch(`${CHZZK_CONSTANTS.CHZZK_VIDEO_API_URL}${videoNo}`)
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
}