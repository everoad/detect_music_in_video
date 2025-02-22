import type { ChzzkVideo, ChzzkContent, ChzzkResponse, ChzzkVideoMetadata, ChzzkVideoTimeline } from "@/types/chzzk";
import { $fetch } from "@/utils/my-fetch";

const CHANNEL_ID = '26253bf7ed6b95832c40f4f43f6d049d'

export async function fetchChzzkChannelVideos(params?: { page: number }): Promise<ChzzkContent<ChzzkVideo>> {
  const res = await $fetch(`/api/chzzk/channels/${CHANNEL_ID}/videos`, { method: 'GET', params })
  const data = await res.json() as ChzzkResponse<ChzzkContent<ChzzkVideo>>

  return data.content
}


export async function fetchChzzkVideo(videoNo: number): Promise<ChzzkVideo> {
  const res = await $fetch(`/api/chzzk/videos/${videoNo}`, { method: 'GET' })
  const data = await res.json() as ChzzkResponse<ChzzkVideo>
  return data.content
}

export async function fetchVideoMetadata(videoId: string, inKey: string): Promise<ChzzkVideoMetadata> {
  const response = await fetch(`https://apis.naver.com/neonplayer/vodplay/v1/playback/${videoId}?key=${inKey}`)
  const data = await response.json() as ChzzkVideoMetadata
  return data
}

export async function fetchVideoTimeline(videoNo: number): Promise<ChzzkVideoTimeline> {
  const response = await fetch(`/api/chzzk/videos/${videoNo}/timeline`)
  const data = await response.json() as ChzzkVideoTimeline
  return data
}