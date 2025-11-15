# -*- coding: utf-8 -*-
"""YouTube Video Processor with Gemini AI Integration via OpenAI Compatibility Layer
Handles various inputs, fetches transcripts, generates content (Reels, Tweets, Carousels),
and exports to a structured format with special handling for Image Carousels.
"""

# --- Imports ---
import argparse
import csv
import json
import logging
import os
import re
import sys
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from enum import Enum
from logging import StreamHandler
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd
import yt_dlp
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.progress import (BarColumn, Progress, SpinnerColumn, TaskProgressColumn,
                           TextColumn, TimeElapsedColumn, TimeRemainingColumn)
from yt_dlp.utils import DownloadError

# Import services
from core.services.transcript_service import get_english_transcript, TranscriptPreferences
from core.services.content_service import ContentGenerator, ContentIdea
from core.services.video_service import get_video_title
from core.services.document_service import DocumentParser, extract_text_from_document

# Load environment variables from .env file
load_dotenv()

# --- Content Style Definition (IMPROVED FOR ROMAN URDU) ---
CONTENT_STYLE = """
    "Target Audience: ecom entrepreneurs, Shopify store owners, and DTC brands looking to launch, improve design, or scale with ads."
    "Call To Action: DM us to launch or fix your store, check our portfolio, and follow for ROI-boosting tips."
    "Content Goal: education, lead_generation, brand_awareness."
    "---"
    "CRITICAL LANGUAGE RULE: The output language MUST be Roman Urdu."
    "Roman Urdu means writing Urdu words using the English alphabet. DO NOT use the native Urdu script."
    "EXAMPLE:"
    "  - CORRECT (Roman Urdu): 'Aap kaise hain?'"
    "  - INCORRECT (Urdu Script): 'آپ کیسے ہیں؟'"
    "This is a strict requirement for all generated text, including titles, captions, and scripts."
"""

# --- Pydantic Models ---
class ContentIdea(BaseModel):
    suggested_content_type: Literal["reel", "image_carousel", "tweet"] = Field(..., description="Type of content suggested.")
    suggested_title: str = Field(..., max_length=100, description="Suggested title for the content.")
    relevant_transcript_snippet: str = Field(..., description="Snippet from the transcript that inspired this idea.")
    type_specific_suggestions: Optional[Dict[str, Any]] = Field(None, description="Type-specific suggestions for the content.")

class GeneratedIdeas(BaseModel):
    ideas: List[ContentIdea] = Field(..., description="A list of generated content ideas.")

class ContentType(str, Enum):
    REEL = "reel"
    IMAGE_CAROUSEL = "image_carousel"
    TWEET = "tweet"

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

class CarouselSlide(BaseModel):
    slide_number: int
    step_number: int = Field(..., description="Step number in the carousel.")
    step_heading : str = Field(..., description="Heading for this step.")
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

# --- Configuration ---
console = Console()
OUTPUT_DIR = "output"
CAROUSELS_DIR = os.path.join(OUTPUT_DIR, "carousels")
SLIDES_DIR = os.path.join(OUTPUT_DIR, "slides")
GENERATED_CONTENT_CSV = os.path.join(OUTPUT_DIR, "generated_content.csv")
REPURPOSE_LOG_FILE = os.path.join(OUTPUT_DIR, 'repurpose.log')

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CAROUSELS_DIR, exist_ok=True)
os.makedirs(SLIDES_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    handlers=[logging.FileHandler(REPURPOSE_LOG_FILE, encoding='utf-8')]
)
logger = logging.getLogger(__name__)

# --- Initialize Content Generator ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    console.print("[bold red]ERROR: GEMINI_API_KEY not found in environment variables. Exiting.[/bold red]")
    sys.exit(1)
gemini_base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
content_generator = ContentGenerator(api_key=api_key, base_url=gemini_base_url)

