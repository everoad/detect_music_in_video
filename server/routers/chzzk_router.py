from fastapi import APIRouter, BackgroundTasks, Request, Header, HTTPException
from httpx import AsyncClient, RequestError
from models.video_model import VideoAnalyzeRequest, VideoAnalyzeResponse, TaskResponse
from services.chzzk_service import analyze_video, find_video_timelines
from typing import List
from log.log_config import logger

VALID_API_KEY = 'S2tZV0dXY2U4MDdaUXlBbHU4UVE='

router = APIRouter(
    prefix="/chzzk",
    tags=["chzzk"],
)


@router.get("/videos/timeline")
async def get_video_timelines(authorization: str = Header(...)):
    if authorization != f"Bearer {VALID_API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")
    logger.info("GET /videos/timeline")
    return find_video_timelines()


@router.post("/videos/analyze", response_model=TaskResponse)
async def analyze_video_endpoint(video_data: VideoAnalyzeRequest, background_tasks: BackgroundTasks, authorization: str = Header(...)):
    if authorization != f"Bearer {VALID_API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    logger.info("GET /videos/analyze")
    
    background_tasks.add_task(analyze_video, video_data.video_url, video_data.video_no, video_data.channel_id)
    
    return {
        "message": "Analysis task started in the background",
        "video_no": video_data.video_no
    }


@router.get("/videos/{video_no}")
async def getVideo(video_no: str, request: Request, authorization: str = Header(...)):
    if authorization != f"Bearer {VALID_API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
      async with AsyncClient() as client:
          url = f"https://api.chzzk.naver.com/service/v3/videos/{video_no}"
          response = await client.get(url, headers={
              "Content-Type": "application/json",
              "User-Agent": request.headers.get('User-Agent', 'FastAPI/1.0')
          })
          return response.json()
    except RequestError as e:
      return {"error": f"RequestError: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

