from fastapi import FastAPI
import uvicorn

from routes import router

app = FastAPI()

app.include_router(router)

