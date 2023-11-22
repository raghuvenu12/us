from fastapi import APIRouter, Depends, HTTPException, status
from app.db.models import FutureTick, StockTick, FutureOrder
from app.config import get_settings
import app.db.schemas as schemas
from app.utils import client
from datetime import datetime, timezone
import time

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