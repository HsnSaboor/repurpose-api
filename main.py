import logging
import json # Added for json.dumps
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
                db_video.status = "transcribed"  # Update status
                print(f"DEBUG: Updating DB for {db_video.youtube_video_id} with new transcript and status 'transcribed'.")
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
                status="transcribed"  # Set status for new video
            )
            print(f"DEBUG: Adding new video {youtube_id_from_request} to DB session with status 'transcribed'.")
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
        if db.is_active and db.in_transaction(): db.rollback()
        raise http_exc
    except ValidationError as ve: # For request model validation
        logging.error(f"ValidationError in /transcribe/ for {youtube_id_from_request}: {str(ve)}")
        if db.is_active and db.in_transaction(): db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(ve)}")
    except Exception as e:
        logging.exception(f"Unexpected error in /transcribe/ for {youtube_id_from_request}: {str(e)}") # Changed to logging.exception
        if db.is_active and db.in_transaction(): db.rollback()
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
                status="transcribed"  # Set status to "transcribed"
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
            db_video.status = "transcribed" # Ensure status is "transcribed"
            db.commit()
            db.refresh(db_video)

        # Step 4b: Repurposing Logic
        # Step 4b.i: Check if db_video.repurposed_text is populated.
        if not db_video.repurposed_text: # Assuming empty string or None means not populated
            if not db_video.transcript: # Safeguard, should have transcript by now
                logging.error(f"Transcript unavailable for repurposing for video ID {db_video.youtube_video_id} (DB ID: {db_video.id}).")
                raise HTTPException(status_code=500, detail=f"Transcript unavailable for repurposing for video ID '{db_video.youtube_video_id}'.")

            # Step 4b.ii.1: Call generate_content_ideas()
            ideas_data_raw = await loop.run_in_executor(executor, generate_content_ideas, db_video.transcript)
            
            # Ensure ideas_data_raw is a list, even if generate_content_ideas returns None (e.g., if transcript was too short)
            if ideas_data_raw is None: 
                logging.warning(f"generate_content_ideas returned None for video ID {db_video.youtube_video_id}. Treating as empty list.")
                ideas_data_raw = [] 

            validated_ideas_list: List[ContentIdea] = []
            if not isinstance(ideas_data_raw, list):
                logging.error(f"Ideas data from generate_content_ideas is not a list for video ID {db_video.youtube_video_id}. Data: {ideas_data_raw}")
                raise HTTPException(status_code=500, detail=f"Invalid structure for content ideas: Expected a list, got {type(ideas_data_raw).__name__}.")

            for idea_dict in ideas_data_raw:
                try:
                    if not isinstance(idea_dict, dict):
                        logging.error(f"Content idea item is not a dictionary for video ID {db_video.youtube_video_id}. Item: {idea_dict}")
                        raise HTTPException(status_code=500, detail="Invalid structure for content idea item: Expected a dictionary.")
                    idea_model = ContentIdea(**idea_dict)
                    validated_ideas_list.append(idea_model)
                except ValidationError as ve:
                    logging.error(f"Validation error for a content idea for video ID {db_video.youtube_video_id}: {ve}. Idea: {idea_dict}")
                    raise HTTPException(status_code=500, detail="Failed to validate content ideas structure.")
            
            # If ideas_data_raw was not empty but validated_ideas_list is, it means all items failed validation.
            if ideas_data_raw and not validated_ideas_list:
                logging.warning(f"No valid content ideas found after validation for video ID {db_video.youtube_video_id}, although raw ideas were present and all failed validation.")
                # This scenario implies all ideas failed validation, which would have raised an HTTPException inside the loop.
                # If the code reaches here, it means either ideas_data_raw was empty or all ideas were successfully validated.
                # So, this specific error condition might not be reachable if ValidationError always raises.
                # However, if an idea_dict was not a dict, and that error was handled differently (e.g. skipped), this could be relevant.
                # Given the current logic, the exception in the loop is the primary guard.
                # For safety, keeping a check, though it might be redundant.
                raise HTTPException(status_code=500, detail=f"All content ideas failed validation for video ID '{db_video.youtube_video_id}'.")

            # Step 4b.ii.2: Call generate_specific_content_pieces()
            # Signature from repurpose.py: generate_specific_content_pieces(ideas: List[ContentIdea], original_transcript: str, video_url: str)
            content_pieces_data = await loop.run_in_executor(
                executor,
                generate_specific_content_pieces,
                validated_ideas_list,  # Pass the list of ContentIdea objects
                db_video.transcript,   # Pass the original transcript
                db_video.youtube_video_id # Pass the video_id as video_url argument
            )

            if content_pieces_data is None: # generate_specific_content_pieces in repurpose.py returns GeneratedContentList, even if empty. So None is an error.
                logging.error(f"Failed to generate specific content pieces for video ID {db_video.youtube_video_id}. Function returned None.")
                raise HTTPException(status_code=500, detail=f"Failed to generate specific content pieces for video ID '{db_video.youtube_video_id}'.")
            
            # Step 4b.iii: Store ideas_data (raw) and content_pieces_data.
            # repurposed_text should be a single JSON string representing an object.
            
            try:
                # Ensure ideas_data_raw (the direct output from generate_content_ideas, defaulted to [] if None) is used.
                # Ensure content_pieces_data (output from generate_specific_content_pieces) is used.
                repurposed_data_for_json = {
                    "ideas": ideas_data_raw,  # This is List[Dict[str, Any]] from generate_content_ideas
                    "content_pieces": content_pieces_data.model_dump() if content_pieces_data else {"pieces": []} # .model_dump() from Pydantic model
                }
                db_video.repurposed_text = json.dumps(repurposed_data_for_json)
            except TypeError as te: # Catch errors during json.dumps if models are complex and not directly serializable
                logging.error(f"Error serializing repurposed content to JSON for {db_video.youtube_video_id}: {te}")
                raise HTTPException(status_code=500, detail="Error storing repurposed content due to serialization issue.")

            # Step 4b.iv: Update db_video.status.
            db_video.status = "processed" # Status becomes "processed" after successful repurposing
            # Step 4b.v: Save changes to the database.
            db.commit()
            db.refresh(db_video)

        # Step 4c: Return the full db_video object
        return db_video # Pydantic will convert using ProcessVideoResponse schema due to orm_mode=True

    except HTTPException as http_exc:
        if db.is_active and db.in_transaction(): db.rollback() 
        raise http_exc
    except ValidationError as ve: # For request model validation or response model issues
        logging.error(f"Pydantic ValidationError in /process-video/ for {youtube_id_from_request}: {str(ve)}")
        if db.is_active and db.in_transaction(): db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(ve)}")
    except Exception as e:
        logging.exception(f"Unexpected error in /process-video/ for {youtube_id_from_request}: {str(e)}")
        if db.is_active and db.in_transaction(): db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing video ID {youtube_id_from_request}: {str(e)}")
