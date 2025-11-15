"""
Content Generation Prompts and API Calls
"""

from typing import Dict, Any, Optional
import os
import logging
import json

from core.content.models import CURRENT_FIELD_LIMITS

logger = logging.getLogger(__name__)

# Content Style Definition
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


def call_gemini_api(system_prompt: str, user_prompt: str, content_generator=None) -> Optional[Dict[str, Any]]:
    """Call Gemini API with retry logic
    
    Note: content_generator should be passed from the calling code.
    This is a helper function that will be called with the generator instance.
    """
    if content_generator is None:
        logger.error("No content generator provided to call_gemini_api")
        return None
        
    return content_generator.call_api(system_prompt, user_prompt)

def get_system_prompt_generate_ideas(content_style: str = "{CONTENT_STYLE}", min_ideas: int = 6, max_ideas: int = 8) -> str:
    """Generate the system prompt for idea generation with configurable limits"""
    return f"""
You are an expert AI assistant specializing in analyzing video transcripts to identify valuable, repurposable content ideas.

**Primary Task**: 
Carefully analyze the provided video transcript and identify {min_ideas} to {max_ideas} distinct content ideas that capture the most important, interesting, or actionable insights from the video.

**Focus on the Video Content**:
- Extract key insights, lessons, tips, or stories from the transcript
- Identify content that would provide real value to viewers
- Look for unique angles, surprising facts, or practical advice
- Consider what parts of the video are most shareable or memorable
- Each idea should highlight something specific and valuable from the video

**Output Format**:
Return a single JSON object with a key named "ideas" containing a list of {min_ideas} to {max_ideas} content ideas.
Each idea object should have this structure:
{{{{
  "suggested_content_type": "<'reel'|'image_carousel'|'tweet'>",
  "suggested_title": "<string, a catchy title that captures the core insight>",
  "relevant_transcript_snippet": "<string, a direct quote from the transcript that inspired this idea>",
  "type_specific_suggestions": {{{{}}}}
}}}}

**Style Consideration** (as a secondary guide):
When presenting these ideas, consider this target style: {content_style}

Note: The video's actual content and key messages should drive your idea selection. Style is a presentation guide, not a content filter."""

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


CONTENT CREATION GUIDELINES:

**Primary Goal**: Extract the most valuable insights and key points from the video transcript/content idea and present them in the requested format.

**Content Requirements**:
    - For image_carousel: Generate {limits['carousel_min_slides']}-{limits['carousel_max_slides']} slides
    - For carousel slides: Make the "text" field detailed and valuable (400-{limits['carousel_slide_text_max']} chars recommended)
      · Include multiple sentences with specific details from the video
      · Provide actionable information, examples, or key insights from the content
      · Make each slide self-contained and informative
      · The step_heading is a short label; the text field contains the real value
    - Your output must be valid JSON matching one of the schemas above
    - Do NOT include content_id in your response

**Style Adaptation** (apply as a guide, not a constraint):
    The content should reflect this style when appropriate: {content_style}
    
    Balance is key:
    - Prioritize accuracy and relevance to the source content
    - Maintain the video's core message and key insights
    - Adapt the tone and presentation style naturally
    - Don't force style elements that conflict with the video's content
    - The video's substance should drive the content; style should enhance, not overpower
"""

