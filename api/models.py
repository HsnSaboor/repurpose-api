"""
API Request/Response Models and Configuration
"""

from pydantic import BaseModel, HttpUrl, Field, root_validator
from typing import Optional, List, Dict, Any, Union, Literal


# ============================================================================
# Content Configuration Models
# ============================================================================

class ContentFieldLimits(BaseModel):
    """Configuration for field length limits per content type"""
    # Reel fields
    reel_title_max: int = Field(100, description="Max length for reel titles")
    reel_caption_max: int = Field(300, description="Max length for reel captions")
    reel_hook_max: int = Field(200, description="Max length for reel hooks")
    reel_script_max: int = Field(2000, description="Max length for reel scripts")
    
    # Carousel fields
    carousel_title_max: int = Field(100, description="Max length for carousel titles")
    carousel_caption_max: int = Field(300, description="Max length for carousel captions")
    carousel_slide_heading_max: int = Field(100, description="Max length for carousel slide headings")
    carousel_slide_text_max: int = Field(800, description="Max length for carousel slide text (detailed content)")
    carousel_min_slides: int = Field(4, description="Minimum number of slides in carousel")
    carousel_max_slides: int = Field(8, description="Maximum number of slides in carousel")
    
    # Tweet fields
    tweet_title_max: int = Field(100, description="Max length for tweet titles")
    tweet_text_max: int = Field(280, description="Max length for tweet text")
    tweet_thread_item_max: int = Field(280, description="Max length for thread continuation items")


class ContentGenerationConfig(BaseModel):
    """Configuration for content generation behavior"""
    min_ideas: int = Field(6, description="Minimum number of content ideas to generate")
    max_ideas: int = Field(8, description="Maximum number of content ideas to generate")
    content_pieces_per_idea: int = Field(1, description="Number of content pieces per idea")
    field_limits: ContentFieldLimits = Field(default_factory=ContentFieldLimits, description="Field length limits")


# ============================================================================
# Content Style Models
# ============================================================================

class ContentStylePreset(BaseModel):
    name: str = Field(..., description="Name of the content style preset")
    description: str = Field(..., description="Description of the style")
    target_audience: str = Field(..., description="Target audience for the content")
    call_to_action: str = Field(..., description="Call to action to include")
    content_goal: str = Field(..., description="Goal of the content (education, lead_generation, etc.)")
    language: str = Field("English", description="Language for content generation")
    tone: str = Field("Professional", description="Tone of the content (Professional, Casual, Humorous, etc.)")
    additional_instructions: Optional[str] = Field(None, description="Additional style instructions")
    content_config: ContentGenerationConfig = Field(default_factory=ContentGenerationConfig, description="Content generation configuration")


class CustomContentStyle(BaseModel):
    target_audience: str = Field(..., description="Target audience for the content")
    call_to_action: str = Field(..., description="Call to action to include")
    content_goal: str = Field(..., description="Goal of the content")
    language: str = Field("English", description="Language for content generation")
    tone: str = Field("Professional", description="Tone of the content")
    additional_instructions: Optional[str] = Field(None, description="Additional style instructions")
    content_config: Optional[ContentGenerationConfig] = Field(None, description="Content generation configuration")


# ============================================================================
# Transcript Models
# ============================================================================

class TranscribeRequest(BaseModel):
    video_id: str = Field(..., description="The YouTube video ID of the video to transcribe.")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Transcript preferences for English processing")


class TranscriptResponse(BaseModel):
    youtube_video_id: str
    title: Optional[str] = None
    transcript: str
    status: Optional[str] = None


class EnhancedTranscriptResponse(BaseModel):
    youtube_video_id: str
    title: Optional[str] = None
    transcript: str
    transcript_metadata: Optional[Dict[str, Any]] = None
    available_languages: List[str] = []
    status: Optional[str] = None


class TranscriptAnalysisResponse(BaseModel):
    youtube_video_id: str
    available_transcripts: List[Dict[str, Any]]
    recommended_approach: str
    processing_notes: List[str]


# ============================================================================
# Video Processing Models
# ============================================================================

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
    ideas: Optional[List[Any]] = Field(None, description="Generated content ideas.")
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


# ============================================================================
# Content Editing Models
# ============================================================================

class EditContentRequest(BaseModel):
    video_id: str = Field(..., description="The YouTube video ID")
    content_piece_id: str = Field(..., description="The ID of the content piece to edit")
    edit_prompt: str = Field(..., description="Natural language prompt describing the desired changes")
    content_type: Literal["reel", "image_carousel", "tweet"] = Field(..., description="Type of content to edit")


class EditContentResponse(BaseModel):
    video_id: str
    content_piece_id: str
    content_type: str
    original_content: Dict[str, Any]
    edited_content: Dict[str, Any]
    changes_made: List[str]
    status: str


# ============================================================================
# Channel Models
# ============================================================================

class ChannelRequest(BaseModel):
    channel_id: str
    max_videos: int = Field(..., ge=1, description="Maximum number of videos to return.")
