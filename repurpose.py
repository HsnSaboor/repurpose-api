# -*- coding: utf-8 -*-
"""YouTube Video Processor with Gemini AI Integration via OpenAI Compatibility Layer
Handles transcript processing, content generation (Ideas + Specific Pieces), and CSV/JSON export.
"""

from pydantic import BaseModel, ValidationError, Field
from typing import List, Optional, Dict, Any, Union, Literal
from openai import OpenAI
import json
import pandas as pd
import time
import threading
from datetime import datetime, timedelta
from collections import deque
import os
import csv
import argparse
import logging
from typing import Tuple , List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn # Keep for potential internal use or if functions use them
import re
from dotenv import load_dotenv
from logging import StreamHandler # Keep if logger setup is maintained
from enum import Enum
import sys # Keep if still used by any part of the module
import yt_dlp
from yt_dlp.utils import DownloadError

# Load environment variables from .env file
load_dotenv()

# --- Content Style Definition ---
CONTENT_STYLES: List[str] = [
    "problem_solution",
    "case_study",
    "how_to",
    "interesting_fact",
    "news_update",
    "inspirational_motivational",
    "educational_explainer",
    "storytelling_narrative",
    "comparison_analysis",
    "listicle_format",
    "controversial_opinion",
    "behind_the_scenes",
    "quick_tip_hack",
    "other",
]

# --- Pydantic Models ---
class ContentIdea(BaseModel):
    suggested_content_type: Literal["reel", "image_carousel", "tweet"] = Field(..., description="Type of content suggested.")
    suggested_title: str = Field(..., max_length=100, description="Suggested title for the content.")
    suggested_style: str = Field(..., description=f"Style from: {', '.join(CONTENT_STYLES)}")
    relevant_transcript_snippet: str = Field(..., description="Snippet from the transcript that inspired this idea.")
    type_specific_suggestions: Optional[Dict[str, Any]] = Field(None, description="Type-specific suggestions for the content.")
    # Optional fields for type-specific suggestions
    estimated_duration_seconds: Optional[int] = Field(None, description="Estimated duration in seconds (for reels).")
    num_slides_idea: Optional[int] = Field(None, description="Number of slides idea (for image carousels).")
    core_message_idea: Optional[str] = Field(None, max_length=280, description="Core message idea (for tweets).")
    # Add any other fields that are relevant to the content idea


class GeneratedIdeas(BaseModel):
    ideas: List[ContentIdea] = Field(..., description="A list of generated content ideas.")
    summary: Optional[str] = Field(None, description="An optional summary of all generated ideas.")


# --- Configuration ---
console = Console()
OUTPUT_DIR = "output"
GENERATED_CONTENT_CSV = os.path.join(OUTPUT_DIR, "generated_content.csv")
REPURPOSE_LOG_FILE = os.path.join(OUTPUT_DIR, 'repurpose.log')

os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    handlers=[
        logging.FileHandler(REPURPOSE_LOG_FILE),
    ]
)
logger = logging.getLogger(__name__)

if not any(isinstance(h, StreamHandler) for h in logging.getLogger().handlers):
    # If running as a module, stdout handler might be added by the main application
    # Consider if this is needed when imported or if main app handles root logger config
    if not any(isinstance(h, StreamHandler) for h in logging.getLogger().handlers) and logging.getLogger().name == '__main__':
        logging.getLogger().addHandler(StreamHandler(sys.stdout))

# --- Pydantic Models ---
class ContentType(str, Enum):
    REEL = "reel"
    IMAGE_CAROUSEL = "image_carousel"
    TWEET = "tweet"

class ReelSegment(BaseModel):
    text: str

class CarouselSlide(BaseModel):
    slide_number: int
    image_prompt: str = Field(..., description="AI image prompt.")
    text_overlay: str = Field(None, max_length=300, description="Optional text overlay for images.")

