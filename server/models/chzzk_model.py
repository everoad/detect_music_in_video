from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal, TypeVar, Generic
from datetime import datetime

# 제네릭 타입 변수 정의
T = TypeVar("T")

# ChzzkVideoCategory 타입
ChzzkVideoCategory = Literal["music"]

# ChzzkResponse (제네릭)
class ChzzkResponse(BaseModel, Generic[T]):
    code: int
    message: str
    content: T

    class Config:
        arbitrary_types_allowed = True  # 제네릭 타입 허용

# ChzzkContent (제네릭)
class ChzzkContent(BaseModel, Generic[T]):
    data: List[T]
    page: int
    size: int
    totalCount: int
    totalPages: int

    class Config:
        arbitrary_types_allowed = True  # 제네릭 타입 허용

# ChzzkChannel
class ChzzkChannel(BaseModel):
    channelId: str
    channelName: str
    channelImageUrl: str
    verifiedMark: bool
    activatedChannelBadgeIds: List[str]

# ChzzkVideo
class ChzzkVideo(BaseModel):
    videoNo: int
    videoId: str
    videoTitle: str
    videoType: Literal["REPLAY", "LIVE", "VOD"]
    publishDate: str  # "YYYY-MM-DD HH:mm:ss" 형식으로 문자열 처리
    thumbnailImageUrl: str
    trailerUrl: str
    duration: int  # 초 단위
    readCount: int
    publishDateAt: int  # timestamp
    categoryType: str  # ETC, GAME 등
    videoCategory: ChzzkVideoCategory
    videoCategoryValue: str
    exposure: bool
    adult: bool
    clipActive: bool
    livePv: int
    channel: ChzzkChannel
    blindType: str
    watchTimeline: str
    paidPromotion: bool
    inKey: str
    liveOpenDate: str
    vodStatus: str
    liveRewindPlaybackJson: str
    prevVideo: Optional["ChzzkVideo"] = None  # 순환 참조 처리
    nextVideo: Optional["ChzzkVideo"] = None  # 순환 참조 처리
    userAdultStatus: bool
    adParameter: Dict[str, str]  # { "tag": str }
    videoChatEnabled: bool
    videoChatChannelId: str

# 순환 참조 해결 (Pydantic 2.x에서는 필요 시 명시적 호출)
ChzzkVideo.model_rebuild()

# ChzzkBaseURL
class ChzzkBaseURL(BaseModel):
    value: str
    serviceLocation: str
    byteRange: str
    availabilityTimeOffset: int
    availabilityTimeComplete: bool
    otherAttributes: Dict[str, Any]

# ChzzkSegmentTimelineEntry
class ChzzkSegmentTimelineEntry(BaseModel):
    t: int  # 시작 시간 (timestamp)
    n: Optional[int] = None  # 번호 (nullable)
    d: int  # 지속 시간 (duration)
    r: int  # 반복 횟수 (repetition)
    otherAttributes: Optional[Dict[str, Any]] = None

# ChzzkSegmentTimeline
class ChzzkSegmentTimeline(BaseModel):
    s: List[ChzzkSegmentTimelineEntry]
    any: List[Any]
    otherAttributes: Dict[str, Any]

# ChzzkSegmentTemplate
class ChzzkSegmentTemplate(BaseModel):
    initialization: Optional[str] = None
    representationIndex: str
    any: List[Any]
    timescale: int
    presentationTimeOffset: int
    indexRange: str
    indexRangeExact: Optional[bool] = None
    availabilityTimeOffset: int
    availabilityTimeComplete: bool
    otherAttributes: Dict[str, Any]
    segmentTimeline: ChzzkSegmentTimeline
    bitstreamSwitching: bool
    duration: int
    startNumber: int
    media: str
    index: str
    initializationAttr: str
    bitstreamSwitchingAttr: str

# ChzzkRepresentation
class ChzzkRepresentation(BaseModel):
    id: str
    width: int
    height: int
    frameRate: int
    mimeType: str
    codecs: str
    bandwidth: int
    qualityRanking: int
    baseURL: List[ChzzkBaseURL]
    segmentTemplate: ChzzkSegmentTemplate
    otherAttributes: Dict[str, str]  # { "m3u": str }

# ChzzkOtherAttributes
class ChzzkOtherAttributes(BaseModel):
    m3u: str

# ChzzkAdaptationSet
class ChzzkAdaptationSet(BaseModel):
    mimeType: str
    baseURL: List[ChzzkBaseURL]
    representation: List[ChzzkRepresentation]
    otherAttributes: ChzzkOtherAttributes

# ChzzkPeriod
class ChzzkPeriod(BaseModel):
    id: str
    duration: str
    adaptationSet: List[ChzzkAdaptationSet]

# ChzzkVideoMetadata
class ChzzkVideoMetadata(BaseModel):
    id: str
    profiles: str
    type: str
    mediaPresentationDuration: str
    minBufferTime: str
    period: List[ChzzkPeriod]
    otherAttributes: Dict[str, str]  # { "videoId": str, "serverTime": str, "expireTime": str }

# MyChzzkVideoMetadata
class MyChzzkVideoMetadata(BaseModel):
    frameRate: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    mimeType: Optional[str] = None
    bandwidth: Optional[int] = None
    baseURL: str

# ChzzkVideoTimeline
class ChzzkVideoTimeline(BaseModel):
    videoNo: int
    timelines: List[Dict[str, float]]  # { "start": number, "end": number }