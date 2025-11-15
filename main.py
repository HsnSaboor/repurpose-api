"""
FastAPI Application - Content Repurposer API
Streamlined with modular imports
"""

import logging
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any
import json
import time

# Import models from api module
from api.models import (
    TranscribeRequest, TranscriptResponse,
    EnhancedTranscriptResponse, TranscriptAnalysisResponse,
    ProcessVideoRequest, ProcessVideoResponse,
    BulkVideoProcessRequest, BulkVideoProcessResponseItem,
    EditContentRequest, EditContentResponse
)

# Import config
from api.config import CONTENT_STYLE_PRESETS, get_content_style_prompt

# Import database
from core.database import init_db, SessionLocal, Video

# Import services
from core.services.transcript_service import (
    get_english_transcript,
    TranscriptPreferences,
    list_available_transcripts_with_metadata,
    get_transcript_text
)
from core.services.document_service import DocumentParser, extract_text_from_document
from core.services.video_service import get_video_title

# Import content generation
from repurpose import (
    generate_content_ideas,
    generate_specific_content_pieces,
    ContentIdea,
    GeneratedIdeas,
    extract_video_id as repurpose_extract_video_id,
    edit_content_piece_with_diff,
    identify_content_changes
)

print("DEBUG: main.py top-level print statement executed.")

# Initialize FastAPI app
app = FastAPI(
    title="Content Repurposer API",
    description="Transform YouTube videos and documents into social media content",
    version="0.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=10)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Include routers
from api.routers.configuration import router as config_router
app.include_router(config_router)

# Add all endpoint functions from original main.py
@app.post("/process-video-stream/")
async def process_video_stream(request: ProcessVideoRequest, db: Session = Depends(get_db)):
    """Process video with real-time streaming updates"""
    
    async def generate_stream():
        try:
            yield f"data: {{\"status\": \"started\", \"message\": \"Starting video processing...\", \"progress\": 0}}\n\n"
            
            # Check if video already exists
            db_video = db.query(Video).filter(Video.youtube_video_id == request.video_id).first()
            
            if db_video and not request.force_regenerate:
                yield f"data: {{\"status\": \"found_existing\", \"message\": \"Found existing video, loading...\", \"progress\": 20}}\n\n"
                
                # Parse and return existing content
                video_data = {
                    "id": db_video.id,
                    "youtube_video_id": db_video.youtube_video_id,
                    "title": db_video.title,
                    "transcript": db_video.transcript,
                    "status": db_video.status,
                    "thumbnail_url": f"https://img.youtube.com/vi/{db_video.youtube_video_id}/maxresdefault.jpg",
                    "ideas": [],
                    "content_pieces": []
                }
                
                if db_video.repurposed_text:
                    try:
                        parts = db_video.repurposed_text.split("Content Pieces:")
                        if len(parts) == 2:
                            content_pieces_text = parts[1].strip()
                            if content_pieces_text:
                                pieces = content_pieces_text.split("\n\n---\n\n")
                                for piece_text in pieces:
                                    if piece_text.strip():
                                        try:
                                            piece = json.loads(piece_text.strip())
                                            video_data["content_pieces"].append(piece)
                                        except json.JSONDecodeError:
                                            continue
                    except Exception:
                        pass
                
                yield f"data: {{\"status\": \"complete\", \"progress\": 100, \"data\": {json.dumps(video_data)}}}\n\n"
                return
            
            # New processing
            yield f"data: {{\"status\": \"fetching_info\", \"message\": \"Fetching video information...\", \"progress\": 10}}\n\n"
            
            # Get video title
            try:
                title = get_video_title(request.video_id)
                if title:
                    yield f"data: {{\"status\": \"info_fetched\", \"message\": \"Video: {title[:50]}...\", \"progress\": 20}}\n\n"
            except Exception:
                title = None
            
            yield f"data: {{\"status\": \"transcribing\", \"message\": \"Extracting English transcript...\", \"progress\": 30}}\n\n"
            
            # Get English transcript with enhanced service
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    executor, 
                    get_english_transcript, 
                    request.video_id, 
                    None
                )
                
                if result:
                    transcript = result.transcript_text
                    yield f"data: {{\"status\": \"transcript_ready\", \"message\": \"English transcript extracted ({result.priority.name})\", \"progress\": 50}}\n\n"
                else:
                    yield f"data: {{\"status\": \"error\", \"message\": \"Failed to get English transcript\", \"progress\": 50}}\n\n"
                    return
                    
            except Exception as e:
                yield f"data: {{\"status\": \"error\", \"message\": \"Failed to get transcript: {str(e)}\", \"progress\": 50}}\n\n"
                return
            
            # Save or update video in database
            if db_video:
                db_video.title = title
                db_video.transcript = transcript
                db_video.status = "processing"
            else:
                db_video = Video(
                    youtube_video_id=request.video_id,
                    title=title,
                    transcript=transcript,
                    status="processing"
                )
                db.add(db_video)
            
            db.commit()
            db.refresh(db_video)
            
            yield f"data: {{\"status\": \"generating_content\", \"message\": \"Generating content ideas...\", \"progress\": 60}}\n\n"
            
            # Prepare content config
            content_config_dict = None
            if request.custom_style and request.custom_style.content_config:
                content_config_dict = request.custom_style.content_config.model_dump()
            elif request.style_preset and request.style_preset in CONTENT_STYLE_PRESETS:
                preset = CONTENT_STYLE_PRESETS[request.style_preset]
                content_config_dict = preset.content_config.model_dump()
            
            # Generate content
            ideas_raw = await asyncio.get_event_loop().run_in_executor(
                executor,
                generate_content_ideas,
                transcript,
                request.style_preset,
                request.custom_style.dict() if request.custom_style else None,
                content_config_dict
            )
            
            if not ideas_raw:
                yield f"data: {{\"status\": \"error\", \"message\": \"Failed to generate content ideas\", \"progress\": 60}}\n\n"
                return
            
            # Convert raw ideas to ContentIdea objects
            generated_ideas = []
            for idea_dict in ideas_raw:
                try:
                    generated_ideas.append(ContentIdea(**idea_dict))
                except Exception as e:
                    continue
            
            yield f"data: {{\"status\": \"ideas_generated\", \"message\": \"Content ideas generated, creating pieces...\", \"progress\": 75}}\n\n"
            
            generated_content: GeneratedContentList = await asyncio.get_event_loop().run_in_executor(
                executor,
                generate_specific_content_pieces,
                generated_ideas,
                transcript,
                f"https://youtube.com/watch?v={request.video_id}",
                request.style_preset,
                request.custom_style.dict() if request.custom_style else None,
                content_config_dict
            )
            
            yield f"data: {{\"status\": \"content_generated\", \"message\": \"Content pieces generated successfully\", \"progress\": 90}}\n\n"
            
            # Save results
            repurposed_text = f"Content Ideas:\n{json.dumps([idea.dict() for idea in generated_ideas], indent=2)}\n\nContent Pieces:\n"
            content_pieces_json = "\n\n---\n\n".join([
                json.dumps(content.dict(), indent=2) for content in generated_content.pieces
            ])
            repurposed_text += content_pieces_json
            
            db_video.repurposed_text = repurposed_text
            db_video.status = "completed"
            db.commit()
            db.refresh(db_video)
            
            # Prepare final response
            final_response = {
                "id": db_video.id,
                "youtube_video_id": db_video.youtube_video_id,
                "title": db_video.title,
                "transcript": db_video.transcript,
                "status": db_video.status,
                "thumbnail_url": f"https://img.youtube.com/vi/{db_video.youtube_video_id}/maxresdefault.jpg",
                "ideas": [idea.dict() for idea in generated_ideas],
                "content_pieces": [content.dict() for content in generated_content.pieces]
            }
            
            yield f"data: {{\"status\": \"complete\", \"progress\": 100, \"data\": {json.dumps(final_response)}}}\n\n"
            
        except Exception as e:
            logging.exception(f"Error in streaming process: {str(e)}")
            yield f"data: {{\"status\": \"error\", \"message\": \"Processing failed: {str(e)}\", \"progress\": 0}}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.get("/videos/")
