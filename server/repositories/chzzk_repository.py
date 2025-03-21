from db.db_helper import execute_query

def get_video_timelines():
    query = """
        SELECT VIDEO_NO, TIMELINES, DEPLOY, PUBLISH_DATE FROM CHZZK_VIDEO
        WHERE PUBLISH_DATE >= DATE_SUB(DATE(NOW()), INTERVAL 60 DAY)
            AND PUBLISH_DATE <= DATE_SUB(DATE(NOW()), INTERVAL 6 DAY)
            AND DEPLOY = 1
        ORDER BY VIDEO_NO DESC
    """
    return execute_query(query)

def get_video_timelines_admin():
    query = "SELECT VIDEO_NO, TIMELINES, DEPLOY, PUBLISH_DATE FROM CHZZK_VIDEO ORDER BY VIDEO_NO DESC"
    return execute_query(query)


def get_video_timelines_by_video_no(videoNo: int):
    query = "SELECT VIDEO_NO, TIMELINES, DEPLOY FROM CHZZK_VIDEO WHERE VIDEO_NO = %s"
    return execute_query(query, (videoNo))
    

def add_video_timelines(video_no: int, channel_id: str, timelines: str, publish_date: str):
    """새 사용자 추가"""
    query = "INSERT INTO CHZZK_VIDEO (VIDEO_NO, CHANNEL_ID, TIMELINES, PUBLISH_DATE, DEPLOY, CREATED_TIME) VALUES (%s, %s, %s, %s, 0, NOW());"
    return execute_query(query, (video_no, channel_id, timelines, publish_date))


def edit_video_timelines(video_no: int, deploy: bool, timelines: str):
    query = "UPDATE CHZZK_VIDEO SET TIMELINES = %s, DEPLOY = %s WHERE VIDEO_NO = %s;"
    return execute_query(query, (timelines, deploy, video_no))