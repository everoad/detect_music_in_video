import type { ChzzkVideo, ChzzkContent, ChzzkResponse, ChzzkVideoMetadata, ChzzkVideoTimeline, ChzzkMusicRegister } from "@/types/chzzk";
import { $fetch } from "@/utils/my-fetch";

const CHANNEL_ID = '26253bf7ed6b95832c40f4f43f6d049d'
const API_KEY = 'S2tZV0dXY2U4MDdaUXlBbHU4UVE='

export async function fetchChzzkChannelVideos(params?: { page: number }): Promise<ChzzkContent<ChzzkVideo>> {
  const res = await $fetch(`/api/chzzk/channels/${CHANNEL_ID}/videos`, { method: 'GET', params })
  const data = await res.json() as ChzzkResponse<ChzzkContent<ChzzkVideo>>

  return data.content
}


export async function fetchChzzkVideo(videoNo: number): Promise<ChzzkVideo> {
  const res = await $fetch(`/api/chzzk/videos/${videoNo}`, { 
    headers: {        
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}` 
    }
  })
  const data = await res.json() as ChzzkResponse<ChzzkVideo>
  return data.content
}

export async function fetchVideoMetadata(videoId: string, inKey: string): Promise<ChzzkVideoMetadata> {
  const response = await fetch(`https://apis.naver.com/neonplayer/vodplay/v2/playback/${videoId}?key=${inKey}`)
  const data = await response.json() as ChzzkVideoMetadata
  return data
}

export async function fetchVideoTimelines(): Promise<ChzzkVideoTimeline[]> {
  const response = await fetch(`/api/chzzk/videos/timeline`, {
    headers: {        
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}` 
    }
  })
  const data = await response.json() as ChzzkVideoTimeline[]
  return data
}

export async function editVideoTimelines(videos: ChzzkVideoTimeline) {
  const response = await fetch(`/api/chzzk/videos/timeline`, {
    method: 'POST',
    headers: {        
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}` 
    },
    body: JSON.stringify(videos)
  })
}

export async function addVideo(video: ChzzkMusicRegister) {
  const response = await fetch(`/api/chzzk/videos/analyze`, {
    method: 'POST',
    headers: {        
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}` 
    },
    body: JSON.stringify({ ...video, channel_id: CHANNEL_ID })
  })
  return await response.json()
}

export async function isCompletedProccess(videoNo: number) {
  const response = await fetch(`/api/chzzk/video/complete?videoNo=${videoNo}`, {
    headers: {        
      'Content-Type': 'application/json',
      Authorization: `Bearer ${API_KEY}` 
    }
  })
  return await response.json()
}