class Reel(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.REEL] = ContentType.REEL
    title: str = Field(..., max_length=100)
    caption: str = Field(None, max_length=300)
    style: str = Field(..., description=f"Style from: {', '.join(CONTENT_STYLES)}")
    hook: str = Field(..., description="Attention-grabbing hook.")
    script_body: str = Field(..., description="Main script content.")
    visual_suggestions: Optional[str] = Field(None)
    segments: Optional[List[ReelSegment]] = Field(None)
    total_duration_seconds: Optional[int] = Field(None)
    hashtags: List[str] = Field(None)

class ImageCarousel(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.IMAGE_CAROUSEL] = ContentType.IMAGE_CAROUSEL
    title: str = Field(..., max_length=100)
    caption: str = Field(None, max_length=300)
    style: str = Field(..., description=f"Style from: {', '.join(CONTENT_STYLES)}")
    slides: List[CarouselSlide] = Field(..., min_length=4)
    hashtags: List[str] = Field(None)

class Tweet(BaseModel):
    content_id: str = Field(..., description="Serial number for this content.")
    content_type: Literal[ContentType.TWEET] = ContentType.TWEET
    title: str = Field(..., max_length=100)
    style: str = Field(..., description=f"Style from: {', '.join(CONTENT_STYLES)}")
    tweet_text: str = Field(..., max_length=280)
    thread_continuation: Optional[List[str]] = Field(None)
    hashtags: List[str] = Field(None)

class GeneratedContentList(BaseModel):
    pieces: List[Union[Reel, ImageCarousel, Tweet]]

# --- Rate Limiter ---
class GeminiRateLimiter:
    def __init__(self, rpm_limit=60, qpd_limit=1500):
        self.rpm_limit = rpm_limit
        self.qpd_limit = qpd_limit
        self.request_times = deque()
        self.lock = threading.Lock()
        self.daily_count = 0
        self.last_reset_day = datetime.now().date()
        logger.info(f"Rate limiter initialized: RPM={rpm_limit}, QPD={qpd_limit}")

    def _cleanup_and_check_daily_reset(self):
        now = datetime.now()
        current_day = now.date()
        if current_day > self.last_reset_day:
            logger.info(f"New day detected. Resetting daily request count from {self.daily_count} to 0.")
            self.daily_count = 0
            self.last_reset_day = current_day

        one_minute_ago = now - timedelta(seconds=60)
        while self.request_times and self.request_times[0] < one_minute_ago:
            self.request_times.popleft()

    def wait_for_capacity(self):
        while True:
            with self.lock:
                self._cleanup_and_check_daily_reset()
                now = datetime.now()

                if self.daily_count >= self.qpd_limit:
                    logger.warning(f"Daily query limit ({self.qpd_limit}) reached. Waiting until next day.")
                    tomorrow = now.date() + timedelta(days=1)
                    wait_until = datetime.combine(tomorrow, datetime.min.time())
                    wait_duration = (wait_until - now).total_seconds()
                    wait_time = max(60.0, wait_duration)
                    logger.warning(f"Daily limit hit. Waiting for ~{wait_time/3600:.2f} hours.")

                elif len(self.request_times) >= self.rpm_limit:
                     oldest_request_time = self.request_times[0]
                     wait_until = oldest_request_time + timedelta(seconds=60.1)
                     wait_duration = (wait_until - now).total_seconds()
                     wait_time = max(0.1, wait_duration)
                     logger.warning(f"RPM limit ({self.rpm_limit}) reached. Waiting for {wait_time:.2f} seconds.")

                else:
                    self.request_times.append(now)
                    self.daily_count += 1
                    return

            time.sleep(wait_time)

# --- API Client Initialization ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.critical("GEMINI_API_KEY not found in environment variables. Exiting.")
    sys.exit("API key is missing. Please set GEMINI_API_KEY in your .env file.")

gemini_base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
gemini_model_name = "gemini-2.0-flash"

logger.info(f"Using Gemini model: {gemini_model_name} via Base URL: {gemini_base_url}")

