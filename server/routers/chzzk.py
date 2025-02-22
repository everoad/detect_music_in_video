from fastapi import Query, Request, APIRouter
from httpx import AsyncClient, RequestError
from ..services import chzzk as chzzk_service

router = APIRouter(
    prefix="/chzzk",
    tags=["chzzk"],
)


@router.get("/channels/{channel_id}/videos")
async def getChannelVideos(
    channel_id: str, 
    request: Request,
    page: int = Query(default=0, ge=0, description="Page number")
):
    try:
      async with AsyncClient() as client:
          url = f"https://api.chzzk.naver.com/service/v1/channels/{channel_id}/videos?sortType=LATEST&pagingType=PAGE&page={page}&size=16&publishDateAt=&videoType="
          print(f"Requesting {url}")
          response = await client.get(url, headers={
              "Content-Type": "application/json",
              "User-Agent": request.headers.get('User-Agent', 'FastAPI/1.0')
          })
          return response.json()
    except RequestError as e:
      return {"error": f"RequestError: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
      

@router.get("/videos/{video_no}")
async def getVideo(video_no: str, request: Request):
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
    
    
@router.get("/videos/{video_no}/timeline")
async def getVideoTimeline(video_no: int):
    print("getVideoTimeline")
    return {
        "videoNo": video_no,
        "timelines": [
            {"start": 0, "end": 30},
            {"start": 60, "end": 120},
            {"start": 180, "end": 240},
            {"start": 300, "end": 360},
        ]
    }   