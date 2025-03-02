from db.db_helper import execute_query

def get_video_timelines():
    query = "SELECT VIDEO_NO, TIMELINES FROM CHZZK_VIDEO ORDER BY VIDEO_NO DESC"
    return execute_query(query)



def find_video_by_no(video_no: int):
    query = "SELECT VIDEO_NO FROM CHZZK_VIDEO WHERE VIDEO_NO = %s"
    return execute_query(query, (video_no))
    

def add_video_timelines(video_no: int, channel_id: str, timelines: str):
    """새 사용자 추가"""
    query = "INSERT INTO CHZZK_VIDEO (VIDEO_NO, CHANNEL_ID, TIMELINES, CREATED_TIME) VALUES (%s, %s, %s, NOW());"
    return execute_query(query, (video_no, channel_id, timelines))

