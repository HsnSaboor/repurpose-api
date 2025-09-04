import logging
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl, ValidationError, Field, root_validator
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any, Union, Literal
from core.database import init_db, SessionLocal, Video
from youtube_transcript_api import YouTubeTranscriptApi
from repurpose import (
    generate_content_ideas,
    generate_specific_content_pieces,
    ContentIdea,
    GeneratedIdeas,
    GeneratedContentList,
    extract_video_id as repurpose_extract_video_id,
    get_video_title,
    Reel,
    ImageCarousel,
    Tweet,
    ContentType,
    edit_content_piece_with_diff,
    identify_content_changes
)
from channelvideos_alt import get_channel_videos
import ast
import json
import requests
import logging
import time

print("DEBUG: main.py top-level print statement executed.")

# Content Style Models
class ContentStylePreset(BaseModel):
    name: str = Field(..., description="Name of the content style preset")
    description: str = Field(..., description="Description of the style")
    target_audience: str = Field(..., description="Target audience for the content")
    call_to_action: str = Field(..., description="Call to action to include")
    content_goal: str = Field(..., description="Goal of the content (education, lead_generation, etc.)")
    language: str = Field("English", description="Language for content generation")
    tone: str = Field("Professional", description="Tone of the content (Professional, Casual, Humorous, etc.)")
    additional_instructions: Optional[str] = Field(None, description="Additional style instructions")

class CustomContentStyle(BaseModel):
    target_audience: str = Field(..., description="Target audience for the content")
    call_to_action: str = Field(..., description="Call to action to include")
    content_goal: str = Field(..., description="Goal of the content")
    language: str = Field("English", description="Language for content generation")
    tone: str = Field("Professional", description="Tone of the content")
    additional_instructions: Optional[str] = Field(None, description="Additional style instructions")

# Request/Response Models
class TranscribeRequest(BaseModel):
    video_id: str = Field(..., description="The YouTube video ID of the video to transcribe.")

class TranscriptResponse(BaseModel):
    youtube_video_id: str
    title: Optional[str] = None
    transcript: str
    status: Optional[str] = None

class ProcessVideoRequest(BaseModel):
    video_id: str = Field(..., description="The YouTube video ID of the video to process.")
    force_regenerate: Optional[bool] = Field(False, description="Force regeneration of content even if it exists.")
    style_preset: Optional[str] = Field(None, description="Name of content style preset to use")
    custom_style: Optional[CustomContentStyle] = Field(None, description="Custom content style configuration")

class ProcessVideoResponse(BaseModel):
    id: Optional[int] = Field(None, description="The internal database ID of the video.")
    youtube_video_id: str = Field(..., description="The YouTube video ID.")
    title: Optional[str] = Field(None, description="The title of the YouTube video.")
    transcript: Optional[str] = Field(None, description="The transcript of the video.")
    status: Optional[str] = Field(None, description="The processing status of the video.")
    ideas: Optional[List[ContentIdea]] = Field(None, description="Generated content ideas.")
    content_pieces: Optional[List[Any]] = Field(None, description="Generated content pieces (e.g., Reels, Tweets).")

    class Config:
        from_attributes = True

class BulkVideoProcessRequest(BaseModel):
    video_ids: List[str] = Field(..., description="A list of YouTube video IDs to process.")

class BulkVideoProcessResponseItem(BaseModel):
    video_id: str
    status: str
    details: Optional[str] = None
    data: Optional[ProcessVideoResponse] = None

class ChannelRequest(BaseModel):
    channel_id: str
    max_videos: int = Field(..., ge=1, description="Maximum number of videos to return.")

class EditContentRequest(BaseModel):
    video_id: str = Field(..., description="The YouTube video ID of the video containing the content piece.")
    content_piece_id: str = Field(..., description="The ID of the content piece to edit (e.g., 'video_id_001').")
    edit_prompt: str = Field(..., description="Natural language prompt describing the changes to make.")
    content_type: Literal["reel", "image_carousel", "tweet"] = Field(..., description="Type of content piece being edited.")

class EditContentResponse(BaseModel):
    success: bool = Field(..., description="Whether the edit was successful.")
    content_piece_id: str = Field(..., description="The ID of the edited content piece.")
    original_content: Optional[Dict[str, Any]] = Field(None, description="The original content before editing.")
    edited_content: Optional[Dict[str, Any]] = Field(None, description="The new edited content.")
    changes_made: Optional[List[str]] = Field(None, description="List of changes that were made.")
    error_message: Optional[str] = Field(None, description="Error message if edit failed.")

