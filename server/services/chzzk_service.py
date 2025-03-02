from fastapi import APIRouter
from libs.music.music import detect_music_sections, extract_audio_from_url
import json
from datetime import datetime
from repositories.chzzk_repository import add_video_timelines, get_video_timelines

main_dir = '/home/beomjk/chzzk/'

router = APIRouter(
    prefix="/chzzk",
    tags=["chzzk"],
)

def find_video_timelines():
    videos = get_video_timelines()
    print(videos)
    for item in videos:
        try:
            item["timelines"] = json.loads(item["timelines"])  # 문자열 → JSON 변환
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류 (video_no={item['video_no']}): {e}")
            
    return videos
    

def analyze_video(video_url: str, video_no: str, channel_id: str):
    audio_output_path = f"{video_no}.wav"
    
    try:
        # 1. 오디오 추출
        extract_audio_from_url(video_url, audio_output_path)
        
        # 2. 음악 구간 탐지
        music_segments = detect_music_sections(audio_output_path)
        
        # 3. 결과 변환 (timelines 생성)
        timelines = [
            {"start": float(min(segment)), "end": float(max(segment))}
            for segment in music_segments
        ]
        
        # 4. JSON 문자열로 변환
        timelines_str = json.dumps(timelines)
        
        add_video_timelines(video_no=video_no, channel_id=channel_id, timelines=timelines_str)
        
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")
