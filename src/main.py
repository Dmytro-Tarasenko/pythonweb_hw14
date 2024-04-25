from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from contacts.routes import router
from auth.routes import router as auth_router
from email_service.routes import router as email_router
from settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    r = await redis.Redis(host=settings.redis_server,
                          port=settings.redis_port,
                          password=settings.redis_pass,
                          db=0,
                          decode_responses=True,
                          encoding='utf-8')
    await FastAPILimiter.init(r)

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.include_router(auth_router)
app.include_router(email_router)

origins = [
    "http://localhost:8080",
    "https://localhost:8080",
    "http://localhost:8000",
    "https://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app="main:app",
                host="localhost",
                port=8080,
                reload=True)
