import logging
import logging.config
from pathlib import Path

# 로그 저장할 디렉터리 설정
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)  # logs 디렉터리가 없으면 생성

LOG_FILE = LOG_DIR / "app.log"

# 로그 설정
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "formatter": "standard",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# 로그 설정 적용
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("fastapi")
