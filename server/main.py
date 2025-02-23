from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import chzzk

import subprocess
import uvicorn

app = FastAPI(
  root_path="/api",
)


app.include_router(chzzk.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# app.mount(
#     "/", 
#     StaticFiles(directory=Path("../client/dist"), html=True), 
#     name="static",
# )
