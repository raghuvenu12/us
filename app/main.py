from datetime import datetime, timezone
from fastapi import FastAPI
from app.routers import (post, report, user)
from app.db.session import init_db

app = FastAPI()

app.include_router(post.router)


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Hello World"}