try:
    client = OpenAI(
        api_key=api_key,
        base_url=gemini_base_url
    )
except Exception as e:
     logger.critical(f"Failed to initialize OpenAI client for Gemini: {e}. Exiting.")
     sys.exit(f"Failed to initialize API client: {e}")

rate_limiter = GeminiRateLimiter(
    rpm_limit=int(os.getenv("RPM_LIMIT", 60)),
    qpd_limit=int(os.getenv("QPD_LIMIT", 1500))
)

# --- Helper Functions ---
def extract_video_id(url: str) -> Optional[str]:
    if not isinstance(url, str):
        return None
    patterns = [
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
        r'^[a-zA-Z0-9_-]{11}$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_title(video_id: str) -> Optional[str]:
    """
    Fetches the title of a YouTube video given its ID.

    Args:
        video_id: The ID of the YouTube video.

    Returns:
        The title of the video as a string, or None if an error occurs.
    """
    if not video_id:
        logger.warning("get_video_title called with empty video_id.")
        return None

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'no_warnings': True, # Suppress warnings like "Skipping DASH manifest"
        'ignoreerrors': True # Ignore errors during extraction if possible
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            # ydl.extract_info can return None if ignoreerrors is True and an error occurs
            if info_dict:
                logging.info(f"yt-dlp info keys for {video_id}: {list(info_dict.keys()) if info_dict else 'None'}")
                if 'title' in info_dict:
                    title = info_dict.get('title')
                    if title:
                        logger.info(f"Successfully fetched title for video ID {video_id}: '{title}'")
                        return str(title)
                    else:
                        logger.warning(f"Title not found or empty in info_dict for video ID {video_id}. Info dict: {info_dict}")
                        return None
                else:
                    logger.warning(f"Could not extract title for video ID {video_id}. 'title' key missing. Info dict: {info_dict}")
                    return None
            else:
                logger.warning(f"Could not extract title for video ID {video_id}. info_dict is None.")
                return None
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"yt-dlp DownloadError for {video_id}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in get_video_title for {video_id}: {e}")
        return None

def call_gemini_api(system_prompt: str, user_prompt: str, client_instance: OpenAI, model_name: str) -> Optional[Dict[str, Any]]:
    rate_limiter.wait_for_capacity()
    try:
        response = client_instance.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            content_str = response.choices[0].message.content
            try:
                content_str = content_str.strip()
                if content_str.startswith("```json"):
                    content_str = content_str[7:-3].strip()
                elif content_str.startswith("```"):
                     content_str = content_str[3:].strip()
                     if content_str.endswith("```"):
                         content_str = content_str[:-3].strip()

                json_response = json.loads(content_str)
                return json_response
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {e}. Response string: '{content_str[:500]}...'")
                return None
        else:
            logger.error("No content found in LLM response or unexpected response structure.")
            return None
    except Exception as e:
        logger.error(f"Error during API call to {model_name}: {e}", exc_info=True)
        return None

# --- Content Generation Functions ---
SYSTEM_PROMPT_GENERATE_IDEAS = f"""
You are an expert AI assistant specializing in analyzing long-form video transcripts to identify diverse, repurposable content ideas.
Your goal is to analyze the provided transcript and suggest several distinct content ideas (Reels, Image Carousels, Tweets).
For each idea, provide a suggested title, content type, style, and a brief snippet from the transcript that inspired it.
Also include any type-specific suggestions like estimated duration for reels or number of slides for carousels.

Output Format:
Return a single JSON object with a key "ideas". The value of "ideas" should be a list of JSON objects, where each object represents a content idea. The structure for each idea dictionary should be like this:
{{
  "suggested_content_type": "<string: 'reel', 'image_carousel', or 'tweet'>",
  "suggested_title": "<string, catchy title idea, max 100 chars>",
  "suggested_style": "<string from the list of styles>",
  "relevant_transcript_snippet": "<string, a brief (1-3 sentence) direct quote or summary from transcript that inspired THIS specific idea>",
  "type_specific_suggestions": {{
    // Optional fields based on suggested_content_type
    "estimated_duration_seconds": <integer, 15-180> (if reel),
    "num_slides_idea": <integer, 4-10> (if image_carousel),
    "core_message_idea": "<string, max 280 chars, core point for tweet>" (if tweet)
  }}
}}

Content Styles to choose from:
{', '.join(CONTENT_STYLES)}

Instructions:
1. Analyze the transcript to find interesting points, stories, tips, etc.
2. Suggest 3-7 diverse content ideas.
3. For each idea, choose one suggested_content_type and one suggested_style.
4. Provide a relevant_transcript_snippet that grounds this idea in the original content.
5. Fill out type_specific_suggestions with relevant details.
6. Strictly follow the output format - do not add extra fields.
"""

