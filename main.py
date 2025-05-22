import logging
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, HttpUrl, ValidationError, Field, root_validator
from sqlalchemy.orm import Session
import asyncio # For run_in_executor
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any
from database import init_db, SessionLocal, Video
from transcript import fetch_transcript
from repurpose import generate_content_ideas, generate_specific_content_pieces, ContentIdea, GeneratedIdeas, GeneratedContentList, extract_video_id as repurpose_extract_video_id, get_video_title
from channelvideos_alt import get_channel_videos
# import yt_dlp # To get video title - Removed as get_video_title_sync is removed

print("DEBUG: main.py top-level print statement executed.")

app = FastAPI(title="YouTube Repurposer API", version="0.1.3") # Incremented version

# Thread pool executor for running synchronous functions
executor = ThreadPoolExecutor(max_workers=10)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models for Request/Response
class TranscribeRequest(BaseModel):
    video_id: str = Field(..., description="The YouTube video ID of the video to transcribe.")

class TranscriptResponse(BaseModel):
    youtube_video_id: str
    title: Optional[str] = None
    transcript: str
    status: Optional[str] = None

class ProcessVideoRequest(BaseModel):
    video_id: str = Field(..., description="The YouTube video ID of the video to process.")
    # force_reprocess: bool = False # Example for future enhancement

class ProcessVideoResponse(BaseModel):
    id: Optional[int] = Field(None, description="The internal database ID of the video.")
    youtube_video_id: str = Field(..., description="The YouTube video ID.")
    title: Optional[str] = Field(None, description="The title of the YouTube video.")
    transcript: Optional[str] = Field(None, description="The transcript of the video.")
    status: Optional[str] = Field(None, description="The processing status of the video.")
    repurposed_text: Optional[str] = Field(None, description="The generated repurposed content ideas and pieces (temporary string format).")

    class Config:
        orm_mode = True

class ChannelRequest(BaseModel):
    channel_id: str # Can be username or channel URL
    max_videos: int = Field(..., ge=1, description="Maximum number of videos to return.")

# Helper function get_video_title_sync removed as it's no longer used.

@app.on_event("startup")
async def on_startup():
    init_db()
    # Initialize other resources if needed

@app.on_event("shutdown")
async def on_shutdown():
    executor.shutdown(wait=True)

@app.get("/test-print/")
async def test_print_endpoint():
    print("DEBUG: /test-print/ endpoint called.")
    return {"message": "Test print endpoint reached. Check console."}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Repurpose API"}

