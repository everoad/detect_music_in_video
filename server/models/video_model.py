from pydantic import BaseModel
from typing import List, Optional

class VideoAnalyzeRequest(BaseModel):
    video_url: str
    video_no: int
    channel_id: str
    publish_date: str

class Timeline(BaseModel):
    start: float
    end: float
    title: Optional[str] = None

class VideoModel(BaseModel):
    videoNo: int
    deploy: bool
    publishDate: str
    timelines: List[Timeline]

class TaskResponse(BaseModel):
    message: str
    video_no: int