SYSTEM_PROMPT_GENERATE_CONTENT =f"""
You are an expert AI content creator. Your task is to take a specific content idea and generate the full content piece according to the requested type.
You MUST adhere strictly to the JSON schema provided for the given content_type. Ensure ALL fields listed in the schema for that content_type are present in your JSON output.

MANDATORY REQUIREMENTS:
1. Your output MUST be a single JSON object.
2. Your output MUST contain a 'content_type' field indicating the type of content (reel/image_carousel/tweet).
3. The 'content_type' must EXACTLY match the idea's suggested_content_type.
4. Include ALL REQUIRED fields for the specified content type as shown in the schemas below. Optional fields can be included if relevant.
5. The 'style' field must be one of: {', '.join(CONTENT_STYLES)}.

Content Types and their target JSON Schemas:

Reel (content_type: "reel"):
{{
  "content_type": "reel",
  "title": "<string, max 100 chars>",
  "caption": "<string, max 100 chars>",
  "style": "<string from the provided list: {', '.join(CONTENT_STYLES)}>",
  "hook": "<string>",
  "script_body": "<string>",
  "visual_suggestions": "<optional string>",
  "segments": [ {{ "text": "<string>"}} ],
  "total_duration_seconds": <optional integer>,
  "hashtags": ["<string>", ...]
}}

Image Carousel (content_type: "image_carousel"):
{{
  "content_type": "image_carousel",
  "title": "<string, max 100 chars>",
  "caption": "<string, max 100 chars>",
  "style": "<string from the provided list: {', '.join(CONTENT_STYLES)}>",
  "slides": [
    {{
      "slide_number": <integer, sequential, starting from 1>,
      "image_prompt": "<detailed AI image prompt>",
      "text_overlay": "<string, max 500 chars>"
    }},
    // ... more slides (minimum 4 slides total)
  ],
  "hashtags": ["<string>", ...]
}}

Tweet (content_type: "tweet"):
{{
  "content_type": "tweet",
  "title": "<string, max 100 chars, for internal tracking/identification>",
  "style": "<string from the provided list: {', '.join(CONTENT_STYLES)}>",
  "tweet_text": "<string, max 280 chars>",
  "thread_continuation": ["<optional string>", ...],
  "hashtags": ["<string>", ...]
}}

FAILURE TO INCLUDE THE CORRECT CONTENT_TYPE AND ALL REQUIRED FIELDS FOR THAT TYPE WILL RESULT IN ERRORS.
Ensure 'style' is chosen from the provided list: {', '.join(CONTENT_STYLES)}.
The 'content_id' will be added programmatically by the script, do not include 'content_id' in your JSON response.
"""