@app.post("/transcribe/", response_model=TranscriptResponse)
async def transcribe_video(
    request: TranscribeRequest,
    db: Session = Depends(get_db)
):
    loop = asyncio.get_event_loop()
    youtube_id_from_request: str = request.video_id
    print(f"DEBUG: /transcribe/ endpoint called with video_id: {youtube_id_from_request}")

    try:
        db_video = db.query(Video).filter(Video.youtube_video_id == youtube_id_from_request).first()
        print(f"DEBUG: DB lookup for {youtube_id_from_request}: {'Found' if db_video else 'Not found'}")

        if db_video:
            print(f"DEBUG: Video {db_video.youtube_video_id} found in DB. Transcript exists: {bool(db_video.transcript)}")
            # Video exists in the database
            if db_video.transcript:
                # Transcript already exists
                response = TranscriptResponse(
                    youtube_video_id=db_video.youtube_video_id,
                    title=db_video.title,
                    transcript=db_video.transcript,
                    status=db_video.status
                )
                print(f"DEBUG: Returning existing transcript for {db_video.youtube_video_id}")
                return response
            else:
                # Video exists, but transcript needs to be generated
                print(f"DEBUG: Attempting to transcribe existing video {db_video.youtube_video_id} as transcript is missing.")
                transcript_text = await loop.run_in_executor(executor, fetch_transcript, db_video.youtube_video_id)
                print(f"DEBUG: Transcript fetched for existing video {db_video.youtube_video_id}: {'Success' if transcript_text else 'Failure'}")
                if transcript_text is None:
                    logging.error(f"Failed to transcribe video ID {db_video.youtube_video_id} (existing record). Raising 500.")
                    raise HTTPException(status_code=500, detail=f"Failed to transcribe video ID {db_video.youtube_video_id} (existing record).")

                db_video.transcript = transcript_text
                db_video.status = "processed"  # Update status
                print(f"DEBUG: Updating DB for {db_video.youtube_video_id} with new transcript.")
                db.commit()
                db.refresh(db_video)
                
                response = TranscriptResponse(
                    youtube_video_id=db_video.youtube_video_id,
                    title=db_video.title,
                    transcript=db_video.transcript,
                    status=db_video.status
                )
                print(f"DEBUG: Returning newly fetched transcript for {db_video.youtube_video_id}")
                return response
        else:
            # Video does not exist, create a new entry
            print(f"DEBUG: Video {youtube_id_from_request} not in DB. Attempting to fetch title.")
            video_title = await loop.run_in_executor(executor, get_video_title, youtube_id_from_request)
            print(f"DEBUG: Title for {youtube_id_from_request}: {video_title}")
            if video_title is None:
                logging.warning(f"Title for {youtube_id_from_request} is None. Raising 404.")
                raise HTTPException(
                    status_code=404,
                    detail=f"Video with ID '{youtube_id_from_request}' not found on YouTube or title could not be retrieved."
                )

            print(f"DEBUG: Attempting to fetch transcript for new video {youtube_id_from_request}.")
            transcript_text = await loop.run_in_executor(executor, fetch_transcript, youtube_id_from_request)
            print(f"DEBUG: Transcript for {youtube_id_from_request}: {'Fetched' if transcript_text else 'Failed to fetch'}")
            if transcript_text is None:
                logging.error(f"Transcript for {youtube_id_from_request} is None. Raising 500.")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to transcribe video ID '{youtube_id_from_request}'. Video found, but transcription unavailable or failed."
                )

            print(f"DEBUG: Creating new Video object for {youtube_id_from_request} with title '{video_title}'.")
            new_video = Video(
                youtube_video_id=youtube_id_from_request,
                title=video_title,
                transcript=transcript_text,
                status="processed"  # Set status for new video
            )
            print(f"DEBUG: Adding new video {youtube_id_from_request} to DB session.")
            db.add(new_video)
            print(f"DEBUG: Committing new video {youtube_id_from_request} to DB.")
            db.commit()
            db.refresh(new_video)

            response = TranscriptResponse(
                youtube_video_id=new_video.youtube_video_id,
                title=new_video.title,
                transcript=new_video.transcript,
                status=new_video.status
            )
            print(f"DEBUG: Returning transcript for newly created video record {new_video.youtube_video_id}")
            return response

    except HTTPException as http_exc:
        logging.error(f"HTTPException in /transcribe/ for {youtube_id_from_request}: {http_exc.status_code} - {http_exc.detail}")
        if db.is_active: db.rollback()
        raise http_exc
    except ValidationError as ve: # For request model validation
        logging.error(f"ValidationError in /transcribe/ for {youtube_id_from_request}: {str(ve)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(ve)}")
    except Exception as e:
        logging.exception(f"Unexpected error in /transcribe/ for {youtube_id_from_request}: {str(e)}") # Changed to logging.exception
        if db.is_active: db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing video ID {youtube_id_from_request}: {str(e)}")

# Removed /repurpose/ endpoint as its functionality is merged into /process-video/

@app.post("/channel/videos/")
async def list_channel_videos(
    request: ChannelRequest, # max_videos is now part of ChannelRequest
    db: Session = Depends(get_db)
):
    loop = asyncio.get_event_loop()
    try:
        # get_channel_videos is synchronous
        videos_data = await loop.run_in_executor(
            executor,
            get_channel_videos,
            request.channel_id,
            request.max_videos # Use max_videos from the request body
        )

        if videos_data is None:
            raise HTTPException(status_code=404, detail="Could not fetch videos for the channel or channel not found.")
        
        # Assuming get_channel_videos respects the max_videos (limit) parameter.
        # No additional slicing needed here.
            
        return videos_data

    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching channel videos for channel {request.channel_id}: {str(e)}")

