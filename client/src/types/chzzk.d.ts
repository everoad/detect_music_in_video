
type ChzzkVideoCategory = 'music'

export interface ChzzkResponse<T> {
  code: number
  message: string
  content: T
}

export interface ChzzkContent<T> {
  data: T[]
  page: number
  size: number
  totalCount: number
  totalPages: number
}

export interface ChzzkChannel {
  channelId: string
  channelName: string
  channelImageUrl: string
  verifiedMark: boolean
  activatedChannelBadgeIds: string[]
}

export interface ChzzkVideo {
  videoNo: number
  videoId: string
  videoTitle: string
  videoType: "REPLAY" | "LIVE" | "VOD" // 비디오 타입 (예상되는 값)
  publishDate: string // "YYYY-MM-DD HH:mm:ss" 형식
  thumbnailImageUrl: string
  trailerUrl: string
  duration: number // 초 단위
  readCount: number
  publishDateAt: number // timestamp
  categoryType: string // ETC, GAME 등
  videoCategory: ChzzkVideoCategory
  videoCategoryValue: string
  exposure: boolean
  adult: boolean
  clipActive: boolean
  livePv: number
  channel: ChzzkChannel
  blindType: string
  watchTimeline: string
  paidPromotion: boolean
  inKey: string
  liveOpenDate: String
  vodStatus: string
  liveRewindPlaybackJson: string 
  prevVideo: ChzzkVideo
  nextVideo: ChzzkVideo
  userAdultStatus: boolean
  adParameter: {
    tag: string
  }
  videoChatEnabled: boolean
  videoChatChannelId: string
}



export interface ChzzkBaseURL {
  value: string
  serviceLocation: string 
  byteRange: string 
  availabilityTimeOffset: number 
  availabilityTimeComplete: boolean 
  otherAttributes: Record<string, any>
}

export interface ChzzkRepresentation {
  id: string
  width: number
  height: number 
  frameRate: number 
  mimeType: string 
  codecs: string 
  bandwidth: number
  qualityRanking: number 
  baseURL: ChzzkBaseURL[]
  segmentTemplate: ChzzkSegmentTemplate
  otherAttributes: {
    m3u: string
  }
}

export interface ChzzkAdaptationSet {
  mimeType: string
  baseURL: ChzzkBaseURL[]
  representation: ChzzkRepresentation[]
  otherAttributes: Record<string, any>
}

export interface ChzzkPeriod {
  id: string
  duration: string
  adaptationSet: ChzzkAdaptationSet[]
}

export interface ChzzkVideoMetadata {
  id: string 
  profiles: string
  type: string
  mediaPresentationDuration: string
  minBufferTime: string
  period: ChzzkPeriod[]
  otherAttributes: {
    videoId: string
    serverTime: string
    expireTime: string
  }
}

export interface MyChzzkVideoMetadata {
  frameRate: number
  height: number
  width: number
  mimeType: string
  bandwidth: number
  baseURL: string
  duration: number
}



export interface ChzzkVideoTimeline {
  videoNo: number
  timelines: {
    "start": number
    "end": number
  }[]
}


export interface ChzzkSegmentTimelineEntry {
  t: number // 시작 시간 (timestamp)
  n: number // 번호 (nullable)
  d: number // 지속 시간 (duration)
  r: number // 반복 횟수 (repetition)
  otherAttributes?: Record<string, any> // 추가 속성
}

export interface ChzzkSegmentTimeline {
  s: ChzzkSegmentTimelineEntry[] // 여러 개의 segment 정보
  any: any[] // 기타 추가 데이터
  otherAttributes: Record<string, any> // 추가 속성
}

export interface ChzzkSegmentTemplate {
  initialization?: string // 초기화 정보
  representationIndex: string // 인덱스 정보
  any: any[] // 기타 데이터
  timescale: number // 타임스케일 (예: 1000)
  presentationTimeOffset: number // 프레젠테이션 시간 오프셋
  indexRange: string // 인덱스 범위
  indexRangeExact?: boolean // 인덱스 범위가 정확한지 여부
  availabilityTimeOffset: number // 가용성 오프셋
  availabilityTimeComplete: boolean // 가용성 완료 여부
  otherAttributes: Record<string, any> // 추가 속성
  segmentTimeline: ChzzkSegmentTimeline // 세그먼트 타임라인 정보
  bitstreamSwitching: boolean // 비트스트림 전환 여부
  duration: number // 지속 시간
  startNumber: number // 시작 번호
  media: string // 세그먼트 파일 패턴
  index: string // 인덱스 정보
  initializationAttr: string // 초기화 속성
  bitstreamSwitchingAttr: string // 비트스트림 전환 속성
}