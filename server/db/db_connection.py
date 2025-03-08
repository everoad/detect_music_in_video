import mariadb
from threading import Lock

# 데이터베이스 연결 정보
DB_CONFIG = {
    "host": "172.237.27.244",  # 예: "localhost"
    "port": 3306,              # 기본 포트
    "user": "web_reader",
    "password": "!Q@W3e4r",
    "database": "detect_music"
}

# 풀 크기 설정
POOL_SIZE = 10  # 동시 최대 연결 개수

class MariaDBPool:
    """MariaDB Connection Pool 관리 클래스"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        """싱글톤 패턴 적용"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_pool()
        return cls._instance

    def _init_pool(self):
        """Connection Pool 생성"""
        try:
            self.pool = mariadb.ConnectionPool(pool_name="mypool",
                                               pool_size=POOL_SIZE,
                                               **DB_CONFIG)
            print("✅ MariaDB Connection Pool 생성 완료")
        except mariadb.Error as e:
            print(f"❌ Connection Pool 생성 실패: {e}")
            self.pool = None

    def get_connection(self):
        """풀에서 연결 가져오기"""
        if not self.pool:
            print("❌ Connection Pool 없음, 연결 실패")
            return None
        try:
            return self.pool.get_connection()
        except mariadb.Error as e:
            print(f"❌ Connection 가져오기 실패: {e}")
            return None

# 싱글톤 풀 인스턴스 생성
mariadb_pool = MariaDBPool()