@app.post("/process-video/", response_model=ProcessVideoResponse)
async def process_video(
    request: ProcessVideoRequest,
    db: Session = Depends(get_db)
):
    loop = asyncio.get_event_loop()
    youtube_id_from_request: str = request.video_id

    try:
        # Step 2: Try to find the Video record in the database by youtube_video_id.
        db_video = db.query(Video).filter(Video.youtube_video_id == youtube_id_from_request).first()

        # Step 3: If the video record is NOT found:
        if not db_video:
            # Step 3a: Call get_video_title()
            video_title = await loop.run_in_executor(executor, get_video_title, youtube_id_from_request)
            if video_title is None:
                logging.warning(f"Title for {youtube_id_from_request} is None. Video not found on YouTube or title retrieval failed.")
                raise HTTPException(
                    status_code=404,
                    detail=f"Video with ID '{youtube_id_from_request}' not found on YouTube or title could not be retrieved."
                )

            # Step 3b: Call fetch_transcript()
            transcript_text = await loop.run_in_executor(executor, fetch_transcript, youtube_id_from_request)
            if transcript_text is None:
                logging.error(f"Failed to transcribe video ID {youtube_id_from_request} (new record). Transcription failed.")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to transcribe video ID '{youtube_id_from_request}'. Transcription failed."
                )

            # Step 3c: Create a new Video object
            db_video = Video(
                youtube_video_id=youtube_id_from_request,
                title=video_title,
                transcript=transcript_text,
                status="transcribed"
            )
            # Step 3d: Save this new Video record to the database.
            db.add(db_video)
            db.commit()
            db.refresh(db_video)
            # Step 3e: db_video variable now references this newly created and saved video record.

        # Step 4: If the video record IS found (or was just created):
        # Step 4a: Check if db_video.transcript is populated.
        if not db_video.transcript:
            # Step 4a.i: Call fetch_transcript().
            transcript_text = await loop.run_in_executor(executor, fetch_transcript, db_video.youtube_video_id)
            if transcript_text is None:
                logging.error(f"Failed to fetch transcript for existing video ID {db_video.youtube_video_id}. Transcription failed.")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch transcript for existing video ID '{db_video.youtube_video_id}'. Transcription failed."
                )
            # Step 4a.ii: Update db_video.transcript and db_video.status. Save to DB.
            db_video.transcript = transcript_text
            db_video.status = "transcribed"
            db.commit()
            db.refresh(db_video)

        # Step 4b: Repurposing Logic
        # Step 4b.i: Check if db_video.repurposed_text is populated.
        if not db_video.repurposed_text: # Assuming empty string or None means not populated
            if not db_video.transcript: # Safeguard, should have transcript by now
                logging.error(f"Transcript unavailable for repurposing for video ID {db_video.youtube_video_id} (DB ID: {db_video.id}).")
                raise HTTPException(status_code=500, detail=f"Transcript unavailable for repurposing for video ID '{db_video.youtube_video_id}'.")

            # Step 4b.ii.1: Call generate_content_ideas()
            ideas_data = await loop.run_in_executor(executor, generate_content_ideas, db_video.transcript)
            if ideas_data is None: # Assuming it can return None on failure
                logging.error(f"Failed to generate content ideas for video ID {db_video.youtube_video_id}.")
                raise HTTPException(status_code=500, detail=f"Failed to generate content ideas for video ID '{db_video.youtube_video_id}'.")

            # Step 4b.ii.2: Call generate_specific_content_pieces()
            # Assuming generate_specific_content_pieces(transcript, ideas_data) signature
            content_pieces_data = await loop.run_in_executor(executor, generate_specific_content_pieces, db_video.transcript, ideas_data)
            if content_pieces_data is None: # Assuming it can return None on failure
                logging.error(f"Failed to generate specific content pieces for video ID {db_video.youtube_video_id}.")
                raise HTTPException(status_code=500, detail=f"Failed to generate specific content pieces for video ID '{db_video.youtube_video_id}'.")
            
            # Step 4b.iii: Store ideas_data and content_pieces_data.
            db_video.repurposed_text = f"Ideas: {ideas_data}\nContent: {content_pieces_data}"
            # Step 4b.iv: Update db_video.status.
            db_video.status = "processed"
            # Step 4b.v: Save changes to the database.
            db.commit()
            db.refresh(db_video)

        # Step 4c: Return the full db_video object
        return db_video # Pydantic will convert using ProcessVideoResponse schema due to orm_mode=True

    except HTTPException as http_exc:
        if db.is_active: db.rollback() # Rollback on known HTTP exceptions
        raise http_exc
    except ValidationError as ve: # For request model validation or response model issues
        logging.error(f"ValidationError in /process-video/ for {youtube_id_from_request}: {str(ve)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(ve)}")
    except Exception as e:
        logging.exception(f"Unexpected error in /process-video/ for {youtube_id_from_request}: {str(e)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing video ID {youtube_id_from_request}: {str(e)}")
