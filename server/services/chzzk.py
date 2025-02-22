

def find_chzzk_video_timeline(video_no: int):
    return {
        "videoNo": video_no,
        "timelines": [
            {"start": 0, "end": 30},
            {"start": 60, "end": 120},
            {"start": 180, "end": 240},
            {"start": 300, "end": 360},
        ]
    }