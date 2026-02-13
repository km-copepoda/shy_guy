import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import mosaic
from services.face_detector import FaceDetector


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.face_detector = FaceDetector()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(mosaic.router, prefix="/api", tags=["mosaic"])

# CORS settings
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
