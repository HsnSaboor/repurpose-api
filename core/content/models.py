"""
Content Generation Models
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Content Configuration
# ============================================================================

# Default content field limits (can be overridden via config)
DEFAULT_FIELD_LIMITS = {
    "reel_title_max": 100,
    "reel_caption_max": 300,
    "reel_hook_max": 200,
    "reel_script_max": 2000,
    "carousel_title_max": 100,
    "carousel_caption_max": 300,
    "carousel_slide_heading_max": 100,
    "carousel_slide_text_max": 800,  # Increased from 300 for more detailed content
    "carousel_min_slides": 4,
    "carousel_max_slides": 8,
    "tweet_title_max": 100,
    "tweet_text_max": 280,
    "tweet_thread_item_max": 280
}

# Global variable to store current field limits (can be updated dynamically)
CURRENT_FIELD_LIMITS = DEFAULT_FIELD_LIMITS.copy()


def update_field_limits(new_limits: dict):
    """Update the global field limits configuration"""
    global CURRENT_FIELD_LIMITS
    CURRENT_FIELD_LIMITS.update(new_limits)


def get_field_limit(key: str) -> int:
    """Get a specific field limit"""
    return CURRENT_FIELD_LIMITS.get(key, DEFAULT_FIELD_LIMITS.get(key, 1000))


# ============================================================================
# Content Types and Models
# ============================================================================

class ContentType(str, Enum):
    REEL = "reel"
    IMAGE_CAROUSEL = "image_carousel"
    TWEET = "tweet"


class ContentIdea(BaseModel):
    suggested_content_type: Literal["reel", "image_carousel", "tweet"] = Field(..., description="Type of content suggested.")
    suggested_title: str = Field(..., max_length=100, description="Suggested title for the content.")
    relevant_transcript_snippet: str = Field(..., description="Snippet from the transcript that inspired this idea.")
    type_specific_suggestions: Optional[Dict[str, Any]] = Field(None, description="Type-specific suggestions for the content.")


class GeneratedIdeas(BaseModel):
    ideas: List[ContentIdea] = Field(..., description="A list of generated content ideas.")


class CarouselSlide(BaseModel):
    slide_number: int
    step_number: int = Field(..., description="Step number in the carousel.")
    step_heading: str = Field(..., description="Heading for this step.")
    text: str = Field(None, description="Detailed text content for the slide. This is the main content.")


class Reel(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.REEL] = ContentType.REEL
    title: str = Field(...)
    caption: str = Field(None)
    hook: str = Field(..., description="Attention-grabbing hook.")
    script_body: str = Field(..., description="Main script content.")
    visual_suggestions: Optional[str] = Field(None)
    hashtags: List[str] = Field(None)


class ImageCarousel(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.IMAGE_CAROUSEL] = ContentType.IMAGE_CAROUSEL
    title: str = Field(...)
    caption: str = Field(None)
    slides: List[CarouselSlide] = Field(...)
    hashtags: List[str] = Field(None)


class Tweet(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.TWEET] = ContentType.TWEET
    title: str = Field(...)
    tweet_text: str = Field(...)
    thread_continuation: Optional[List[str]] = Field(None)
    hashtags: List[str] = Field(None)


class GeneratedContentList(BaseModel):
    pieces: List[Union[Reel, ImageCarousel, Tweet]]