def generate_content_ideas(transcript: str) -> Optional[List[Dict[str, Any]]]:
    """Generate content ideas from the full transcript."""
    logger.info("Generating content ideas from transcript.")
    if not transcript or len(transcript.strip()) < 50:
        logger.warning("Transcript too short or invalid. Skipping idea generation.")
        return None

    user_prompt = f"""Transcript:
{transcript}

Please analyze the transcript and generate content ideas based on the system prompt instructions.
"""
    logger.info(f"Calling Gemini API for idea generation. User prompt (first 500 chars): {user_prompt[:500]}")
    raw_response = call_gemini_api(SYSTEM_PROMPT_GENERATE_IDEAS, user_prompt, client, gemini_model_name)
    logger.info(f"Raw response from Gemini API for idea generation: {raw_response}")

    if not raw_response:
        logger.error("Failed to get any response from LLM for idea generation.")
        return None
    if 'ideas' not in raw_response or not isinstance(raw_response.get('ideas'), list):
        logger.error(f"LLM response for idea generation does not contain a valid list of ideas. Response: {raw_response}")
        return None

    logger.info(f"Successfully generated {len(raw_response['ideas'])} raw content ideas.")
    return raw_response['ideas']

def generate_specific_content_pieces(ideas: List[ContentIdea],
                                   original_transcript: str,
                                   video_url: str) -> GeneratedContentList:
    """Generate full content pieces from a list of ideas."""
    generated_pieces: List[Union[Reel, ImageCarousel, Tweet]] = []
    video_id_for_log = extract_video_id(video_url) or video_url
    logger.info(f"Starting generation of specific content pieces for {len(ideas)} ideas from video: {video_id_for_log}.")

    try:
        for i, idea in enumerate(ideas, start=1):
            content_id = f"{video_id_for_log}_{i:03d}"
            
            # Access Pydantic model attributes directly
            suggested_type = idea.suggested_content_type
            suggested_title = idea.suggested_title
            logger.info(f"Processing idea {i}/{len(ideas)}: '{suggested_title}' (type: {suggested_type})")

            # Prepare input for generation
            input_for_generation_json = {
                "content_idea_details": idea.dict(),  # Convert Pydantic model to dict for JSON serialization
                "original_video_url": video_url
            }

            user_prompt_text = f"""Please generate a complete content piece based on the following idea from video '{video_url}'.
Adhere strictly to the JSON schema for the 'suggested_content_type'.

Content Idea to Generate:
{json.dumps(input_for_generation_json, indent=2)}

Original Full Transcript (for broader context):
{original_transcript}
"""
            raw_content_response = call_gemini_api(SYSTEM_PROMPT_GENERATE_CONTENT, user_prompt_text, client, gemini_model_name)

            if not raw_content_response:
                logger.error(f"Failed to get content from LLM for idea '{suggested_title}' (Content ID: {content_id})")
                continue

            # Validate content_type from response
            content_type_value = raw_content_response.get('content_type')
            if not content_type_value or content_type_value not in {ct.value for ct in ContentType}:
                logger.error(f"Invalid content_type '{content_type_value}' for idea '{suggested_title}'")
                continue

            # Add generated content_id
            raw_content_response['content_id'] = content_id

            # Validate and default style if needed
            raw_style = raw_content_response.get('style', '')
            if raw_style not in CONTENT_STYLES:
                logger.warning(f"Invalid style '{raw_style}' for {content_id}. Defaulting to 'other'.")
                raw_content_response['style'] = 'other'

            try:
                piece: Union[Reel, ImageCarousel, Tweet]
                
                if content_type_value == ContentType.REEL.value:
                    # Handle segments data
                    segments_data = raw_content_response.get('segments')
                    if isinstance(segments_data, str):
                        try:
                            parsed_segments = json.loads(segments_data)
                            if isinstance(parsed_segments, list):
                                raw_content_response['segments'] = parsed_segments
                            else:
                                raw_content_response['segments'] = None
                        except json.JSONDecodeError:
                            raw_content_response['segments'] = None
                    elif not isinstance(segments_data, list):
                        raw_content_response['segments'] = None
                    
                    piece = Reel(**raw_content_response)
                    logger.info(f"Created Reel: {content_id}, Title: {piece.title}")

                elif content_type_value == ContentType.IMAGE_CAROUSEL.value:
                    slides_data = raw_content_response.get('slides')
                    if not isinstance(slides_data, list) or not all(isinstance(s, dict) for s in slides_data):
                        logger.error(f"Invalid slides format for {content_id}")
                        continue
                    piece = ImageCarousel(**raw_content_response)
                    logger.info(f"Created ImageCarousel: {content_id}, Title: {piece.title}")

                elif content_type_value == ContentType.TWEET.value:
                    piece = Tweet(**raw_content_response)
                    logger.info(f"Created Tweet: {content_id}, Title: {piece.title}")

                else:
                    logger.error(f"Unhandled content_type '{content_type_value}' for {content_id}")
                    continue

                generated_pieces.append(piece)

            except ValidationError as e:
                logger.error(f"Validation failed for {content_id}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error with {content_id}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in content generation process: {str(e)}", exc_info=True)

    logger.info(f"Completed generating {len(generated_pieces)} pieces for video: {video_id_for_log}")
    return GeneratedContentList(pieces=generated_pieces)

