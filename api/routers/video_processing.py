"""
Video Processing Router
Handles video transcription, processing, and bulk operations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import json

from core.database import SessionLocal, Video
from core.services.transcript_service import get_english_transcript
from core.services.video_service import get_video_title
from api.models import (
    ProcessVideoRequest,
    ProcessVideoResponse,
    BulkVideoProcessRequest,
    BulkVideoProcessResponseItem
)
from api.config import CONTENT_STYLE_PRESETS
from repurpose import (
    generate_content_ideas,
    generate_specific_content_pieces,
    ContentIdea,
    extract_video_id as repurpose_extract_video_id
)
from pydantic import ValidationError

router = APIRouter(prefix="", tags=["video-processing"])
executor = ThreadPoolExecutor(max_workers=10)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Import will come from main after refactoring
# This is a placeholder - actual implementation stays in main.py for now
# We'll gradually move logic to services