# Content Style Presets
CONTENT_STYLE_PRESETS = {
    "ecommerce_entrepreneur": ContentStylePreset(
        name="E-commerce Entrepreneur",
        description="For e-commerce entrepreneurs and Shopify store owners",
        target_audience="ecom entrepreneurs, Shopify store owners, and DTC brands looking to launch, improve design, or scale with ads",
        call_to_action="DM us to launch or fix your store, check our portfolio, and follow for ROI-boosting tips",
        content_goal="education, lead_generation, brand_awareness",
        language="Roman Urdu",
        tone="Educational and engaging",
        additional_instructions="CRITICAL LANGUAGE RULE: The output language MUST be Roman Urdu. Roman Urdu means writing Urdu words using the English alphabet. DO NOT use the native Urdu script."
    ),
    "professional_business": ContentStylePreset(
        name="Professional Business",
        description="Professional business content for corporate audiences",
        target_audience="business professionals, entrepreneurs, and corporate decision makers",
        call_to_action="Contact us for consultation, follow for business insights",
        content_goal="thought_leadership, brand_awareness, lead_generation",
        language="English",
        tone="Professional and authoritative",
        additional_instructions="Use industry terminology and maintain a professional tone throughout"
    ),
    "social_media_casual": ContentStylePreset(
        name="Social Media Casual",
        description="Casual, engaging content for social media audiences",
        target_audience="general social media users, millennials, and Gen Z",
        call_to_action="Like, share, and follow for more content",
        content_goal="entertainment, engagement, brand_awareness",
        language="English",
        tone="Casual and fun",
        additional_instructions="Use emojis, trendy language, and keep it conversational"
    ),
    "educational_content": ContentStylePreset(
        name="Educational Content",
        description="Educational and informative content for learners",
        target_audience="students, professionals seeking knowledge, lifelong learners",
        call_to_action="Subscribe for more educational content, share with others",
        content_goal="education, knowledge_sharing, community_building",
        language="English",
        tone="Informative and encouraging",
        additional_instructions="Break down complex topics into digestible pieces, use examples and analogies"
    ),
    "fitness_wellness": ContentStylePreset(
        name="Fitness & Wellness",
        description="Health, fitness, and wellness focused content",
        target_audience="fitness enthusiasts, health-conscious individuals, wellness seekers",
        call_to_action="Follow for daily tips, share your progress, join our community",
        content_goal="motivation, education, community_building",
        language="English",
        tone="Motivational and supportive",
        additional_instructions="Use encouraging language, focus on positive health outcomes, include actionable tips"
    )
}

def get_content_style_prompt(style_preset: Optional[str] = None, custom_style: Optional[CustomContentStyle] = None) -> str:
    """Generate content style prompt based on preset or custom style"""
    if custom_style:
        style_text = f"""
        "Target Audience: {custom_style.target_audience}"
        "Call To Action: {custom_style.call_to_action}"
        "Content Goal: {custom_style.content_goal}"
        "Language: {custom_style.language}"
        "Tone: {custom_style.tone}"
        """
        if custom_style.additional_instructions:
            style_text += f'"Additional Instructions: {custom_style.additional_instructions}"'
    elif style_preset and style_preset in CONTENT_STYLE_PRESETS:
        preset = CONTENT_STYLE_PRESETS[style_preset]
        style_text = f"""
        "Target Audience: {preset.target_audience}"
        "Call To Action: {preset.call_to_action}"
        "Content Goal: {preset.content_goal}"
        "Language: {preset.language}"
        "Tone: {preset.tone}"
        """
        if preset.additional_instructions:
            style_text += f'"Additional Instructions: {preset.additional_instructions}"'
    else:
        # Default style (original ecommerce style)
        style_text = """
        "Target Audience: ecom entrepreneurs, Shopify store owners, and DTC brands looking to launch, improve design, or scale with ads."
        "Call To Action: DM us to launch or fix your store, check our portfolio, and follow for ROI-boosting tips."
        "Content Goal: education, lead_generation, brand_awareness."
        "Language: Roman Urdu"
        "Tone: Educational and engaging"
        "CRITICAL LANGUAGE RULE: The output language MUST be Roman Urdu. Roman Urdu means writing Urdu words using the English alphabet. DO NOT use the native Urdu script."
        """
    
    return style_text

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="YouTube Repurposer API", version="0.1.3")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

