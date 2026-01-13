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


# ============================================================================
# Brain Knowledge Base Models (v2.0)
# ============================================================================

class BrainSourceBase(BaseModel):
    """Base fields for Brain source"""
    title: str = Field(..., min_length=1, max_length=500, description="Title of the source")
    content: str = Field(..., min_length=1, description="Main content text")
    source_type: Literal["youtube", "document", "text", "url"] = Field(..., description="Type of source")
    summary: Optional[str] = Field(None, max_length=1000, description="AI-generated summary")
    topics: Optional[List[str]] = Field(None, description="Extracted topics")
    tags: Optional[List[str]] = Field(None, description="User-defined tags")
    source_metadata: Optional[Dict[str, Any]] = Field(None, description="Source-specific metadata")


class BrainSourceCreate(BrainSourceBase):
    """Request model for creating a Brain source"""
    pass


class URLExtractOptions(BaseModel):
    """Options for URL content extraction"""
    include_tables: bool = Field(default=True, description="Include tables in extracted content")
    include_links: bool = Field(default=True, description="Preserve hyperlinks in content")
    include_images: bool = Field(default=False, description="Include image references")


class URLSourceCreate(BaseModel):
    """Request model for creating a Brain source from URL"""
    url: str = Field(..., min_length=10, description="URL to fetch and extract content from")
    title: Optional[str] = Field(None, max_length=500, description="Custom title (auto-extracted if not provided)")
    tags: Optional[List[str]] = Field(None, description="User-defined tags")
    extract_options: Optional[URLExtractOptions] = Field(
        default_factory=URLExtractOptions,
        description="Content extraction options"
    )


class BrainSourceUpdate(BaseModel):
    """Request model for updating a Brain source"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=1000)
    topics: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    source_metadata: Optional[Dict[str, Any]] = None


class BrainSourceResponse(BrainSourceBase):
    """Response model for a Brain source"""
    source_id: str
    use_count: int = 0
    last_used_at: Optional[str] = None
    created_at: str
    updated_at: str
    has_embedding: bool = False

    class Config:
        from_attributes = True


class BrainSourceListResponse(BaseModel):
    """Paginated list of Brain sources"""
    sources: List[BrainSourceResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================================
# Brain Vision-Based Generation Models
# ============================================================================

class VisionGenerateRequest(BaseModel):
    """Request for vision-based content generation"""
    user_vision: str = Field(..., min_length=10, max_length=2000, description="User's content idea/vision")
    content_types: List[Literal["reel", "image_carousel", "tweet"]] = Field(
        default=["reel", "tweet"], 
        description="Types of content to generate"
    )
    style_preset: Optional[str] = Field(None, description="Name of style preset to use")
    custom_style: Optional[CustomContentStyle] = Field(None, description="Custom style configuration")
    max_sources: int = Field(default=5, ge=1, le=20, description="Max sources to match")
    min_match_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum relevance score")


class MatchedSource(BaseModel):
    """A source matched to user's vision"""
    source_id: str
    title: str
    source_type: str
    match_score: float
    matched_topics: List[str] = []
    snippet: str = Field(..., description="Relevant content snippet")


class VisionGenerateResponse(BaseModel):
    """Response for vision-based generation"""
    session_id: str
    matched_sources: List[MatchedSource]
    generated_content: List[Dict[str, Any]]
    total_matches: int
    status: str


# ============================================================================
# Brain Full AI Mode Models
# ============================================================================

class AutoGenerateSingleRequest(BaseModel):
    """Request for single source auto-generation"""
    source_id: str = Field(..., description="ID of the source to use")
    content_types: List[Literal["reel", "image_carousel", "tweet"]] = Field(
        default=["reel", "tweet"]
    )
    style_preset: Optional[str] = None
    custom_style: Optional[CustomContentStyle] = None


class AutoGenerateMultipleRequest(BaseModel):
    """Request for multiple sources auto-generation"""
    source_ids: List[str] = Field(..., min_length=1, max_length=10, description="Source IDs to use")
    content_count: int = Field(default=5, ge=1, le=20, description="Number of pieces to generate")
    content_types: List[Literal["reel", "image_carousel", "tweet"]] = Field(
        default=["reel", "tweet"]
    )
    style_preset: Optional[str] = None
    custom_style: Optional[CustomContentStyle] = None


class AutoGenerateAutoRequest(BaseModel):
    """Request for auto-selection auto-generation"""
    content_count: int = Field(default=5, ge=1, le=20, description="Number of pieces to generate")
    content_types: List[Literal["reel", "image_carousel", "tweet"]] = Field(
        default=["reel", "tweet"]
    )
    source_types: Optional[List[Literal["youtube", "document", "text", "url"]]] = Field(
        None, description="Filter by source types"
    )
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    topics: Optional[List[str]] = Field(None, description="Filter by topics")
    style_preset: Optional[str] = None
    custom_style: Optional[CustomContentStyle] = None


class AutoGenerateResponse(BaseModel):
    """Response for auto-generation modes"""
    session_id: str
    sources_used: List[Dict[str, Any]]
    generated_content: List[Dict[str, Any]]
    content_count: int
    status: str


# ============================================================================
# Brain Hybrid Mode Models
# ============================================================================

class HybridGenerateRequest(BaseModel):
    """Request for hybrid source selection generation"""
    selected_source_ids: List[str] = Field(
        ..., 
        min_length=1, 
        max_length=10, 
        description="User-selected source IDs"
    )
    ai_augment_hint: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Hint for AI to find related sources"
    )
    ai_augment_strategy: Literal["augment", "fill", "support"] = Field(
        default="augment",
        description="Strategy: augment=add related, fill=complete gaps, support=find supporting"
    )
    ai_augment_count: int = Field(
        default=3, 
        ge=0, 
        le=10, 
        description="Max AI-discovered sources"
    )
    content_count: int = Field(default=5, ge=1, le=20)
    content_types: List[Literal["reel", "image_carousel", "tweet"]] = Field(
        default=["reel", "tweet"]
    )
    style_preset: Optional[str] = None
    custom_style: Optional[CustomContentStyle] = None


class HybridGenerateResponse(BaseModel):
    """Response for hybrid generation"""
    session_id: str
    user_sources: List[Dict[str, Any]]
    ai_discovered_sources: List[Dict[str, Any]]
    combined_sources_count: int
    generated_content: List[Dict[str, Any]]
    content_count: int
    status: str


# ============================================================================
# Brain Search Models
# ============================================================================

class BrainSearchRequest(BaseModel):
    """Request for semantic search in Brain"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    source_types: Optional[List[Literal["youtube", "document", "text", "url"]]] = None
    tags: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    limit: int = Field(default=10, ge=1, le=50)
    min_score: float = Field(default=0.3, ge=0.0, le=1.0)


class BrainSearchResult(BaseModel):
    """A single search result"""
    source_id: str
    title: str
    source_type: str
    relevance_score: float
    snippet: str
    topics: List[str] = []
    tags: List[str] = []


class BrainSearchResponse(BaseModel):
    """Response for Brain search"""
    results: List[BrainSearchResult]
    total_results: int
    query: str


# ============================================================================
# Brain Session Models
# ============================================================================

class BrainSessionResponse(BaseModel):
    """Response model for a Brain session"""
    session_id: str
    mode: str
    status: str
    user_vision: Optional[str] = None
    selected_source_ids: Optional[List[str]] = None
    matched_source_ids: Optional[List[str]] = None
    ai_discovered_source_ids: Optional[List[str]] = None
    generated_count: Optional[int] = None
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