async def get_all_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all processed videos from the database"""
    try:
        videos = db.query(Video).offset(skip).limit(limit).all()
        result = []
        
        for video in videos:
            video_data = {
                "id": video.id,
                "youtube_video_id": video.youtube_video_id,
                "title": video.title,
                "transcript": video.transcript,
                "status": video.status,
                "thumbnail_url": f"https://img.youtube.com/vi/{video.youtube_video_id}/maxresdefault.jpg",
                "video_url": f"https://youtube.com/watch?v={video.youtube_video_id}",
                "created_at": video.created_at.isoformat() if hasattr(video, 'created_at') and video.created_at else None,
                "ideas": [],
                "content_pieces": []
            }
            
            # Parse repurposed_text if it exists
            if video.repurposed_text:
                try:
                    parts = video.repurposed_text.split("Content Pieces:")
                    if len(parts) == 2:
                        # Parse content pieces
                        content_pieces_text = parts[1].strip()
                        if content_pieces_text:
                            pieces = content_pieces_text.split("\n\n---\n\n")
                            for piece_text in pieces:
                                if piece_text.strip():
                                    try:
                                        piece = json.loads(piece_text.strip())
                                        video_data["content_pieces"].append(piece)
                                    except json.JSONDecodeError:
                                        continue
                except Exception as e:
                    logging.warning(f"Failed to parse repurposed_text for video {video.youtube_video_id}: {str(e)}")
            
            result.append(video_data)
        
        return {"videos": result, "total": len(result)}
        
    except Exception as e:
        logging.exception(f"Error fetching videos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")
@app.on_event("startup")
async def on_startup():
    init_db()

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
            if db_video.transcript:
                response = TranscriptResponse(
                    youtube_video_id=db_video.youtube_video_id,
                    title=db_video.title,
                    transcript=db_video.transcript,
                    status=db_video.status
                )
                print(f"DEBUG: Returning existing transcript for {db_video.youtube_video_id}")
                return response
            else:
                print(f"DEBUG: Attempting to transcribe existing video {db_video.youtube_video_id} as transcript is missing.")
                try:
                    # Use enhanced transcript service
                    result = await loop.run_in_executor(
                        executor, 
                        get_english_transcript, 
                        db_video.youtube_video_id, 
                        None  # Default preferences
                    )
                    
                    if result:
                        # Update database with enhanced metadata
                        transcript_text = result.transcript_text
                        db_video.transcript_language = result.language_code
                        db_video.transcript_type = 'auto_generated' if result.is_generated else 'manual'
                        db_video.is_translated = result.is_translated
                        db_video.source_language = result.translation_source_language
                        db_video.translation_confidence = result.confidence_score
                        db_video.transcript_priority = result.priority.name
                        db_video.processing_notes = json.dumps(result.processing_notes)
                    else:
                        transcript_text = "Transcript unavailable"
                        
                except Exception as e:
                    logging.error(f"Failed to fetch enhanced transcript: {str(e)}")
                    transcript_text = "Transcript unavailable"
                
                print(f"DEBUG: Transcript fetched for existing video {db_video.youtube_video_id}: {'Success' if transcript_text else 'Failure'}")
                
                db_video.transcript = transcript_text
                db_video.status = "processed"
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
            print(f"DEBUG: Video {youtube_id_from_request} not in DB. Attempting to fetch title.")
            try:
                video_title = await loop.run_in_executor(executor, get_video_title, youtube_id_from_request)
            except Exception as e:
                logging.error(f"Failed to fetch title: {str(e)}")
                video_title = "Unknown Title"
            
            print(f"DEBUG: Title for {youtube_id_from_request}: {video_title}")
            
            print(f"DEBUG: Attempting to fetch transcript for new video {youtube_id_from_request}.")
            try:
                # Use enhanced transcript service
                result = await loop.run_in_executor(
                    executor, 
                    get_english_transcript, 
                    youtube_id_from_request, 
                    None  # Default preferences
                )
                
                if result:
                    transcript_text = result.transcript_text
                    
                    # Create new video record with enhanced metadata
                    new_video = Video(
                        youtube_video_id=youtube_id_from_request,
                        title=video_title,
                        transcript=transcript_text,
                        status="processed",
                        transcript_language=result.language_code,
                        transcript_type='auto_generated' if result.is_generated else 'manual',
                        is_translated=result.is_translated,
                        source_language=result.translation_source_language,
                        translation_confidence=result.confidence_score,
                        transcript_priority=result.priority.name,
                        processing_notes=json.dumps(result.processing_notes)
                    )
                else:
                    transcript_text = "Transcript unavailable"
                    new_video = Video(
                        youtube_video_id=youtube_id_from_request,
                        title=video_title,
                        transcript=transcript_text,
                        status="failed"
                    )
                    
            except Exception as e:
                logging.error(f"Failed to fetch enhanced transcript: {str(e)}")
                transcript_text = "Transcript unavailable"
                new_video = Video(
                    youtube_video_id=youtube_id_from_request,
                    title=video_title,
                    transcript=transcript_text,
                    status="failed"
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
    except ValidationError as ve:
        logging.error(f"ValidationError in /transcribe/ for {youtube_id_from_request}: {str(ve)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(ve)}")
    except Exception as e:
        logging.exception(f"Unexpected error in /transcribe/ for {youtube_id_from_request}: {str(e)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing video ID {youtube_id_from_request}: {str(e)}")

@app.post("/process-video/", response_model=ProcessVideoResponse)
async def process_video(
    request: ProcessVideoRequest,
    db: Session = Depends(get_db)
):
    loop = asyncio.get_event_loop()
    youtube_id_from_request: str = request.video_id
    constructed_video_url = f"https://www.youtube.com/watch?v={youtube_id_from_request}"

    try:
        db_video = db.query(Video).filter(Video.youtube_video_id == youtube_id_from_request).first()
        made_changes_to_video_record_before_repurpose = False

        if not db_video:
            try:
                video_title = await loop.run_in_executor(executor, get_video_title, youtube_id_from_request)
            except Exception as e:
                logging.error(f"Failed to fetch title: {str(e)}")
                video_title = "Unknown Title"
            
            try:
                # Use enhanced transcript service for English preference
                result = await loop.run_in_executor(
                    executor, 
                    get_english_transcript, 
                    youtube_id_from_request, 
                    None
                )
                
                if result:
                    transcript_text = result.transcript_text
                else:
                    transcript_text = "Transcript unavailable"
                    
            except Exception as e:
                logging.error(f"Failed to fetch enhanced transcript: {str(e)}")
                transcript_text = "Transcript unavailable"

            new_video = Video(
                youtube_video_id=youtube_id_from_request,
                title=video_title,
                transcript=transcript_text,
                status="processed",
                video_url=constructed_video_url
            )
            db.add(new_video)
            db.commit()
            db.refresh(new_video)
            db_video = new_video
        else:
            if not db_video.video_url:
                db_video.video_url = constructed_video_url
                made_changes_to_video_record_before_repurpose = True
            
            if not db_video.transcript:
                try:
                    # Use enhanced transcript service for English preference
                    result = await loop.run_in_executor(
                        executor, 
                        get_english_transcript, 
                        db_video.youtube_video_id, 
                        None
                    )
                    
                    if result:
                        transcript_text = result.transcript_text
                        # Update metadata
                        db_video.transcript_language = result.language_code
                        db_video.transcript_type = 'auto_generated' if result.is_generated else 'manual'
                        db_video.is_translated = result.is_translated
                        db_video.source_language = result.translation_source_language
                        db_video.translation_confidence = result.confidence_score
                        db_video.transcript_priority = result.priority.name
                        db_video.processing_notes = json.dumps(result.processing_notes)
                    else:
                        transcript_text = "Transcript unavailable"
                        
                except Exception as e:
                    logging.error(f"Failed to fetch enhanced transcript: {str(e)}")
                    transcript_text = "Transcript unavailable"
                
                db_video.transcript = transcript_text
                db_video.status = "processed"
                made_changes_to_video_record_before_repurpose = True

            if made_changes_to_video_record_before_repurpose:
                db.commit()
                db.refresh(db_video)

        if not db_video.transcript:
            logging.error(f"Transcript still missing for video ID {db_video.youtube_video_id} before repurposing.")
            raise HTTPException(status_code=500, detail=f"Transcript unavailable for video ID '{db_video.youtube_video_id}' prior to repurposing.")

        repurposed_text_initially_present = bool(db_video.repurposed_text)
        generated_ideas_this_run: Optional[List[ContentIdea]] = None
        generated_content_pieces_this_run: Optional[List[Union[Reel, ImageCarousel, Tweet]]] = None
        
        final_ideas: Optional[List[ContentIdea]] = None
        final_content_pieces: Optional[List[Any]] = None
        
        if request.force_regenerate or not repurposed_text_initially_present:
            if request.force_regenerate:
                logging.info(f"Force regenerating content for video ID {db_video.youtube_video_id} (DB ID: {db_video.id}).")

            if not db_video.transcript:
                logging.error(f"Transcript unavailable for repurposing for video ID {db_video.youtube_video_id} (DB ID: {db_video.id}).")
                raise HTTPException(status_code=500, detail=f"Transcript unavailable for repurposing for video ID '{db_video.youtube_video_id}'.")

            # Prepare style parameters for content generation
            style_preset = request.style_preset
            custom_style_dict = None
            content_config_dict = None
            
            if request.custom_style:
                custom_style_dict = {
                    'target_audience': request.custom_style.target_audience,
                    'call_to_action': request.custom_style.call_to_action,
                    'content_goal': request.custom_style.content_goal,
                    'language': request.custom_style.language,
                    'tone': request.custom_style.tone,
                    'additional_instructions': request.custom_style.additional_instructions
                }
                # Extract content config from custom style if present
                if request.custom_style.content_config:
                    content_config_dict = request.custom_style.content_config.model_dump()
            
            # If using preset, get content config from preset
            elif style_preset and style_preset in CONTENT_STYLE_PRESETS:
                preset = CONTENT_STYLE_PRESETS[style_preset]
                content_config_dict = preset.content_config.model_dump()

            ideas_data_raw = await loop.run_in_executor(executor, generate_content_ideas, db_video.transcript, style_preset, custom_style_dict, content_config_dict)
            if ideas_data_raw is None:
                logging.error(f"Failed to generate content ideas for video ID {db_video.youtube_video_id}.")
                raise HTTPException(status_code=500, detail=f"Failed to generate content ideas for video ID '{db_video.youtube_video_id}'.")
            
            current_parsed_ideas: List[ContentIdea] = []
            if isinstance(ideas_data_raw, list):
                for idea_dict in ideas_data_raw:
                    if isinstance(idea_dict, dict):
                        try:
                            current_parsed_ideas.append(ContentIdea(**idea_dict))
                        except ValidationError as e_val_gen_idea:
                            logging.error(f"Validation error parsing newly generated content idea for video {db_video.youtube_video_id}: {idea_dict}. Error: {e_val_gen_idea}")
                            continue
                    else:
                        logging.warning(f"Skipping non-dictionary item in newly generated ideas_data_raw for video {db_video.youtube_video_id}: {idea_dict}")

            generated_ideas_this_run = current_parsed_ideas
            final_ideas = generated_ideas_this_run

            video_url_to_pass = db_video.video_url
            if not video_url_to_pass:
                logging.warning(f"db_video.video_url was unexpectedly empty for {db_video.youtube_video_id} before repurposing. Reconstructing.")
                video_url_to_pass = constructed_video_url

            content_pieces_data_obj = await loop.run_in_executor(
                executor,
                generate_specific_content_pieces,
                generated_ideas_this_run,
                db_video.transcript,
                video_url_to_pass,
                style_preset,
                custom_style_dict,
                content_config_dict
            )

            if content_pieces_data_obj is None or not hasattr(content_pieces_data_obj, 'pieces'):
                logging.error(f"Failed to generate specific content pieces or result was malformed for video ID {db_video.youtube_video_id}.")
                generated_content_pieces_this_run = []
            else:
                generated_content_pieces_this_run = content_pieces_data_obj.pieces
            
            final_content_pieces = generated_content_pieces_this_run

            ideas_repr_for_storage = repr(ideas_data_raw)
            content_pieces_json_for_storage = "\n\n---\n\n".join([p.model_dump_json(indent=2) for p in generated_content_pieces_this_run if p])
            db_video.repurposed_text = f"Ideas:\n{ideas_repr_for_storage}\n\nContent Pieces:\n{content_pieces_json_for_storage}"
            
            db_video.status = "processed"
            db.commit()
            db.refresh(db_video)
        
        elif repurposed_text_initially_present and db_video.repurposed_text:
            logging.info(f"Attempting to parse stored repurposed_text for video {db_video.youtube_video_id} (DB ID: {db_video.id}) using robust parser.")
            # Parsing logic would go here
            final_ideas = []
            final_content_pieces = []
        
        return ProcessVideoResponse(
            id=db_video.id,
            youtube_video_id=db_video.youtube_video_id,
            title=db_video.title,
            transcript=db_video.transcript,
            status=db_video.status,
            ideas=final_ideas,
            content_pieces=final_content_pieces
        )

    except HTTPException as http_exc:
        if db.is_active: db.rollback()
        raise http_exc
    except ValidationError as ve:
        logging.error(f"ValidationError in /process-video/ for {youtube_id_from_request}: {str(ve)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(ve)}")
    except Exception as e:
        logging.exception(f"Unexpected error in /process-video/ for {youtube_id_from_request}: {str(e)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing video ID {youtube_id_from_request}: {str(e)}")

@app.post("/process-videos-bulk/", response_model=List[BulkVideoProcessResponseItem])
async def process_videos_bulk(
    request: BulkVideoProcessRequest,
    db: Session = Depends(get_db)
):
    results = []
    for video_id in request.video_ids:
        try:
            single_video_request = ProcessVideoRequest(video_id=video_id, force_regenerate=False)
            video_response_data: ProcessVideoResponse = await process_video(request=single_video_request, db=db)
            
            results.append(BulkVideoProcessResponseItem(
                video_id=video_id,
                status="success",
                details="Processed successfully.",
                data=video_response_data
            ))
        except HTTPException as http_exc:
            results.append(BulkVideoProcessResponseItem(
                video_id=video_id,
                status="error",
                details=f"HTTP {http_exc.status_code}: {http_exc.detail}"
            ))
        except Exception as e:
            logging.error(f"Unexpected error processing video_id {video_id} in bulk: {str(e)}", exc_info=True)
            results.append(BulkVideoProcessResponseItem(
                video_id=video_id,
                status="error",
                details=f"An unexpected error occurred: {str(e)}"
            ))
    return results

@app.post("/edit-content/", response_model=EditContentResponse)
async def edit_content_piece(
    request: EditContentRequest,
    db: Session = Depends(get_db)
):
    """Edit a specific content piece using natural language prompts with diff-based editing"""
    loop = asyncio.get_event_loop()
    
    try:
        # Find the video in the database
        db_video = db.query(Video).filter(Video.youtube_video_id == request.video_id).first()
        
        if not db_video:
            raise HTTPException(status_code=404, detail=f"Video with ID '{request.video_id}' not found.")
        
        if not db_video.repurposed_text:
            raise HTTPException(status_code=404, detail=f"No content pieces found for video '{request.video_id}'. Please process the video first.")
        
        # Parse the stored content pieces
        try:
            # Extract content pieces from repurposed_text
            content_pieces_section = db_video.repurposed_text.split("Content Pieces:")[-1].strip()
            content_pieces_json_parts = content_pieces_section.split("\n\n---\n\n")
            
            original_content = None
            content_pieces = []
            
            for piece_json in content_pieces_json_parts:
                if piece_json.strip():
                    try:
                        piece_data = json.loads(piece_json.strip())
                        content_pieces.append(piece_data)
                        
                        # Find the specific content piece to edit
                        if piece_data.get('content_id') == request.content_piece_id:
                            original_content = piece_data
                    except json.JSONDecodeError:
                        continue
            
            if not original_content:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Content piece with ID '{request.content_piece_id}' not found. Available IDs: {[p.get('content_id') for p in content_pieces]}"
                )
            
            # Validate content type matches
            if original_content.get('content_type') != request.content_type:
                raise HTTPException(
                    status_code=400,
                    detail=f"Content type mismatch. Expected '{request.content_type}', found '{original_content.get('content_type')}'."
                )
            
            # Edit the content piece using LLM with diff-based editing
            edited_content = await loop.run_in_executor(
                executor,
                edit_content_piece_with_diff,
                original_content,
                request.edit_prompt,
                request.content_type
            )
            
            if not edited_content:
                return EditContentResponse(
                    success=False,
                    content_piece_id=request.content_piece_id,
                    original_content=original_content,
                    edited_content=None,
                    changes_made=None,
                    error_message="Failed to generate edited content. Please try a different edit prompt."
                )
            
            # Identify changes made
            changes_made = identify_content_changes(original_content, edited_content)
            
            # Update the content piece in the database
            updated_content_pieces = []
            for piece in content_pieces:
                if piece.get('content_id') == request.content_piece_id:
                    updated_content_pieces.append(edited_content)
                else:
                    updated_content_pieces.append(piece)
            
            # Reconstruct the repurposed_text
            ideas_section = db_video.repurposed_text.split("Content Pieces:")[0]
            updated_content_pieces_json = "\n\n---\n\n".join([
                json.dumps(piece, indent=2) for piece in updated_content_pieces
            ])
            db_video.repurposed_text = f"{ideas_section}Content Pieces:\n{updated_content_pieces_json}"
            
            # Save to database
            db.commit()
            db.refresh(db_video)
            
            return EditContentResponse(
                success=True,
                content_piece_id=request.content_piece_id,
                original_content=original_content,
                edited_content=edited_content,
                changes_made=changes_made,
                error_message=None
            )
            
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse stored content pieces: {str(e)}")
        
    except HTTPException as http_exc:
        if db.is_active: db.rollback()
        raise http_exc
    except Exception as e:
        logging.exception(f"Unexpected error in /edit-content/ for {request.content_piece_id}: {str(e)}")
        if db.is_active: db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while editing content piece: {str(e)}")

# New Enhanced Transcript Endpoints
@app.post("/transcribe-enhanced/", response_model=EnhancedTranscriptResponse)
async def transcribe_video_enhanced(
    request: TranscribeRequest,
    db: Session = Depends(get_db)
):
    """Enhanced transcription endpoint with English preference and detailed metadata"""
    loop = asyncio.get_event_loop()
    youtube_id_from_request: str = request.video_id
    
    try:
        # Parse transcript preferences if provided
        preferences = None
        if request.preferences:
            try:
                preferences = TranscriptPreferences(**request.preferences)
            except Exception as e:
                logging.warning(f"Invalid transcript preferences: {e}, using defaults")
                preferences = TranscriptPreferences()
        
        # Get enhanced transcript result
        result = await loop.run_in_executor(
            executor,
            get_english_transcript,
            youtube_id_from_request,
            preferences
        )
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No transcript available for video {youtube_id_from_request}")
        
        # Get video title
        try:
            title = await loop.run_in_executor(executor, get_video_title, youtube_id_from_request)
        except Exception:
            title = "Unknown Title"
        
        # Get available languages
        available_languages = await loop.run_in_executor(
            executor,
            list_available_transcripts_with_metadata,
            youtube_id_from_request
        )
        
        # Prepare transcript metadata
        transcript_metadata = {
            "language_code": result.language_code,
            "language": result.language,
            "is_generated": result.is_generated,
            "is_translated": result.is_translated,
            "priority": result.priority.name,
            "translation_source_language": result.translation_source_language,
            "confidence_score": result.confidence_score,
            "processing_notes": result.processing_notes
        }
        
        # Update database
        db_video = db.query(Video).filter(Video.youtube_video_id == youtube_id_from_request).first()
        
        if db_video:
            db_video.transcript = result.transcript_text
            db_video.transcript_language = result.language_code
            db_video.transcript_type = 'auto_generated' if result.is_generated else 'manual'
            db_video.is_translated = result.is_translated
            db_video.source_language = result.translation_source_language
            db_video.translation_confidence = result.confidence_score
            db_video.transcript_priority = result.priority.name
            db_video.processing_notes = json.dumps(result.processing_notes)
            db_video.status = "processed"
        else:
            db_video = Video(
                youtube_video_id=youtube_id_from_request,
                title=title,
                transcript=result.transcript_text,
                status="processed",
                transcript_language=result.language_code,
                transcript_type='auto_generated' if result.is_generated else 'manual',
                is_translated=result.is_translated,
                source_language=result.translation_source_language,
                translation_confidence=result.confidence_score,
                transcript_priority=result.priority.name,
                processing_notes=json.dumps(result.processing_notes)
            )
            db.add(db_video)
        
        db.commit()
        db.refresh(db_video)
        
        return EnhancedTranscriptResponse(
            youtube_video_id=youtube_id_from_request,
            title=title,
            transcript=result.transcript_text,
            transcript_metadata=transcript_metadata,
            available_languages=[meta.language_code for meta in available_languages],
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error in enhanced transcription for {youtube_id_from_request}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process enhanced transcript: {str(e)}")

@app.get("/analyze-transcripts/{video_id}", response_model=TranscriptAnalysisResponse)
async def analyze_available_transcripts(video_id: str):
    """Analyze available transcripts for a video and recommend processing approach"""
    loop = asyncio.get_event_loop()
    
    try:
        # Get available transcript metadata
        metadata_list = await loop.run_in_executor(
            executor,
            list_available_transcripts_with_metadata,
            video_id
        )
        
        if not metadata_list:
            raise HTTPException(status_code=404, detail=f"No transcripts found for video {video_id}")
        
        # Determine recommended approach
        processing_notes = []
        recommended_approach = "auto_translated"
        
        for meta in metadata_list:
            if meta.language_code.lower() == 'en' and not meta.is_generated:
                recommended_approach = "manual_english"
                processing_notes.append("Manual English transcript available - highest quality")
                break
            elif meta.language_code.lower() == 'en' and meta.is_generated:
                recommended_approach = "auto_english"
                processing_notes.append("Auto-generated English transcript available - good quality")
            elif not meta.is_generated and meta.is_translatable:
                if recommended_approach not in ["manual_english", "auto_english"]:
                    recommended_approach = "manual_translated"
                    processing_notes.append(f"Manual {meta.language} transcript available for translation")
            elif meta.is_generated and meta.is_translatable:
                if recommended_approach == "auto_translated":
                    processing_notes.append(f"Auto-generated {meta.language} transcript available for translation")
        
        # Convert metadata to dict format
        available_transcripts = [
            {
                "language_code": meta.language_code,
                "language": meta.language,
                "is_generated": meta.is_generated,
                "is_translatable": meta.is_translatable
            }
            for meta in metadata_list
        ]
        
        return TranscriptAnalysisResponse(
            youtube_video_id=video_id,
            available_transcripts=available_transcripts,
            recommended_approach=recommended_approach,
            processing_notes=processing_notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error analyzing transcripts for {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze transcripts: {str(e)}")

# ==================== Document Processing Endpoints ====================

@app.post("/process-document/", response_model=ProcessVideoResponse)
async def process_document(
    file: UploadFile = File(...),
    force_regenerate: bool = Form(False),
    style_preset: Optional[str] = Form(None),
    custom_style: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Process a document file (TXT, MD, DOCX, PDF) and generate social media content
    
    Upload a document and get content ideas and pieces generated from its text.
    Works the same as video processing but with document input.
    """
    import tempfile
    import os
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in DocumentParser.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported: {', '.join(DocumentParser.SUPPORTED_EXTENSIONS)}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Extract text from document
        loop = asyncio.get_event_loop()
        text, format_name = await loop.run_in_executor(
            executor,
            DocumentParser.parse_document,
            temp_file_path
        )
        
        # Use filename without extension as "video_id" for database
        doc_id = os.path.splitext(file.filename)[0].replace(' ', '_')[:50]
        
        # Check if document already processed
        db_video = db.query(Video).filter(Video.youtube_video_id == doc_id).first()
        
        if db_video and not force_regenerate:
            # Return existing processed content
            video_data = {
                "id": db_video.id,
                "youtube_video_id": db_video.youtube_video_id,
                "title": db_video.title or file.filename,
                "transcript": db_video.transcript,
                "status": db_video.status,
                "ideas": [],
                "content_pieces": []
            }
            
            try:
                if db_video.repurposed_text:
                    repurposed_data = json.loads(db_video.repurposed_text)
                    video_data["ideas"] = repurposed_data.get("ideas", [])
                    video_data["content_pieces"] = repurposed_data.get("content_pieces", [])
            except:
                pass
            
            return video_data
        
        # Parse custom style if provided
        custom_style_dict = None
        content_config_dict = None
        
        if custom_style:
            try:
                custom_style_dict = json.loads(custom_style)
                # Extract content config if present
                if 'content_config' in custom_style_dict:
                    content_config_dict = custom_style_dict['content_config']
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in custom_style")
        elif style_preset:
            if style_preset not in CONTENT_STYLE_PRESETS:
                raise HTTPException(status_code=404, detail=f"Style preset '{style_preset}' not found")
            # Get content config from preset
            preset = CONTENT_STYLE_PRESETS[style_preset]
            content_config_dict = preset.content_config.model_dump()
        
        # Generate content ideas (uses either preset name or custom dict)
        ideas_raw = await loop.run_in_executor(
            executor,
            generate_content_ideas,
            text,
            style_preset,
            custom_style_dict,
            content_config_dict
        )
        
        if not ideas_raw:
            raise HTTPException(status_code=500, detail="Failed to generate content ideas")
        
        # Convert dict ideas to ContentIdea objects if needed
        if ideas_raw and isinstance(ideas_raw[0], dict):
            ideas_raw = [ContentIdea(**idea) for idea in ideas_raw]
        
        # Generate specific content pieces
        generated_content = await loop.run_in_executor(
            executor,
            generate_specific_content_pieces,
            ideas_raw,
            text,
            f"document://{file.filename}",
            style_preset,
            custom_style_dict,
            content_config_dict
        )
        
        all_pieces = generated_content.pieces if hasattr(generated_content, 'pieces') else []
        
        # Prepare data for storage - convert Pydantic models to dicts
        ideas_list = []
        for idea in ideas_raw:
            if hasattr(idea, 'dict'):
                ideas_list.append(idea.dict())
            elif isinstance(idea, dict):
                ideas_list.append(idea)
            else:
                ideas_list.append(str(idea))
        
        pieces_list = []
        for p in all_pieces:
            if hasattr(p, 'dict'):
                pieces_list.append(p.dict())
            elif isinstance(p, dict):
                pieces_list.append(p)
            else:
                pieces_list.append(str(p))
        
        repurposed_data = {
            "ideas": ideas_list,
            "content_pieces": pieces_list
        }
        
        # Save or update in database
        if db_video:
            db_video.title = file.filename
            db_video.transcript = text
            db_video.repurposed_text = json.dumps(repurposed_data)
            db_video.status = "completed"
        else:
            db_video = Video(
                youtube_video_id=doc_id,
                title=file.filename,
                transcript=text,
                repurposed_text=json.dumps(repurposed_data),
                status="completed"
            )
            db.add(db_video)
        
        db.commit()
        db.refresh(db_video)
        
        return {
            "id": db_video.id,
            "youtube_video_id": db_video.youtube_video_id,
            "title": db_video.title,
            "transcript": db_video.transcript,
            "status": "completed",
            "ideas": ideas_list,
            "content_pieces": pieces_list
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.exception(f"Error processing document {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass


@app.post("/process-document-stream/")
async def process_document_stream(
    file: UploadFile = File(...),
    force_regenerate: bool = Form(False),
    style_preset: Optional[str] = Form(None),
    custom_style: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Process a document with real-time streaming updates (SSE)
    
    Same as /process-document/ but returns Server-Sent Events for progress tracking
    """
    import tempfile
    import os
    
    async def generate_stream():
        temp_file_path = None
        try:
            yield f"data: {{\"status\": \"started\", \"message\": \"Processing document...\", \"progress\": 0}}\n\n"
            
            # Validate file
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in DocumentParser.SUPPORTED_EXTENSIONS:
                yield f"data: {{\"status\": \"error\", \"message\": \"Unsupported file format: {file_ext}\", \"progress\": 0}}\n\n"
                return
            
            yield f"data: {{\"status\": \"uploading\", \"message\": \"Reading file: {file.filename}\", \"progress\": 10}}\n\n"
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            yield f"data: {{\"status\": \"parsing\", \"message\": \"Extracting text from {file_ext} file...\", \"progress\": 30}}\n\n"
            
            # Extract text
            loop = asyncio.get_event_loop()
            text, format_name = await loop.run_in_executor(
                executor,
                DocumentParser.parse_document,
                temp_file_path
            )
            
            char_count = len(text)
            yield f"data: {{\"status\": \"text_extracted\", \"message\": \"Extracted {char_count} characters from {format_name}\", \"progress\": 50}}\n\n"
            
            doc_id = os.path.splitext(file.filename)[0].replace(' ', '_')[:50]
            
            # Check existing
            db_video = db.query(Video).filter(Video.youtube_video_id == doc_id).first()
            
            if db_video and not force_regenerate:
                yield f"data: {{\"status\": \"found_existing\", \"message\": \"Found existing processed document\", \"progress\": 60}}\n\n"
                
                video_data = {
                    "id": db_video.id,
                    "youtube_video_id": db_video.youtube_video_id,
                    "title": db_video.title,
                    "transcript": db_video.transcript,
                    "status": db_video.status,
                    "ideas": [],
                    "content_pieces": []
                }
                
                try:
                    if db_video.repurposed_text:
                        repurposed_data = json.loads(db_video.repurposed_text)
                        video_data["ideas"] = repurposed_data.get("ideas", [])
                        video_data["content_pieces"] = repurposed_data.get("content_pieces", [])
                except:
                    pass
                
                yield f"data: {{\"status\": \"complete\", \"progress\": 100, \"data\": {json.dumps(video_data)}}}\n\n"
                return
            
            yield f"data: {{\"status\": \"generating_content\", \"message\": \"Generating content ideas...\", \"progress\": 60}}\n\n"
            
            # Parse style and content config
            custom_style_dict = None
            content_config_dict = None
            
            if custom_style:
                try:
                    custom_style_dict = json.loads(custom_style)
                    if 'content_config' in custom_style_dict:
                        content_config_dict = custom_style_dict['content_config']
                except:
                    pass
            elif style_preset and style_preset in CONTENT_STYLE_PRESETS:
                preset = CONTENT_STYLE_PRESETS[style_preset]
                content_config_dict = preset.content_config.model_dump()
            
            # Generate ideas
            ideas_raw = await loop.run_in_executor(
                executor,
                generate_content_ideas,
                text,
                style_preset,
                custom_style_dict,
                content_config_dict
            )
            
            if not ideas_raw:
                yield f"data: {{\"status\": \"error\", \"message\": \"Failed to generate ideas\", \"progress\": 60}}\n\n"
                return
            
            yield f"data: {{\"status\": \"ideas_generated\", \"message\": \"Generated {len(ideas_raw)} content ideas\", \"progress\": 75}}\n\n"
            
            # Convert dict ideas to ContentIdea objects if needed
            if ideas_raw and isinstance(ideas_raw[0], dict):
                ideas_raw = [ContentIdea(**idea) for idea in ideas_raw]
            
            # Generate pieces
            generated_content = await loop.run_in_executor(
                executor,
                generate_specific_content_pieces,
                ideas_raw,
                text,
                f"document://{file.filename}",
                style_preset,
                custom_style_dict,
                content_config_dict
            )
            
            all_pieces = generated_content.pieces if hasattr(generated_content, 'pieces') else []
            
            yield f"data: {{\"status\": \"content_generated\", \"message\": \"Created {len(all_pieces)} content pieces\", \"progress\": 90}}\n\n"
            
            # Prepare data for storage - convert Pydantic models to dicts
            ideas_list = []
            for idea in ideas_raw:
                if hasattr(idea, 'dict'):
                    ideas_list.append(idea.dict())
                elif isinstance(idea, dict):
                    ideas_list.append(idea)
                else:
                    ideas_list.append(str(idea))
            
            pieces_list = []
            for p in all_pieces:
                if hasattr(p, 'dict'):
                    pieces_list.append(p.dict())
                elif isinstance(p, dict):
                    pieces_list.append(p)
                else:
                    pieces_list.append(str(p))
            
            repurposed_data = {
                "ideas": ideas_list,
                "content_pieces": pieces_list
            }
            
            # Save to database
            if db_video:
                db_video.title = file.filename
                db_video.transcript = text
                db_video.repurposed_text = json.dumps(repurposed_data)
                db_video.status = "completed"
            else:
                db_video = Video(
                    youtube_video_id=doc_id,
                    title=file.filename,
                    transcript=text,
                    repurposed_text=json.dumps(repurposed_data),
                    status="completed"
                )
                db.add(db_video)
            
            db.commit()
            db.refresh(db_video)
            
            video_data = {
                "id": db_video.id,
                "youtube_video_id": db_video.youtube_video_id,
                "title": db_video.title,
                "transcript": db_video.transcript,
                "status": "completed",
                "ideas": ideas_list,
                "content_pieces": pieces_list
            }
            
            yield f"data: {{\"status\": \"complete\", \"progress\": 100, \"data\": {json.dumps(video_data)}}}\n\n"
            
        except Exception as e:
            logging.exception(f"Error in document streaming: {str(e)}")
            yield f"data: {{\"status\": \"error\", \"message\": \"Error: {str(e)[:100]}\", \"progress\": 0}}\n\n"
        finally:
            if temp_file_path:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")
