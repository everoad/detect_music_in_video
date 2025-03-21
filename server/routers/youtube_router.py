from fastapi import APIRouter, BackgroundTasks, Request, Header, HTTPException
from httpx import AsyncClient, RequestError
from models.video_model import VideoAnalyzeRequest, VideoModel, TaskResponse
from services.chzzk_service import analyze_video, find_video_timelines, save_video_timelines, find_video_timelines_by_video_no, find_video_timelines_admin
from typing import List
from log.log_config import logger

VALID_API_KEY = 'S2tZV0dXY2U4MDdaUXlBbHU4UVE='
router = APIRouter(
    prefix="/youtube",
    tags=["youtube"],
)

CHANNEL_ID = 'UCRU9FOLAAJkWxyktN4Ydf8w'
YOUTUBE_API_KEY = 'AIzaSyCHEPqZIOcNX9F_zV2Bpd712TA8MXuvyWU'


@router.get("/videos")
async def get_videos(request: Request, authorization: str = Header(...)):
    if authorization != f"Bearer {VALID_API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        async with AsyncClient() as client:
            # 1. 채널의 업로드 플레이리스트 ID 가져오기
            playlist_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={CHANNEL_ID}&key={YOUTUBE_API_KEY}"
            playlist_response = await client.get(playlist_url)
            playlist_data = playlist_response.json()

            if "items" not in playlist_data or not playlist_data["items"]:
                return {"error": "Playlist ID not found"}
            
            playlist_id = playlist_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # 2. 플레이리스트에서 모든 영상 가져오기 (페이지네이션)
            videos = []
            next_page_token = ""

            while True:
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"
                if next_page_token:
                    url += f"&pageToken={next_page_token}"

                response = await client.get(url, headers={
                    "Content-Type": "application/json",
                    "User-Agent": request.headers.get('User-Agent', 'FastAPI/1.0')
                })
                
                data = response.json()

                if "items" not in data:
                    break

                for item in data["items"]:
                    video_id = item["snippet"]["resourceId"]["videoId"]
                    videos.append({
                        "title": item["snippet"]["title"],
                        "url": f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}",
                        "thumbnail": item["snippet"]["thumbnails"].get("high", {}).get("url", "")
                    })

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break
            
            return videos

    except RequestError as e:
        return {"error": f"RequestError: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}