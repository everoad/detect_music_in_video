from db.db_connection import mariadb_pool

def to_camel_case(snake_str):
    """스네이크 케이스(SNAKE_CASE) → 카멜 케이스(camelCase) 변환"""
    parts = snake_str.lower().split('_')  # 언더스코어 기준 분리
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def execute_query(query, params=None):
    """쿼리 실행 후 List[Dict] 형태로 반환"""
    conn = mariadb_pool.get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        
        # SELECT 문인지 확인
        if cursor.description:  
            # SELECT문이라면 컬럼명 변환 후 데이터 가져오기
            columns = [to_camel_case(col[0]) for col in cursor.description]
            results = [dict(zip(columns, row)) for row in (cursor.fetchall() or [])]
        else:
            # SELECT가 아닌 경우, 변경된 row 개수만 반환
            results = {"affectedRows": cursor.rowcount}

        conn.commit()
        return results
    except Exception as e:
        print(f"❌ 쿼리 실행 오류: {e}")
        return None
    finally:
        cursor.close()
        conn.close()  # 풀에 반환
