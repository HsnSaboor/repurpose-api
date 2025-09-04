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
from core.services.transcript_service import get_transcript_text
from core.services.content_service import ContentGenerator, ContentIdea
from core.services.video_service import get_video_title

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

class CarouselSlide(BaseModel):
    slide_number: int
    step_number: int = Field(..., description="Step number in the carousel.")
    step_heading : str = Field(..., max_length=100, description="Heading for this step.")
    text: str = Field(None, max_length=300, description="text content for the slide.")

class Reel(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.REEL] = ContentType.REEL
    title: str = Field(..., max_length=100)
    caption: str = Field(None, max_length=300)
    hook: str = Field(..., description="Attention-grabbing hook.")
    script_body: str = Field(..., description="Main script content.")
    visual_suggestions: Optional[str] = Field(None)
    hashtags: List[str] = Field(None)

class ImageCarousel(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.IMAGE_CAROUSEL] = ContentType.IMAGE_CAROUSEL
    title: str = Field(..., max_length=100)
    caption: str = Field(None, max_length=300)
    slides: List[CarouselSlide] = Field(..., min_length=4)
    hashtags: List[str] = Field(None)

class Tweet(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.TWEET] = ContentType.TWEET
    title: str = Field(..., max_length=100)
    tweet_text: str = Field(..., max_length=280)
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

# --- FIX: RESTORED EXPLICIT JSON STRUCTURE TO THE PROMPT ---
SYSTEM_PROMPT_GENERATE_IDEAS = f"""
You are an expert AI assistant specializing in analyzing video transcripts to identify diverse, repurposable content ideas.
Your goal is to analyze the provided transcript and suggest several distinct content ideas (Reels, Image Carousels, Tweets).

Output Format:
You MUST return a single JSON object. This object must have a single key named "ideas".
You are not limited to just one idea per type — generate as many as the transcript allows. Use your judgment to decide.
The value for "ideas" must be a list of JSON objects. Each object in the list represents one content idea and MUST have the following structure:
{{
  "suggested_content_type": "<'reel'|'image_carousel'|'tweet'>",
  "suggested_title": "<string, a catchy and relevant title for the content>",
  "relevant_transcript_snippet": "<string, a short, direct quote from the transcript that inspired this idea>",
  "type_specific_suggestions": {{}}
}}

Content Style to Follow:
{CONTENT_STYLE}
"""

# --- FIX: MADE THE SYSTEM PROMPT FOR CONTENT GENERATION HYPER-EXPLICIT ---
SYSTEM_PROMPT_GENERATE_CONTENT =f"""
You are an expert AI content creator. Your task is to take a specific content idea and generate the full content piece.
You MUST follow the JSON schema for the requested `content_type` with absolute precision. All required fields MUST be included.

**Content Type Schemas:**

If `content_type` is "reel", the JSON MUST look like this:
```json
{{
  "content_type": "reel",
  "title": "<string, the title for the reel>",
  "caption": "<string, a short, engaging caption, max 300 chars>",
  "hook": "<string, a strong, attention-grabbing opening line, required>",
  "script_body": "<string, the main script for the reel, required>",
  "visual_suggestions": "<string, optional suggestions for visuals>",
  "hashtags": ["<list of relevant string hashtags>"]
}}


If content_type is "image_carousel", the JSON MUST look like this:
      
{{
  "content_type": "image_carousel",
  "title": "<string, the title for the carousel>",
  "caption": "<string, a short, engaging caption>",
  "slides": [
    {{
      "slide_number": 1,
      "step_number": 1,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }},
    {{
      "slide_number": 2,
      "step_number": 2,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }},
    {{
      "slide_number": 3,
      "step_number": 3,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }},
    {{
      "slide_number": 4,
      "step_number": 4,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }}
  ],
  "hashtags": ["<list of relevant string hashtags>"]
}}


If content_type is "tweet", the JSON MUST look like this:
      
{{
  "content_type": "tweet",
  "title": "<string, an internal title for the tweet>",
  "tweet_text": "<string, the main tweet content, max 280 chars, required>",
  "thread_continuation": ["<list of optional strings for a follow-up thread>"],
  "hashtags": ["<list of relevant string hashtags>"]
}}


MANDATORY INSTRUCTIONS:

    For an image_carousel, you MUST generate at least 4 slides.

    Stirctly Follow the Language Constraint in {CONTENT_STYLE}.

    Your entire output must be a single, valid JSON object that matches one of the schemas above.

    Do NOT include content_id in your response.

    The generated text must strictly follow this style: {CONTENT_STYLE}
"""