def save_generated_content_to_csv(all_pieces: GeneratedContentList, output_csv_path: str,
                                video_url: str):
    """Saves all generated content pieces to CSV with specified format."""
    try:
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        file_exists = os.path.isfile(output_csv_path)

        with open(output_csv_path, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Video URL", "Content Type", "Style", "Generated Content"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists or os.path.getsize(output_csv_path) == 0:
                writer.writeheader()

            if all_pieces.pieces:
                for piece in all_pieces.pieces:
                    content_data = piece.model_dump()
                    writer.writerow({
                        "Video URL": video_url,
                        "Content Type": piece.content_type.value,
                        "Style": piece.style,
                        "Generated Content": json.dumps(content_data, ensure_ascii=False)
                    })
                logger.info(f"Saved {len(all_pieces.pieces)} rows to {output_csv_path}")

    except Exception as e:
        logger.critical(f"CSV save failed: {str(e)[:500]}")
        raise

def process_csv_file(input_csv_path: str, output_csv_path: str, max_videos: Optional[int] = None):
    """Processes each video transcript from the input CSV."""
    logger.info(f"Starting processing of input CSV: {input_csv_path}")
    try:
        df = pd.read_csv(input_csv_path, dtype=str, keep_default_na=False, encoding='utf-8')
        logger.info(f"Successfully read {len(df)} rows from {input_csv_path}")
    except FileNotFoundError:
        logger.critical(f"Input CSV file not found: {input_csv_path}")
        console.print(f"[bold red]Error: Input CSV file not found: {input_csv_path}[/bold red]")
        return
    except Exception as e:
        logger.critical(f"Error reading input CSV {input_csv_path}: {e}", exc_info=True)
        console.print(f"[bold red]Error reading input CSV {input_csv_path}: {e}[/bold red]")
        return

    required_cols = ["Video URL", "Transcript"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
         logger.critical(f"Input CSV missing required columns: {missing_cols}. Exiting.")
         console.print(f"[bold red]Error: Input CSV missing required columns: {missing_cols}[/bold red]")
         return

    videos_to_process = df.to_dict('records')
    if not videos_to_process:
        logger.info(f"No videos found in {input_csv_path} to process.")
        return

    if max_videos is not None and max_videos >= 0:
        videos_to_process = videos_to_process[:max_videos]
        logger.info(f"Processing limit set. Will process {len(videos_to_process)} videos.")
    else:
        logger.info(f"No limit set. Processing all {len(videos_to_process)} videos found.")

    if not videos_to_process:
        logger.info("No videos to process after applying limit.")
        return

    videos_attempted_count = 0
    videos_with_ideas_count = 0
    videos_with_generated_pieces_count = 0
    total_ideas_suggested_count = 0
    total_pieces_generated_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[{task.completed}/{task.total}]"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
        refresh_per_second=2
    ) as progress:
        main_task = progress.add_task(
            "[cyan]Processing videos...[/]",
            total=len(videos_to_process)
        )

        for i, row in enumerate(videos_to_process):
            videos_attempted_count += 1
            transcript_text = str(row.get('Transcript', '')).strip()
            video_url = str(row.get('Video URL', '')).strip()
            video_id = extract_video_id(video_url)

            video_identifier = video_url or f"Row {i+2}"
            logger.info(f"Processing transcript for: {video_identifier}")

            if not video_url:
                progress.update(main_task, advance=1)
                continue

            if not transcript_text or len(transcript_text) < 50:
                progress.update(main_task, advance=1)
                continue

            progress.update(main_task, description=f"Analyzing {video_url[:30]}...")
            content_ideas = generate_content_ideas(transcript_text)

            ideas_suggested_this_video = 0
            if content_ideas and len(content_ideas) > 0:
                ideas_suggested_this_video = len(content_ideas)
                total_ideas_suggested_count += ideas_suggested_this_video
                videos_with_ideas_count += 1

                all_generated_content = generate_specific_content_pieces(
                    content_ideas,
                    transcript_text,
                    video_url
                )

                pieces_generated_this_video = 0
                if all_generated_content and all_generated_content.pieces:
                    pieces_generated_this_video = len(all_generated_content.pieces)
                    total_pieces_generated_count += pieces_generated_this_video
                    videos_with_generated_pieces_count += 1
                    
                    save_generated_content_to_csv(
                        all_generated_content,
                        output_csv_path,
                        video_url
                    )

            progress.update(main_task, advance=1)

    console.print("\n" + "="*30 + " Processing Summary " + "="*30)
    console.print(f" Total Videos in CSV:                 {len(df)}")
    console.print(f" Videos Attempted (up to limit):      {videos_attempted_count}")
    console.print(f" [green]Videos with Suggested Ideas:[/green]   {videos_with_ideas_count}")
    console.print(f" [green]Videos with Generated Pieces:[/green]  {videos_with_generated_pieces_count}")
    console.print(f" Total Content Ideas Suggested:     {total_ideas_suggested_count}")
    console.print(f" Total Valid Content Pieces Generated: {total_pieces_generated_count}")
    console.print("="*80)

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate short-form content from YouTube video transcripts using Gemini.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input", help="Input CSV file with 'Video URL' and 'Transcript' columns.")
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=None,
        help="Maximum number of videos to process from the CSV."
    )
    args = parser.parse_args()

    console.rule("[bold blue]Repurpose Script Execution[/]", style="blue")
    console.print(f"Input CSV:        [cyan]{args.input}[/cyan]")
    console.print(f"Output CSV:       [cyan]{os.path.abspath(GENERATED_CONTENT_CSV)}[/cyan]")
    console.print(f"Log File:         [cyan]{os.path.abspath(REPURPOSE_LOG_FILE)}[/cyan]")
    console.print(f"Gemini Model:     [cyan]{gemini_model_name}[/cyan]")

    if args.limit is not None:
         console.print(f"Processing limit: [yellow]{args.limit if args.limit >= 0 else 'None'}[/]")

    start_time = time.time()
    try:
        process_csv_file(args.input, GENERATED_CONTENT_CSV, args.limit)
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Script completed successfully in {duration:.2f} seconds.")
        console.print(f"\n[bold green]🏁 Finished processing in {duration:.2f} seconds.[/bold green]")
        console.rule(style="blue")

    except KeyboardInterrupt:
         end_time = time.time()
         duration = end_time - start_time
         console.print("\n[bold yellow]⚠️ Processing interrupted by user (Ctrl+C).[/bold yellow]")
         logger.warning("Processing interrupted by user.")
         sys.exit(130)

    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        console.print(f"\n[bold red]❌ Critical error after {duration:.2f} seconds: {str(e)}[/bold red]")
        logger.critical("Critical unhandled error occurred during script execution.", exc_info=True)
        console.print("[red]Check the log file for details:[/red]", os.path.abspath(REPURPOSE_LOG_FILE))
        sys.exit(1)

    sys.exit(0)