from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import chzzk_router, youtube_router
from pathlib import Path

app = FastAPI(
  root_path="/api",
)

origins = [
    "https://chzzk.naver.com",  # 허용할 출처
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 목록
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"]   # 허용할 HTTP 헤더
)

app.include_router(chzzk_router.router)
app.include_router(youtube_router.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


static_dir = Path("../client/dist")
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