def generate_content_ideas(transcript: str, style_preset: Optional[str] = None, custom_style: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
    """Generate content ideas with optional style customization"""
    # Import get_content_style_prompt from main.py to avoid circular imports
    # We'll construct the style prompt here to avoid import issues
    
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
        # Use default styles or preset-specific content
        if style_preset == "ecommerce_entrepreneur":
            style_text = CONTENT_STYLE  # Use the existing Roman Urdu style
        else:
            # For other presets, we'll use a generic style (could be expanded)
            style_text = """
            "Target Audience: general audience interested in the topic"
            "Call To Action: engage with our content and follow for more"
            "Content Goal: education, engagement"
            "Language: English"
            "Tone: Professional and engaging"
            """
    else:
        # Default to the original style
        style_text = CONTENT_STYLE
    
    # Create dynamic system prompt with the selected style
    dynamic_system_prompt = f"""
You are an expert AI assistant specializing in analyzing video transcripts to identify diverse, repurposable content ideas.
Your goal is to analyze the provided transcript and suggest several distinct content ideas (Reels, Image Carousels, Tweets).

Output Format:
You MUST return a single JSON object. This object must have a single key named "ideas".
You are not limited to just one idea per type — generate as many as the transcript allows. Use your judgment to decide.
The value for "ideas" must be a list of JSON objects. Each object in the list represents one content idea and MUST have the following structure:
{{
  "suggested_content_type": "<'reel'|'image_carousel'|'tweet'>",
  "suggested_title": "<string, a catchy and relevant title for the content>",
  "relevant_transcript_snippet": "<string, a short, direct quote from the transcript that inspired this idea>",
  "type_specific_suggestions": {{}}
}}

Content Style to Follow:
{style_text}
"""
    
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
    
    # Create a system prompt for diff-based editing
    edit_system_prompt = f"""
You are an expert content editor specializing in precise, diff-based editing of social media content.
Your task is to make ONLY the specific changes requested by the user while preserving everything else.

**CRITICAL INSTRUCTIONS:**
1. Make ONLY the changes explicitly requested in the edit prompt
2. Preserve all other content exactly as it was
3. Ensure the edited content still meets all validation requirements:
   - caption: Maximum 300 characters
   - title: Maximum 100 characters  
   - tweet_text: Maximum 280 characters (for tweets)
   - step_heading: Maximum 100 characters (for carousel slides)
   - slide text: Maximum 300 characters (for carousel slides)

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
        
        # Create a specific prompt to fix the validation issues
        fix_prompt = f"""The previously generated content failed validation with these specific errors:

{chr(10).join(error_details)}

Please regenerate the content for '{idea.suggested_content_type}' type, ensuring ALL validation requirements are met:

**CRITICAL REQUIREMENTS:**
- caption: Must be 300 characters or less
- title: Must be 100 characters or less
- tweet_text: Must be 280 characters or less (for tweets)
- step_heading: Must be 100 characters or less (for carousel slides)
- slide text: Must be 300 characters or less (for carousel slides)

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

def generate_specific_content_pieces(ideas: List[ContentIdea], original_transcript: str, video_url: str, style_preset: Optional[str] = None, custom_style: Optional[Dict[str, Any]] = None) -> GeneratedContentList:
    """Generate specific content pieces with optional style customization"""
    generated_pieces = []
    video_id = extract_video_id(video_url) or "unknown"
    
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
        # Use default styles or preset-specific content
        if style_preset == "ecommerce_entrepreneur":
            style_text = CONTENT_STYLE  # Use the existing Roman Urdu style
        else:
            # For other presets, we'll use a generic style (could be expanded)
            style_text = """
            "Target Audience: general audience interested in the topic"
            "Call To Action: engage with our content and follow for more"
            "Content Goal: education, engagement"
            "Language: English"
            "Tone: Professional and engaging"
            """
    else:
        # Default to the original style
        style_text = CONTENT_STYLE
    
    # Create dynamic system prompt with the selected style
    dynamic_system_prompt = f"""
You are an expert AI content creator. Your task is to take a specific content idea and generate the full content piece.
You MUST follow the JSON schema for the requested `content_type` with absolute precision. All required fields MUST be included.

**Content Type Schemas:**

If `content_type` is "reel", the JSON MUST look like this:
```json
{{
  "content_type": "reel",
  "title": "<string, the title for the reel>",
  "caption": "<string, a short, engaging caption, max 300 chars>",
  "hook": "<string, a strong, attention-grabbing opening line, required>",
  "script_body": "<string, the main script for the reel, required>",
  "visual_suggestions": "<string, optional suggestions for visuals>",
  "hashtags": ["<list of relevant string hashtags>"]
}}


If content_type is "image_carousel", the JSON MUST look like this:
      
{{
  "content_type": "image_carousel",
  "title": "<string, the title for the carousel>",
  "caption": "<string, a short, engaging caption>",
  "slides": [
    {{
      "slide_number": 1,
      "step_number": 1,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }},
    {{
      "slide_number": 2,
      "step_number": 2,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }},
    {{
      "slide_number": 3,
      "step_number": 3,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }},
    {{
      "slide_number": 4,
      "step_number": 4,
      "step_heading": "<string, the heading for this step, max 100 chars>",
      "text": "<text string, the text to display on this slide dont add heading or step_number here, only text>"
    }}
  ],
  "hashtags": ["<list of relevant string hashtags>"]
}}


If content_type is "tweet", the JSON MUST look like this:
      
{{
  "content_type": "tweet",
  "title": "<string, an internal title for the tweet>",
  "tweet_text": "<string, the main tweet content, max 280 chars, required>",
  "thread_continuation": ["<list of optional strings for a follow-up thread>"],
  "hashtags": ["<list of relevant string hashtags>"]
}}


MANDATORY INSTRUCTIONS:

    For an image_carousel, you MUST generate at least 4 slides.

    Strictly Follow the Language Constraint in the style below.

    Your entire output must be a single, valid JSON object that matches one of the schemas above.

    Do NOT include content_id in your response.

    The generated text must strictly follow this style: {style_text}
"""
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

def parse_input_source(input_source: str) -> List[str]:
    video_ids = set()
    if os.path.isfile(input_source):
        console.log(f":page_facing_up: Reading from file: [cyan]{input_source}[/cyan]")
        ext = os.path.splitext(input_source)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(input_source, dtype=str, keep_default_na=False)
                col = 'video_id' if 'video_id' in df.columns else 'video_url'
                for item in df[col].dropna():
                    vid = extract_video_id(item)
                    if vid: video_ids.add(vid)
            elif ext == '.txt':
                with open(input_source, 'r', encoding='utf-8') as f:
                    for line in f:
                        vid = extract_video_id(line.strip())
                        if vid: video_ids.add(vid)
        except Exception as e:
            console.log(f"[red]Error reading file {input_source}: {e}[/red]")
    else:
        console.log(":keyboard: Reading from command-line argument.")
        for item in input_source.split(','):
            vid = extract_video_id(item.strip())
            if vid: video_ids.add(vid)
    return list(video_ids)

def process_videos(video_ids: List[str]):
    if not video_ids:
        console.log("[yellow]No valid video IDs found to process.[/yellow]")
        return
    
    summary = {"reels": 0, "tweets": 0, "carousels": 0}

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(),
        TaskProgressColumn(), TextColumn("[{task.completed}/{task.total}]"), TimeElapsedColumn(),
        console=console, transient=True
    ) as progress:
        main_task = progress.add_task("[cyan]Processing videos...[/]", total=len(video_ids))
        for video_id in video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_title = get_video_title(video_id) or video_id
            progress.update(main_task, description=f"Processing '{video_title[:35]}...'")
            
            try:
                transcript_text = get_transcript_text(video_id)
            except Exception as e:
                logger.error(f"Error fetching transcript for {video_id}: {e}")
                transcript_text = None
            if not transcript_text or len(transcript_text) < 50:
                console.log(f"[yellow]Transcript for {video_id} is empty or too short. Skipping.[/yellow]")
                progress.update(main_task, advance=1)
                continue
            
            raw_ideas = generate_content_ideas(transcript_text)
            if not raw_ideas:
                # console.log is already called inside generate_content_ideas
                progress.update(main_task, advance=1)
                continue
            
            try:
                validated_ideas = GeneratedIdeas(ideas=raw_ideas).ideas
            except ValidationError as e:
                console.log(f"[red]Failed to validate ideas for {video_id}: {e}[/red]")
                progress.update(main_task, advance=1)
                continue

            all_pieces = generate_specific_content_pieces(validated_ideas, transcript_text, video_url).pieces
            if not all_pieces:
                console.log(f"[yellow]No valid content pieces were generated for {video_id}.[/yellow]")
                progress.update(main_task, advance=1)
                continue

            carousels = [p for p in all_pieces if isinstance(p, ImageCarousel)]
            others = [p for p in all_pieces if not isinstance(p, ImageCarousel)]
            
            if carousels:
                titles_csv = os.path.join(CAROUSELS_DIR, f"{video_id}_carousel_titles.csv")
                console.log(f"Saving {len(carousels)} carousel(s) for [bold magenta]{video_id}[/bold magenta]:")
                for carousel in carousels:
                    save_carousel_metadata(carousel, titles_csv, video_url)
                console.log(f"  -> Saved metadata to [cyan]{os.path.basename(titles_csv)}[/cyan]")
                for carousel in carousels:
                    save_carousel_slides(carousel, SLIDES_DIR)
                summary["carousels"] += len(carousels)
                
            if others:
                save_other_content_to_csv(others, GENERATED_CONTENT_CSV, video_url, video_title)
                summary["reels"] += sum(1 for p in others if isinstance(p, Reel))
                summary["tweets"] += sum(1 for p in others if isinstance(p, Tweet))

            progress.update(main_task, advance=1)

    console.rule("[bold green]Processing Complete[/bold green]")
    console.print(f"Generated a total of:")
    console.print(f"  - [bold blue]{summary['reels']}[/bold blue] Reels")
    console.print(f"  - [bold cyan]{summary['tweets']}[/bold cyan] Tweets")
    console.print(f"  - [bold magenta]{summary['carousels']}[/bold magenta] Image Carousels")
    console.print(f"Check the '{OUTPUT_DIR}' directory for all generated files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate short-form content from YouTube videos.")
    parser.add_argument("input_source", help="Comma-separated URLs/IDs, or a path to a .txt/.csv file.")
    parser.add_argument("-l", "--limit", type=int, help="Maximum number of videos to process.")
    args = parser.parse_args()

    console.rule("[bold blue]YouTube Content Repurposing Script[/]", style="blue")
    console.print(f"Output (Other Content): [cyan]{os.path.abspath(GENERATED_CONTENT_CSV)}[/cyan]")
    console.print(f"Output (Carousels):     [cyan]{os.path.abspath(CAROUSELS_DIR)}[/cyan]")
    console.print(f"Output (Slides):        [cyan]{os.path.abspath(SLIDES_DIR)}[/cyan]")
    
    start_time = time.time()
    try:
        video_ids = parse_input_source(args.input_source)
        if args.limit is not None:
            video_ids = video_ids[:args.limit]
            console.print(f"Processing limit: [yellow]First {len(video_ids)} videos.[/yellow]")
        
        process_videos(video_ids)

    except Exception as e:
        console.print(f"\n[bold red]❌ Critical error: {e}[/bold red]")
        logger.critical("Critical unhandled error during script execution.", exc_info=True)
    finally:
        duration = time.time() - start_time
        console.print(f"\n[bold]🏁 Finished in {duration:.2f} seconds.[/bold]")
        console.rule(style="blue")