def extract_video_id(url: str) -> Optional[str]:
    """Extracts the 11-character video ID from various YouTube URL formats."""
    if not isinstance(url, str):
        return None
    patterns = [
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # For standalone IDs
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def call_gemini_api(system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
    rate_limiter.wait_for_capacity()
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"}, temperature=0.7
        )
        if response.choices and response.choices[0].message.content:
            content_str = response.choices[0].message.content.strip()
            if content_str.startswith("```json"): content_str = content_str[7:-3].strip()
            return json.loads(content_str)
        logger.error("No content in LLM response.")
    except Exception as e:
        logger.error(f"Error in API call: {e}", exc_info=True)
    return None

def get_system_prompt_generate_ideas(content_style: str = "{CONTENT_STYLE}", min_ideas: int = 6, max_ideas: int = 8) -> str:
    """Generate the system prompt for idea generation with configurable limits"""
    return f"""
You are an expert AI assistant specializing in analyzing video transcripts to identify diverse, repurposable content ideas.
Your goal is to analyze the provided transcript and suggest {min_ideas} to {max_ideas} distinct content ideas (Reels, Image Carousels, Tweets).

Output Format:
You MUST return a single JSON object. This object must have a single key named "ideas".
The value for "ideas" must be a list of JSON objects with {min_ideas} to {max_ideas} items.
Each object in the list represents one content idea and MUST have the following structure:
{{{{
  "suggested_content_type": "<'reel'|'image_carousel'|'tweet'>",
  "suggested_title": "<string, a catchy and relevant title for the content>",
  "relevant_transcript_snippet": "<string, a short, direct quote from the transcript that inspired this idea>",
  "type_specific_suggestions": {{{{}}}}
}}}}

Content Style to Follow:
{content_style}
"""

def get_system_prompt_generate_content(content_style: str = "{CONTENT_STYLE}") -> str:
    """Generate the system prompt for content generation with configurable field limits"""
    limits = CURRENT_FIELD_LIMITS
    
    return f"""
You are an expert AI content creator. Your task is to take a specific content idea and generate the full content piece.
You MUST follow the JSON schema for the requested `content_type` with absolute precision. All required fields MUST be included.

**Content Type Schemas:**

If `content_type` is "reel", the JSON MUST look like this:
```json
{{{{
  "content_type": "reel",
  "title": "<string, the title for the reel, max {limits['reel_title_max']} chars>",
  "caption": "<string, a short, engaging caption, max {limits['reel_caption_max']} chars>",
  "hook": "<string, a strong, attention-grabbing opening line, max {limits['reel_hook_max']} chars, required>",
  "script_body": "<string, the main script for the reel, max {limits['reel_script_max']} chars, required>",
  "visual_suggestions": "<string, optional suggestions for visuals>",
  "hashtags": ["<list of relevant string hashtags>"]
}}}}


If content_type is "image_carousel", the JSON MUST look like this:
      
{{{{
  "content_type": "image_carousel",
  "title": "<string, the title for the carousel, max {limits['carousel_title_max']} chars>",
  "caption": "<string, a short, engaging caption, max {limits['carousel_caption_max']} chars>",
  "slides": [
    {{{{
      "slide_number": 1,
      "step_number": 1,
      "step_heading": "<string, SHORT heading for this step, max {limits['carousel_slide_heading_max']} chars - e.g., 'Step 1: Setup' or 'Choose Your Niche'>",
      "text": "<string, DETAILED TEXT CONTENT - This is the PRIMARY content field. Write 3-5 sentences with specific details, examples, actionable tips, or explanations. Make it comprehensive and valuable. Min 400 chars recommended, max {limits['carousel_slide_text_max']} chars. Do NOT repeat the heading - only provide the detailed explanation.>"
    }},
    {{{{
      "slide_number": 2,
      "step_number": 2,
      "step_heading": "<string, SHORT heading for this step, max {limits['carousel_slide_heading_max']} chars>",
      "text": "<string, DETAILED TEXT CONTENT - Multiple sentences with specifics, reasoning, examples, and actionable information. Make this substantial and informative. 400-{limits['carousel_slide_text_max']} chars.>"
    }},
    {{{{
      "slide_number": 3,
      "step_number": 3,
      "step_heading": "<string, SHORT heading for this step, max {limits['carousel_slide_heading_max']} chars>",
      "text": "<string, DETAILED TEXT CONTENT - Provide depth and context. Include why, how, or what makes this important. Use examples if relevant. 400-{limits['carousel_slide_text_max']} chars.>"
    }},
    {{{{
      "slide_number": 4,
      "step_number": 4,
      "step_heading": "<string, SHORT heading for this step, max {limits['carousel_slide_heading_max']} chars>",
      "text": "<string, DETAILED TEXT CONTENT - Comprehensive explanation with actionable details. Think mini-article, not caption. 400-{limits['carousel_slide_text_max']} chars.>"
    }}}}
  ],
  "hashtags": ["<list of relevant string hashtags>"]
}}


If content_type is "tweet", the JSON MUST look like this:
      
{{{{
  "content_type": "tweet",
  "title": "<string, an internal title for the tweet, max {limits['tweet_title_max']} chars>",
  "tweet_text": "<string, the main tweet content, max {limits['tweet_text_max']} chars, required>",
  "thread_continuation": ["<list of optional strings for a follow-up thread, each max {limits['tweet_thread_item_max']} chars>"],
  "hashtags": ["<list of relevant string hashtags>"]
}}}}


MANDATORY INSTRUCTIONS:

    For an image_carousel, you MUST generate at least {limits['carousel_min_slides']} slides and at most {limits['carousel_max_slides']} slides.
    
    For carousel slides, the "text" field is the PRIMARY content and MUST be detailed, comprehensive, and valuable:
    - Each slide text should be 400-{limits['carousel_slide_text_max']} characters (aim for longer, more detailed content)
    - Include multiple sentences with actionable information, examples, or explanations
    - Provide context, reasoning, or supporting details - not just a single statement
    - Make the text self-contained and informative without relying solely on the heading
    - Think of it as a mini-article or detailed explanation, not just a caption
    
    The step_heading is just a short label (max {limits['carousel_slide_heading_max']} chars), while the text field is where the real value lies.

    Stirctly Follow the Language Constraint in {content_style}.

    Your entire output must be a single, valid JSON object that matches one of the schemas above.

    Do NOT include content_id in your response.

    The generated text must strictly follow this style: {content_style}
"""

def generate_content_ideas(transcript: str, style_preset: Optional[str] = None, custom_style: Optional[Dict[str, Any]] = None, content_config: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
    """Generate content ideas with optional style customization and configurable limits"""
    
    # Update field limits if provided in content_config
    if content_config and 'field_limits' in content_config:
        update_field_limits(content_config['field_limits'])
    
    # Get min/max ideas from config
    min_ideas = content_config.get('min_ideas', 6) if content_config else 6
    max_ideas = content_config.get('max_ideas', 8) if content_config else 8
    
    # Build style text
    if custom_style:
        style_text = f"""
        "Target Audience: {custom_style.get('target_audience', 'general audience')}"
        "Call To Action: {custom_style.get('call_to_action', 'engage with our content')}"
        "Content Goal: {custom_style.get('content_goal', 'engagement')}"
        "Language: {custom_style.get('language', 'English')}"
        "Tone: {custom_style.get('tone', 'Professional')}"
        """
        if custom_style.get('additional_instructions'):
            style_text += f'"Additional Instructions: {custom_style["additional_instructions"]}"'
    elif style_preset:
        if style_preset == "ecommerce_entrepreneur":
            style_text = CONTENT_STYLE
        else:
            style_text = """
            "Target Audience: general audience interested in the topic"
            "Call To Action: engage with our content and follow for more"
            "Content Goal: education, engagement"
            "Language: English"
            "Tone: Professional and engaging"
            """
    else:
        style_text = CONTENT_STYLE
    
    # Generate dynamic system prompt with configured limits
    dynamic_system_prompt = get_system_prompt_generate_ideas(style_text, min_ideas, max_ideas)
    
    user_prompt = f"Transcript:\n{transcript}\n\nPlease analyze and generate ideas based on system prompt instructions."
    raw_response = content_generator.generate_content(dynamic_system_prompt, user_prompt)
    if raw_response and isinstance(raw_response.get('ideas'), list):
        console.log(f"[green]Successfully generated {len(raw_response['ideas'])} content ideas.[/green]")
        return raw_response['ideas']
    console.log(f"[yellow]LLM response for idea generation was invalid or empty.[/yellow]")
    logger.error(f"Invalid idea response: {raw_response}")
    return None

def edit_content_piece_with_diff(original_content: Dict[str, Any], edit_prompt: str, content_type: str) -> Optional[Dict[str, Any]]:
    """Edit a content piece using LLM with diff-based editing"""
    
    # Get current field limits
    limits = CURRENT_FIELD_LIMITS
    
    # Create a system prompt for diff-based editing
    edit_system_prompt = f"""
You are an expert content editor specializing in precise, diff-based editing of social media content.
Your task is to make ONLY the specific changes requested by the user while preserving everything else.

**CRITICAL INSTRUCTIONS:**
1. Make ONLY the changes explicitly requested in the edit prompt
2. Preserve all other content exactly as it was
3. Ensure the edited content still meets all validation requirements:
   - caption: Maximum {limits['carousel_caption_max']} characters (for carousels) or {limits['reel_caption_max']} characters (for reels)
   - title: Maximum {limits['reel_title_max']} characters
   - tweet_text: Maximum {limits['tweet_text_max']} characters (for tweets)
   - step_heading: Maximum {limits['carousel_slide_heading_max']} characters (for carousel slides)
   - slide text: Maximum {limits['carousel_slide_text_max']} characters (for carousel slides) - should be detailed and comprehensive

**CONTENT TYPE SPECIFIC REQUIREMENTS:**
{CONTENT_STYLE}

**OUTPUT FORMAT:**
Return the complete edited content piece as JSON, maintaining the exact same structure as the original.
Include ALL fields from the original, changing only what was specifically requested.
"""
    
    # Create detailed edit prompt
    user_edit_prompt = f"""ORIGINAL CONTENT:
{json.dumps(original_content, indent=2)}

EDIT REQUEST:
{edit_prompt}

Please apply the requested changes to the above {content_type} content while:
1. Keeping all unchanged fields exactly the same
2. Ensuring the edited content meets all validation requirements
3. Maintaining the content style and structure
4. Only changing what was specifically requested

Return the complete edited content as JSON."""
    
    try:
        edited_content = content_generator.generate_content(edit_system_prompt, user_edit_prompt)
        
        if not edited_content:
            console.log(f"[red]Failed to generate edited content[/red]")
            return None
        
        # Ensure content_id is preserved from original
        edited_content['content_id'] = original_content.get('content_id')
        
        # Validate the edited content
        try:
            if content_type == ContentType.REEL.value:
                Reel(**edited_content)  # Test validation
            elif content_type == ContentType.IMAGE_CAROUSEL.value:
                ImageCarousel(**edited_content)  # Test validation
            elif content_type == ContentType.TWEET.value:
                Tweet(**edited_content)  # Test validation
            else:
                console.log(f"[red]Unknown content type: '{content_type}'[/red]")
                return None
            
            console.log(f"[green]✅ Content piece edited successfully[/green]")
            return edited_content
            
        except ValidationError as e:
            console.log(f"[red]Edited content failed validation: {e}[/red]")
            return None
    
    except Exception as e:
        console.log(f"[red]Error during content editing: {e}[/red]")
        return None

def identify_content_changes(original: Dict[str, Any], edited: Dict[str, Any]) -> List[str]:
    """Identify what changes were made between original and edited content"""
    changes = []
    
    # Compare all fields
    for key in original.keys():
        if key in edited and str(original[key]) != str(edited[key]):
            if key == 'slides' and isinstance(original[key], list) and isinstance(edited[key], list):
                # Special handling for carousel slides
                if len(original[key]) != len(edited[key]):
                    changes.append(f"Number of slides changed from {len(original[key])} to {len(edited[key])}")
                else:
                    for i, (orig_slide, edit_slide) in enumerate(zip(original[key], edited[key])):
                        for slide_key in orig_slide.keys():
                            if slide_key in edit_slide and str(orig_slide[slide_key]) != str(edit_slide[slide_key]):
                                changes.append(f"Slide {i+1} {slide_key} changed")
            else:
                changes.append(f"'{key}' changed")
    
    # Check for new fields
    for key in edited.keys():
        if key not in original:
            changes.append(f"Added new field '{key}'")
    
    return changes if changes else ["No changes detected"]

def fix_validation_errors(raw_content: Dict[str, Any], validation_error: ValidationError, idea: ContentIdea, original_transcript: str, video_url: str, dynamic_system_prompt: str, max_retries: int = 2) -> Optional[Dict[str, Any]]:
    """Attempt to fix validation errors by regenerating the problematic fields"""
    
    for attempt in range(max_retries):
        console.log(f"[yellow]Attempting to fix validation errors (attempt {attempt + 1}/{max_retries})...[/yellow]")
        
        # Extract specific validation issues
        error_details = []
        for error in validation_error.errors():
            field = '.'.join(str(loc) for loc in error['loc'])
            error_type = error['type']
            message = error['msg']
            error_details.append(f"Field '{field}': {message} (type: {error_type})")
        
        # Get current field limits
        limits = CURRENT_FIELD_LIMITS
        
        # Create a specific prompt to fix the validation issues
        fix_prompt = f"""The previously generated content failed validation with these specific errors:

{chr(10).join(error_details)}

Please regenerate the content for '{idea.suggested_content_type}' type, ensuring ALL validation requirements are met:

**CRITICAL REQUIREMENTS:**
- caption: Must be {limits['carousel_caption_max']} characters or less (for carousels) or {limits['reel_caption_max']} characters or less (for reels)
- title: Must be {limits['reel_title_max']} characters or less (max for all types)
- tweet_text: Must be {limits['tweet_text_max']} characters or less (for tweets)
- step_heading: Must be {limits['carousel_slide_heading_max']} characters or less (for carousel slides)
- slide text: Must be {limits['carousel_slide_text_max']} characters or less (for carousel slides) - make this detailed and comprehensive

Content Idea: {json.dumps(idea.model_dump(), indent=2)}

Previous content that failed validation:
{json.dumps(raw_content, indent=2)}

Please fix the specific validation errors and regenerate the complete content piece."""
        
        fixed_content = content_generator.generate_content(dynamic_system_prompt, fix_prompt)
        if not fixed_content:
            console.log(f"[red]Failed to generate fixed content on attempt {attempt + 1}[/red]")
            continue
        
        # Copy the content_id from the original
        fixed_content['content_id'] = raw_content.get('content_id')
        
        # Try to validate the fixed content
        try:
            content_type = fixed_content.get('content_type')
            if content_type == ContentType.REEL.value:
                Reel(**fixed_content)  # Test validation
            elif content_type == ContentType.IMAGE_CAROUSEL.value:
                ImageCarousel(**fixed_content)  # Test validation
            elif content_type == ContentType.TWEET.value:
                Tweet(**fixed_content)  # Test validation
            else:
                console.log(f"[red]Fixed content has unknown type: '{content_type}'.[/red]")
                continue
            
            console.log(f"[green]✅ Successfully fixed validation errors on attempt {attempt + 1}[/green]")
            return fixed_content
            
        except ValidationError as retry_error:
            console.log(f"[yellow]Validation still failing on attempt {attempt + 1}: {retry_error}[/yellow]")
            continue
    
    console.log(f"[red]❌ Failed to fix validation errors after {max_retries} attempts[/red]")
    return None

def generate_specific_content_pieces(ideas: List[ContentIdea], original_transcript: str, video_url: str, style_preset: Optional[str] = None, custom_style: Optional[Dict[str, Any]] = None, content_config: Optional[Dict[str, Any]] = None) -> GeneratedContentList:
    """Generate specific content pieces with optional style customization and configurable limits"""
    generated_pieces = []
    video_id = extract_video_id(video_url) or "unknown"
    
    # Update field limits if provided in content_config
    if content_config and 'field_limits' in content_config:
        update_field_limits(content_config['field_limits'])
    
    # Create dynamic style text based on parameters
    if custom_style:
        style_text = f"""
        "Target Audience: {custom_style.get('target_audience', 'general audience')}"
        "Call To Action: {custom_style.get('call_to_action', 'engage with our content')}"
        "Content Goal: {custom_style.get('content_goal', 'engagement')}"
        "Language: {custom_style.get('language', 'English')}"
        "Tone: {custom_style.get('tone', 'Professional')}"
        """
        if custom_style.get('additional_instructions'):
            style_text += f'"Additional Instructions: {custom_style["additional_instructions"]}"'
    elif style_preset:
        if style_preset == "ecommerce_entrepreneur":
            style_text = CONTENT_STYLE
        else:
            style_text = """
            "Target Audience: general audience interested in the topic"
            "Call To Action: engage with our content and follow for more"
            "Content Goal: education, engagement"
            "Language: English"
            "Tone: Professional and engaging"
            """
    else:
        style_text = CONTENT_STYLE
    
    # Use the dynamic prompt generator with configurable limits
    dynamic_system_prompt = get_system_prompt_generate_content(style_text)
    
    for i, idea in enumerate(ideas, start=1):
        content_id = f"{video_id}_{i:03d}"
        console.log(f"Generating piece {i}/{len(ideas)}: '{idea.suggested_title}' (type: {idea.suggested_content_type})")
        user_prompt = f"""Generate a complete content piece based on the following idea from video '{video_url}'.
Adhere strictly to the JSON schema for the '{idea.suggested_content_type}'.

Content Idea: {json.dumps(idea.model_dump(), indent=2)}

Full Transcript (for context):
{original_transcript}
"""
        raw_content = content_generator.generate_content(dynamic_system_prompt, user_prompt)
        if not raw_content:
            console.log(f"[red]Failed to generate content for idea '{idea.suggested_title}'.[/red]")
            continue
        
        raw_content['content_id'] = content_id
        try:
            content_type = raw_content.get('content_type')
            if content_type == ContentType.REEL.value: piece = Reel(**raw_content)
            elif content_type == ContentType.IMAGE_CAROUSEL.value: piece = ImageCarousel(**raw_content)
            elif content_type == ContentType.TWEET.value: piece = Tweet(**raw_content)
            else:
                console.log(f"[red]Generated content has unknown type: '{content_type}'.[/red]")
                continue
            generated_pieces.append(piece)
        except ValidationError as e:
            console.log(f"[yellow]Initial validation failed for content '{idea.suggested_title}': {e}[/yellow]")
            
            # Attempt to fix validation errors
            fixed_content = fix_validation_errors(raw_content, e, idea, original_transcript, video_url, dynamic_system_prompt)
            
            if fixed_content:
                try:
                    content_type = fixed_content.get('content_type')
                    if content_type == ContentType.REEL.value: piece = Reel(**fixed_content)
                    elif content_type == ContentType.IMAGE_CAROUSEL.value: piece = ImageCarousel(**fixed_content)
                    elif content_type == ContentType.TWEET.value: piece = Tweet(**fixed_content)
                    else:
                        console.log(f"[red]Fixed content has unknown type: '{content_type}'.[/red]")
                        continue
                    generated_pieces.append(piece)
                    console.log(f"[green]✅ Successfully recovered content piece '{idea.suggested_title}'[/green]")
                except ValidationError as final_error:
                    console.log(f"[red]❌ Final validation failed for '{idea.suggested_title}': {final_error}[/red]")
                    logger.error(f"Final validation failed for {content_id}: {final_error}")
            else:
                console.log(f"[red]❌ Unable to fix validation errors for '{idea.suggested_title}' - content piece discarded[/red]")
                logger.error(f"Unable to fix validation errors for {content_id}: {e}")
            
    return GeneratedContentList(pieces=generated_pieces)

def save_carousel_metadata(carousel: ImageCarousel, titles_csv_path: str, video_url: str):
    try:
        file_exists = os.path.isfile(titles_csv_path)
        with open(titles_csv_path, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ["Content ID", "Video URL", "Title", "Caption", "Hashtags", "Slides Count"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists: writer.writeheader()
            writer.writerow({
                "Content ID": carousel.content_id, "Video URL": video_url, "Title": carousel.title,
                "Caption": carousel.caption, "Hashtags": " ".join(carousel.hashtags or []), "Slides Count": len(carousel.slides)
            })
    except Exception as e:
        console.log(f"[red]Error saving carousel metadata for {carousel.content_id}: {e}[/red]")

def save_carousel_slides(carousel: ImageCarousel, slides_dir: str):
    if not carousel.slides: return
    slides_csv_path = os.path.join(slides_dir, f"{carousel.content_id}_slides.csv")
    try:
        with open(slides_csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["slide_number", "step_number" , "step_heading" , "text"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for slide in carousel.slides:
                writer.writerow(slide.model_dump())
        console.log(f"  -> Saved slides to [cyan]{os.path.basename(slides_csv_path)}[/cyan]")
    except Exception as e:
        console.log(f"[red]Error saving slides for {carousel.content_id}: {e}[/red]")

def save_other_content_to_csv(other_pieces: List[Union[Reel, Tweet]], output_csv_path: str, video_url: str, video_title: str):
    if not other_pieces: return
    try:
        file_exists = os.path.isfile(output_csv_path)
        with open(output_csv_path, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ["Video URL", "Video Title", "Content ID", "Content Type", "Title", "Generated Content JSON"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists: writer.writeheader()
            for piece in other_pieces:
                writer.writerow({
                    "Video URL": video_url, "Video Title": video_title, "Content ID": piece.content_id,
                    "Content Type": piece.content_type.value, "Title": piece.title, "Generated Content JSON": piece.model_dump_json()
                })
        console.log(f"Saved {len(other_pieces)} other content piece(s) to [cyan]{os.path.basename(output_csv_path)}[/cyan]")
    except Exception as e:
        console.log(f"[red]Failed to save other content to CSV: {e}[/red]")

def parse_input_source(input_source: str) -> List[dict]:
    """
    Parse input source and return list of sources (videos or documents)
    Returns list of dicts: {"type": "video"|"document", "value": video_id|file_path, "name": display_name}
    """
    sources = []
    
    if os.path.isfile(input_source):
        ext = os.path.splitext(input_source)[1].lower()
        
        # Check if it's a document file that should be processed directly
        if DocumentParser.is_supported(input_source):
            console.log(f"📄 Document file detected: [cyan]{input_source}[/cyan]")
            sources.append({
                "type": "document",
                "value": input_source,
                "name": os.path.basename(input_source)
            })
            return sources
        
        # Otherwise, it's a list file (CSV/TXT) containing video IDs
        console.log(f"📄 Reading video list from: [cyan]{input_source}[/cyan]")
        try:
            if ext == '.csv':
                df = pd.read_csv(input_source, dtype=str, keep_default_na=False)
                col = 'video_id' if 'video_id' in df.columns else 'video_url'
                for item in df[col].dropna():
                    vid = extract_video_id(item)
                    if vid:
                        sources.append({
                            "type": "video",
                            "value": vid,
                            "name": vid
                        })
            elif ext == '.txt':
                with open(input_source, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        vid = extract_video_id(line)
                        if vid:
                            sources.append({
                                "type": "video",
                                "value": vid,
                                "name": vid
                            })
        except Exception as e:
            console.log(f"[red]Error reading file {input_source}: {e}[/red]")
    else:
        # Command-line argument (comma-separated video IDs/URLs)
        console.log("⌨️  Reading from command-line argument")
        for item in input_source.split(','):
            item = item.strip()
            if not item:
                continue
            vid = extract_video_id(item)
            if vid:
                sources.append({
                    "type": "video",
                    "value": vid,
                    "name": vid
                })
    
    # Remove duplicates while preserving order
    seen = set()
    unique_sources = []
    for source in sources:
        key = (source["type"], source["value"])
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)
    
    return unique_sources

def process_sources(sources: List[dict], content_config: Optional[Dict[str, Any]] = None):
    """Process both video and document sources with optional configuration"""
    if not sources:
        console.log("[yellow]⚠ No sources found to process.[/yellow]")
        return
    
    summary = {"reels": 0, "tweets": 0, "carousels": 0}

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(),
        TaskProgressColumn(), TextColumn("[{task.completed}/{task.total}]"), TimeElapsedColumn(),
        console=console, transient=True
    ) as progress:
        main_task = progress.add_task("[cyan]Processing sources...[/]", total=len(sources))
        for idx, source in enumerate(sources, 1):
            source_type = source["type"]
            source_value = source["value"]
            source_name = source["name"]
            
            console.print()
            console.rule(f"[bold]Source {idx}/{len(sources)}[/]", style="dim")
            
            # Handle based on type
            if source_type == "document":
                # Process document
                console.log(f"📄 Document: [bold]{source_name}[/]")
                progress.update(main_task, description=f"[{idx}/{len(sources)}] {source_name[:30]}...")
                
                try:
                    # Extract text from document
                    console.log(f"[cyan]📖[/] Parsing document...")
                    text, format_name = DocumentParser.parse_document(source_value)
                    
                    console.log(f"[green]✓[/] Extracted {len(text)} characters from {format_name}")
                    
                    # Use document text instead of transcript
                    transcript_text = text
                    video_title = source_name
                    video_url = f"document://{source_name}"
                    
                except Exception as e:
                    logger.error(f"Error parsing document {source_value}: {e}")
                    console.log(f"[red]✗[/] Failed to parse document: {str(e)[:100]}")
                    progress.update(main_task, advance=1)
                    continue
                    
            else:  # video
                # Process YouTube video
                video_id = source_value
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                console.log(f"🎥 Video ID: [bold]{video_id}[/]")
                
                try:
                    video_title = get_video_title(video_id)
                    if video_title:
                        console.log(f"📝 Title: [bold]{video_title[:60]}{'...' if len(video_title) > 60 else ''}[/]")
                        progress.update(main_task, description=f"[{idx}/{len(sources)}] {video_title[:30]}...")
                    else:
                        console.log(f"[dim]Title not available[/]")
                        video_title = video_id
                        progress.update(main_task, description=f"[{idx}/{len(sources)}] {video_id}")
                except Exception as e:
                    console.log(f"[yellow]⚠[/] Could not fetch title: {str(e)[:50]}")
                    video_title = video_id
                    progress.update(main_task, description=f"[{idx}/{len(sources)}] {video_id}")
            
            # Get transcript/text only for videos (already have text for documents)
            if source_type == "video":
                try:
                    # Use enhanced transcript service with preferences
                    preferences = TranscriptPreferences(
                        prefer_manual=True,
                        require_english=False,  # Allow non-English transcripts
                        enable_translation=True,
                        fallback_languages=["en", "es", "fr", "de", "hi", "ur"]
                    )
                    
                    result = get_english_transcript(video_id, preferences)
                    
                    if result:
                        transcript_text = result.transcript_text
                        
                        # Show transcript info
                        lang_info = f"{result.language} ({result.language_code})"
                        if result.is_translated:
                            lang_info = f"Translated from {lang_info}"
                        if result.is_generated:
                            lang_info += " [auto-generated]"
                        
                        console.log(f"[green]✓[/] Transcript: {lang_info} - {len(transcript_text)} chars")
                        
                        # Show processing notes if any
                        if result.processing_notes:
                            for note in result.processing_notes:
                                if "YouTube translation failed" in note or "original" in note.lower():
                                    console.log(f"  [yellow]ℹ[/] {note}")
                    else:
                        transcript_text = None
                        
                except Exception as e:
                    logger.error(f"Error fetching transcript for {video_id}: {e}")
                    console.log(f"[red]✗[/] Failed to get transcript: {str(e)[:100]}")
                    transcript_text = None
                    
                if not transcript_text or len(transcript_text) < 50:
                    console.log(f"[yellow]⚠[/] Transcript is empty or too short. Skipping.")
                    progress.update(main_task, advance=1)
                    continue
            
            # Validate text content (applies to both videos and documents)
            if not transcript_text or len(transcript_text) < 50:
                console.log(f"[yellow]⚠[/] Content is empty or too short. Skipping.")
                progress.update(main_task, advance=1)
                continue
            
            console.log(f"[cyan]💡[/] Generating content ideas...")
            raw_ideas = generate_content_ideas(transcript_text, content_config=content_config)
            if not raw_ideas:
                console.log(f"[yellow]⚠[/] No ideas generated for {video_id}")
                progress.update(main_task, advance=1)
                continue
            
            try:
                validated_ideas = GeneratedIdeas(ideas=raw_ideas).ideas
                console.log(f"[green]✓[/] Generated {len(validated_ideas)} content idea(s)")
            except ValidationError as e:
                console.log(f"[red]✗[/] Failed to validate ideas: {str(e)[:80]}...")
                progress.update(main_task, advance=1)
                continue

            console.log(f"[cyan]✨[/] Creating content pieces...")
            all_pieces = generate_specific_content_pieces(validated_ideas, transcript_text, video_url, content_config=content_config).pieces
            if not all_pieces:
                console.log(f"[yellow]⚠[/] No content pieces generated")
                progress.update(main_task, advance=1)
                continue

            carousels = [p for p in all_pieces if isinstance(p, ImageCarousel)]
            others = [p for p in all_pieces if not isinstance(p, ImageCarousel)]
            
            pieces_summary = []
            if carousels:
                pieces_summary.append(f"{len(carousels)} carousel(s)")
            reels_count = sum(1 for p in others if isinstance(p, Reel))
            tweets_count = sum(1 for p in others if isinstance(p, Tweet))
            if reels_count:
                pieces_summary.append(f"{reels_count} reel(s)")
            if tweets_count:
                pieces_summary.append(f"{tweets_count} tweet(s)")
            
            console.log(f"[green]✓[/] Created: {', '.join(pieces_summary)}")
            
            if carousels:
                titles_csv = os.path.join(CAROUSELS_DIR, f"{video_id}_carousel_titles.csv")
                for carousel in carousels:
                    save_carousel_metadata(carousel, titles_csv, video_url)
                for carousel in carousels:
                    save_carousel_slides(carousel, SLIDES_DIR)
                summary["carousels"] += len(carousels)
                console.log(f"  [dim]└─[/] Saved carousel metadata & slides")
                
            if others:
                save_other_content_to_csv(others, GENERATED_CONTENT_CSV, video_url, video_title)
                summary["reels"] += reels_count
                summary["tweets"] += tweets_count
                console.log(f"  [dim]└─[/] Saved content to CSV")

            progress.update(main_task, advance=1)

    console.print()
    console.rule("[bold green]✓ Processing Complete[/]", style="green")
    console.print()
    
    total_content = summary['reels'] + summary['tweets'] + summary['carousels']
    
    if total_content > 0:
        console.print("📊 [bold]Generated Content:[/]")
        if summary['reels'] > 0:
            console.print(f"   🎬 [bold blue]{summary['reels']}[/] Reel(s)")
        if summary['tweets'] > 0:
            console.print(f"   🐦 [bold cyan]{summary['tweets']}[/] Tweet(s)")
        if summary['carousels'] > 0:
            console.print(f"   🖼️  [bold magenta]{summary['carousels']}[/] Image Carousel(s)")
        
        console.print()
        console.print(f"📁 All files saved to: [cyan]{os.path.abspath(OUTPUT_DIR)}[/]")
    else:
        console.print("[yellow]⚠ No content was generated[/]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🎬 Content Repurposing Tool - Generate social media content from videos & documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single video (uses enhanced defaults: 800 char slides)
  python repurpose.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  
  # Multiple videos
  python repurpose.py "dQw4w9WgXcQ,jNQXAC9IVRw"
  
  # Document file (TXT, MD, DOCX, PDF)
  python repurpose.py article.pdf
  python repurpose.py notes.md
  
  # Video list from file
  python repurpose.py videos.txt
  
  # Limit processing
  python repurpose.py videos.csv -l 5
  
  # Custom configuration: longer carousel slides
  python repurpose.py video.txt --carousel-text-max 1000
  
  # More slides per carousel
  python repurpose.py video.txt --carousel-slides-max 12
  
  # Generate more content ideas
  python repurpose.py video.txt --min-ideas 10 --max-ideas 15
  
  # Show current configuration
  python repurpose.py --show-config
        """
    )
    parser.add_argument("input_source", nargs='?', help="Video URLs/IDs, document file (.txt/.md/.docx/.pdf), or list file")
    parser.add_argument("-l", "--limit", type=int, metavar="N", help="Process only first N videos")
    
    # Configuration options
    config_group = parser.add_argument_group('Configuration Options', 'Customize content generation settings')
    config_group.add_argument("--carousel-text-max", type=int, metavar="N", 
                            help=f"Max chars per carousel slide text (default: {DEFAULT_FIELD_LIMITS['carousel_slide_text_max']})")
    config_group.add_argument("--carousel-slides-min", type=int, metavar="N",
                            help=f"Min slides per carousel (default: {DEFAULT_FIELD_LIMITS['carousel_min_slides']})")
    config_group.add_argument("--carousel-slides-max", type=int, metavar="N",
                            help=f"Max slides per carousel (default: {DEFAULT_FIELD_LIMITS['carousel_max_slides']})")
    config_group.add_argument("--min-ideas", type=int, metavar="N",
                            help="Min content ideas to generate (default: 6)")
    config_group.add_argument("--max-ideas", type=int, metavar="N",
                            help="Max content ideas to generate (default: 8)")
    config_group.add_argument("--show-config", action="store_true",
                            help="Show current configuration and exit")
    
    args = parser.parse_args()
    
    # Check if input_source is required
    if not args.show_config and not args.input_source:
        parser.error("input_source is required unless --show-config is used")
    
    # Handle show-config option
    if args.show_config:
        console.print("[bold]Current Configuration:[/]")
        console.print()
        console.print("[bold cyan]Carousel Settings:[/]")
        console.print(f"  Slide Text Max:  {CURRENT_FIELD_LIMITS['carousel_slide_text_max']} chars")
        console.print(f"  Min Slides:      {CURRENT_FIELD_LIMITS['carousel_min_slides']}")
        console.print(f"  Max Slides:      {CURRENT_FIELD_LIMITS['carousel_max_slides']}")
        console.print()
        console.print("[bold cyan]Reel Settings:[/]")
        console.print(f"  Script Max:      {CURRENT_FIELD_LIMITS['reel_script_max']} chars")
        console.print(f"  Caption Max:     {CURRENT_FIELD_LIMITS['reel_caption_max']} chars")
        console.print()
        console.print("[bold cyan]Generation Settings:[/]")
        console.print(f"  Min Ideas:       6")
        console.print(f"  Max Ideas:       8")
        console.print()
        console.print("💡 [dim]Use --carousel-text-max, --carousel-slides-min, etc. to override[/]")
        sys.exit(0)
    
    # Build content config from CLI arguments
    cli_content_config = {}
    cli_field_limits = {}
    
    if args.carousel_text_max:
        cli_field_limits['carousel_slide_text_max'] = args.carousel_text_max
    if args.carousel_slides_min:
        cli_field_limits['carousel_min_slides'] = args.carousel_slides_min
    if args.carousel_slides_max:
        cli_field_limits['carousel_max_slides'] = args.carousel_slides_max
    
    if cli_field_limits:
        cli_content_config['field_limits'] = cli_field_limits
    
    if args.min_ideas:
        cli_content_config['min_ideas'] = args.min_ideas
    if args.max_ideas:
        cli_content_config['max_ideas'] = args.max_ideas

    console.rule("[bold blue]🎬 Content Repurposing Tool[/]", style="blue")
    console.print()
    console.print("📁 [bold]Output Directories:[/]")
    console.print(f"   └─ Content: [cyan]{os.path.abspath(GENERATED_CONTENT_CSV)}[/cyan]")
    console.print(f"   └─ Carousels: [cyan]{os.path.abspath(CAROUSELS_DIR)}[/cyan]")
    console.print(f"   └─ Slides: [cyan]{os.path.abspath(SLIDES_DIR)}[/cyan]")
    console.print()
    
    start_time = time.time()
    try:
        console.print("🔍 [bold]Parsing input...[/]")
        sources = parse_input_source(args.input_source)
        
        if not sources:
            console.print("[yellow]⚠ No sources found to process.[/]")
            sys.exit(0)
        
        # Count by type
        video_count = sum(1 for s in sources if s["type"] == "video")
        doc_count = sum(1 for s in sources if s["type"] == "document")
        
        if video_count and doc_count:
            console.print(f"✓ Found [bold green]{len(sources)}[/] sources: {video_count} video(s), {doc_count} document(s)")
        elif video_count:
            console.print(f"✓ Found [bold green]{video_count}[/] video(s)")
        else:
            console.print(f"✓ Found [bold green]{doc_count}[/] document(s)")
        
        if args.limit is not None:
            sources = sources[:args.limit]
            console.print(f"⚙️  Limiting to first [yellow]{len(sources)}[/] source(s)")
        
        # Show configuration if custom settings provided
        if cli_content_config:
            console.print()
            console.print("⚙️  [bold]Custom Configuration:[/]")
            if 'field_limits' in cli_content_config:
                for key, value in cli_content_config['field_limits'].items():
                    console.print(f"   • {key}: {value}")
            if 'min_ideas' in cli_content_config:
                console.print(f"   • min_ideas: {cli_content_config['min_ideas']}")
            if 'max_ideas' in cli_content_config:
                console.print(f"   • max_ideas: {cli_content_config['max_ideas']}")
        
        console.print()
        console.rule("[dim]Starting Processing[/]", style="dim")
        console.print()
        
        process_sources(sources, content_config=cli_content_config if cli_content_config else None)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠ Interrupted by user[/]")
        logger.info("Script interrupted by user (Ctrl+C)")
    except Exception as e:
        console.print(f"\n[bold red]❌ Critical error: {e}[/bold red]")
        logger.critical("Critical unhandled error during script execution.", exc_info=True)
        sys.exit(1)
    finally:
        duration = time.time() - start_time
        console.print()
        console.rule(style="dim")
        console.print(f"[bold green]✓[/] Completed in [cyan]{duration:.2f}s[/]")
        console.rule("[bold blue]🏁 Finished[/]", style="blue")