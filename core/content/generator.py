"""
Content Generation Functions
"""

from typing import List, Dict, Any, Optional
from pydantic import ValidationError
import json
import logging

from core.content.models import (
    ContentIdea,
    GeneratedIdeas,
    GeneratedContentList,
    Reel,
    ImageCarousel,
    Tweet,
    ContentType,
    CURRENT_FIELD_LIMITS,
    update_field_limits
)
from core.content.prompts import (
    get_system_prompt_generate_ideas,
    get_system_prompt_generate_content,
    call_gemini_api
)

logger = logging.getLogger(__name__)

