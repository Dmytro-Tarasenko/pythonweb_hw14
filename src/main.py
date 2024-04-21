import uvicorn
from fastapi import FastAPI

from contacts.routes import router
from auth.routes import router as auth_router

app = FastAPI()

app.include_router(router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run(app="main:app",
                host="localhost",
                port=8080,
                reload=True)
