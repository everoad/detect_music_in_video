from pydantic import BaseModel
from typing import List

class VideoAnalyzeRequest(BaseModel):
    video_url: str
    video_no: int
    channel_id: str

class Timeline(BaseModel):
    start: float
    end: float

class VideoAnalyzeResponse(BaseModel):
    video_no: int
    timelines: List[Timeline]

class TaskResponse(BaseModel):
    message: str
    video_no: int