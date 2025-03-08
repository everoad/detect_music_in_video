from db.db_helper import execute_query

def get_video_timelines():
    query = "SELECT VIDEO_NO, TIMELINES, DEPLOY FROM CHZZK_VIDEO ORDER BY VIDEO_NO DESC"
    return execute_query(query)


def get_video_timelines_by_video_no(videoNo: int):
    query = "SELECT VIDEO_NO, TIMELINES, DEPLOY FROM CHZZK_VIDEO WHERE VIDEO_NO = %s"
    return execute_query(query, (videoNo))
    

def add_video_timelines(video_no: int, channel_id: str, timelines: str):
    """새 사용자 추가"""
    query = "INSERT INTO CHZZK_VIDEO (VIDEO_NO, CHANNEL_ID, TIMELINES, DEPLOY, CREATED_TIME) VALUES (%s, %s, %s, 0, NOW());"
    return execute_query(query, (video_no, channel_id, timelines))


def edit_video_timelines(video_no: int, deploy: bool, timelines: str):
    print(f"no: {video_no}, timelines: {timelines}")
    query = "UPDATE CHZZK_VIDEO SET TIMELINES = %s, DEPLOY = %s WHERE VIDEO_NO = %s;"
    return execute_query(query, (timelines, deploy, video_no))