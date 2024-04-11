from fastapi import FastAPI
import uvicorn

from contacts.routes import router

app = FastAPI()

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app="main:app",
                host="localhost",
                port=8080,
                reload=True)
