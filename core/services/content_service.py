"""Content Generation Service using Google Gemini"""
import json
import logging
import threading
import time
from collections import deque
from datetime import timedelta
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pydantic import BaseModel

class GeminiRateLimiter:
    def __init__(self, rpm_limit=10, qpd_limit=1500):
        self.rpm_limit = rpm_limit
        self.qpd_limit = qpd_limit
        self.request_times = deque()
        self.lock = threading.Lock()
        self.daily_count = 0
        self.last_reset_day = time.localtime().tm_yday
    
    def wait_for_capacity(self):
        while True:
            with self.lock:
                now = time.time()
                current_day = time.localtime().tm_yday
                
                # Reset daily count if it's a new day
                if current_day != self.last_reset_day:
                    self.daily_count = 0
                    self.last_reset_day = current_day
                
                # Remove old requests from the queue
                one_minute_ago = now - 60
                while self.request_times and self.request_times[0] < one_minute_ago:
                    self.request_times.popleft()
                
                # Check if we can make a request
                if (self.daily_count < self.qpd_limit and 
                    len(self.request_times) < self.rpm_limit):
                    self.request_times.append(now)
                    self.daily_count += 1
                    return
            
            time.sleep(0.1)

class ContentGenerator:
    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.rate_limiter = GeminiRateLimiter()
        self.logger = logging.getLogger(__name__)
    
    def generate_content(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        self.rate_limiter.wait_for_capacity()
        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            if response.choices and response.choices[0].message.content:
                content_str = response.choices[0].message.content.strip()
                if content_str.startswith("```json"):
                    content_str = content_str[7:-3].strip()
                return json.loads(content_str)
        except Exception as e:
            self.logger.error(f"Error in content generation: {e}")
        return None

class ContentIdea(BaseModel):
    suggested_content_type: str
    suggested_title: str
    relevant_transcript_snippet: str
    type_specific_suggestions: Optional[Dict[str, Any]] = None

class GeneratedContent(BaseModel):
    content_id: str
    content_type: str
    title: str
    content: Dict[str, Any]