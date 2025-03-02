from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import chzzk_router

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
    allow_methods=["GET"],
    allow_headers=["Authorization"]   # 허용할 HTTP 헤더
)

app.include_router(chzzk_router.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# app.mount(
#     "/", 
#     StaticFiles(directory=Path("../client/dist"), html=True), 
#     name="static",
# )
