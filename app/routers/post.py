from fastapi import APIRouter, Depends, HTTPException, status
from app.config import get_settings
import app.db.schemas as schemas
from datetime import datetime, timezone
import time
from app.db.models import User

# Get application settings from the configuration module
settings = get_settings()

# Create an APIRouter instance
router = APIRouter()

__all__ = (
    'future_one_min'
)

# create a post
@router.post("/post/create")
async def create():
    return {"message": "Hello World"}

@router.get("/post/test")
async def create():
    users = await User.all()
    print(users)
    return {"phone": users[0].phone}