executor = ThreadPoolExecutor(max_workers=10)


@app.get("/content-styles/presets/")
async def get_style_presets():
    """Get all available content style presets"""
    return {
        "presets": {
            key: {
                "name": preset.name,
                "description": preset.description,
                "target_audience": preset.target_audience,
                "language": preset.language,
                "tone": preset.tone
            } for key, preset in CONTENT_STYLE_PRESETS.items()
        }
    }

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
            
            yield f"data: {{\"status\": \"transcribing\", \"message\": \"Extracting transcript...\", \"progress\": 30}}\n\n"
            
            # Get transcript
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(request.video_id)
                transcript = ' '.join([item['text'] for item in transcript_list])
                yield f"data: {{\"status\": \"transcript_ready\", \"message\": \"Transcript extracted successfully\", \"progress\": 50}}\n\n"
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
            
            # Generate content
            ideas_raw = await asyncio.get_event_loop().run_in_executor(
                executor,
                generate_content_ideas,
                transcript,
                request.style_preset,
                request.custom_style.dict() if request.custom_style else None
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
                request.custom_style.dict() if request.custom_style else None
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
@app.get("/content-styles/presets/{preset_name}")
async def get_style_preset(preset_name: str):
    """Get details of a specific content style preset"""
    if preset_name not in CONTENT_STYLE_PRESETS:
        raise HTTPException(status_code=404, detail=f"Style preset '{preset_name}' not found")
    
    preset = CONTENT_STYLE_PRESETS[preset_name]
    return {
        "name": preset.name,
        "description": preset.description,
        "target_audience": preset.target_audience,
        "call_to_action": preset.call_to_action,
        "content_goal": preset.content_goal,
        "language": preset.language,
        "tone": preset.tone,
        "additional_instructions": preset.additional_instructions
    }
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
                    ytt_api = YouTubeTranscriptApi()
                    transcript = ytt_api.fetch(db_video.youtube_video_id)
                    transcript_text = " ".join([entry['text'] for entry in transcript.to_raw_data()]) if transcript else "Transcript unavailable"
                except Exception as e:
                    logging.error(f"Failed to fetch transcript: {str(e)}")
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
                ytt_api = YouTubeTranscriptApi()
                transcript = ytt_api.fetch(youtube_id_from_request)
                transcript_text = " ".join([entry['text'] for entry in transcript.to_raw_data()]) if transcript else "Transcript unavailable"
            except Exception as e:
                logging.error(f"Failed to fetch transcript: {str(e)}")
                transcript_text = "Transcript unavailable"
            
            print(f"DEBUG: Transcript for {youtube_id_from_request}: {'Fetched' if transcript_text else 'Failed to fetch'}")

            print(f"DEBUG: Creating new Video object for {youtube_id_from_request} with title '{video_title}'.")
            new_video = Video(
                youtube_video_id=youtube_id_from_request,
                title=video_title,
                transcript=transcript_text,
                status="processed"
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
                ytt_api = YouTubeTranscriptApi()
                transcript = ytt_api.fetch(youtube_id_from_request)
                transcript_text = " ".join([entry['text'] for entry in transcript.to_raw_data()]) if transcript else "Transcript unavailable"
            except Exception as e:
                logging.error(f"Failed to fetch transcript: {str(e)}")
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
                    ytt_api = YouTubeTranscriptApi()
                    transcript = ytt_api.fetch(db_video.youtube_video_id)
                    transcript_text = " ".join([entry['text'] for entry in transcript.to_raw_data()]) if transcript else "Transcript unavailable"
                except Exception as e:
                    logging.error(f"Failed to fetch transcript: {str(e)}")
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
            if request.custom_style:
                custom_style_dict = {
                    'target_audience': request.custom_style.target_audience,
                    'call_to_action': request.custom_style.call_to_action,
                    'content_goal': request.custom_style.content_goal,
                    'language': request.custom_style.language,
                    'tone': request.custom_style.tone,
                    'additional_instructions': request.custom_style.additional_instructions
                }

            ideas_data_raw = await loop.run_in_executor(executor, generate_content_ideas, db_video.transcript, style_preset, custom_style_dict)
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
                custom_style_dict
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
