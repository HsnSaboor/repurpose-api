"""
Transcript Service Models
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class TranscriptPriority(Enum):
    """Priority levels for transcript selection"""
    MANUAL_ENGLISH = 1
    AUTO_ENGLISH = 2
    MANUAL_TRANSLATED = 3
    AUTO_TRANSLATED = 4


class TranscriptMetadata(BaseModel):
    """Metadata about a transcript"""
    language_code: str
    language: str
    is_generated: bool
    is_translatable: bool
    translation_languages: List[str] = []


class EnglishTranscriptResult(BaseModel):
    """Result of English transcript processing"""
    transcript_text: str
    language_code: str
    language: str
    is_generated: bool
    is_translated: bool
    priority: TranscriptPriority
    translation_source_language: Optional[str] = None
    confidence_score: float = 1.0
    processing_notes: List[str] = []


class TranscriptPreferences(BaseModel):
    """User preferences for transcript processing"""
    prefer_manual: bool = True
    require_english: bool = True
    enable_translation: bool = True
    fallback_languages: List[str] = ["en", "es", "fr", "de"]
    preserve_formatting: bool = False
