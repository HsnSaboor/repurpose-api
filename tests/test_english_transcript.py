#!/usr/bin/env python3
"""
Comprehensive test suite for English transcript preference functionality
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.services.transcript_service import (
    TranscriptPriority,
    TranscriptMetadata,
    EnglishTranscriptResult,
    TranscriptPreferences,
    get_english_transcript,
    find_best_english_transcript_source,
    get_priority_for_transcript,
    list_available_transcripts_with_metadata,
    get_cached_transcript,
    cache_transcript,
    clear_expired_cache
)


class TestTranscriptPriority:
    """Test TranscriptPriority enum"""
    
    def test_priority_values(self):
        """Test that priority values are correctly ordered"""
        assert TranscriptPriority.MANUAL_ENGLISH.value == 1
        assert TranscriptPriority.AUTO_ENGLISH.value == 2
        assert TranscriptPriority.MANUAL_TRANSLATED.value == 3
        assert TranscriptPriority.AUTO_TRANSLATED.value == 4


class TestTranscriptModels:
    """Test Pydantic models"""
    
    def test_transcript_preferences_defaults(self):
        """Test default values for TranscriptPreferences"""
        prefs = TranscriptPreferences()
        assert prefs.prefer_manual is True
        assert prefs.require_english is True
        assert prefs.enable_translation is True
        assert prefs.fallback_languages == ["en", "es", "fr", "de"]
        assert prefs.preserve_formatting is False
    
    def test_english_transcript_result_creation(self):
        """Test EnglishTranscriptResult model creation"""
        result = EnglishTranscriptResult(
            transcript_text="Test transcript",
            language_code="en",
            language="English",
            is_generated=False,
            is_translated=False,
            priority=TranscriptPriority.MANUAL_ENGLISH
        )
        
        assert result.transcript_text == "Test transcript"
        assert result.language_code == "en"
        assert result.priority == TranscriptPriority.MANUAL_ENGLISH
        assert result.confidence_score == 1.0  # Default value
        assert result.processing_notes == []  # Default value


class TestTranscriptSelection:
    """Test transcript selection logic"""
    
    def create_mock_transcript(self, language_code: str, language: str, is_generated: bool, is_translatable: bool = True):
        """Helper to create mock transcript objects"""
        mock_transcript = Mock()
        mock_transcript.language_code = language_code
        mock_transcript.language = language
        mock_transcript.is_generated = is_generated
        mock_transcript.is_translatable = is_translatable
        
        # Mock fetch method
        mock_data = Mock()
        mock_data.to_raw_data.return_value = [
            {'text': f'Test text in {language}', 'start': 0.0, 'duration': 5.0}
        ]
        mock_transcript.fetch.return_value = mock_data
        
        # Mock translate method
        if is_translatable:
            mock_translated = Mock()
            mock_translated_data = Mock()
            mock_translated_data.to_raw_data.return_value = [
                {'text': 'Translated test text', 'start': 0.0, 'duration': 5.0}
            ]
            mock_translated.fetch.return_value = mock_translated_data
            mock_transcript.translate.return_value = mock_translated
        
        return mock_transcript
    
    @patch('core.services.transcript_service.YouTubeTranscriptApi')
    def test_manual_english_priority(self, mock_api):
        """Test that manual English transcript gets highest priority"""
        # Setup mock API
        mock_instance = Mock()
        mock_api.return_value = mock_instance
        
        # Create mock transcript list with various options
        transcripts = [
            self.create_mock_transcript('es', 'Spanish', True),  # Auto Spanish
            self.create_mock_transcript('en', 'English', False),  # Manual English - should win
            self.create_mock_transcript('en', 'English', True),   # Auto English
        ]
        mock_instance.list.return_value = transcripts
        
        # Test
        best = find_best_english_transcript_source('test_video_id')
        
        assert best is not None
        assert best.language_code == 'en'
        assert best.is_generated is False  # Manual transcript
    
    @patch('core.services.transcript_service.YouTubeTranscriptApi')
    def test_auto_english_fallback(self, mock_api):
        """Test fallback to auto-generated English when manual not available"""
        mock_instance = Mock()
        mock_api.return_value = mock_instance
        
        transcripts = [
            self.create_mock_transcript('es', 'Spanish', False),  # Manual Spanish
            self.create_mock_transcript('en', 'English', True),   # Auto English - should win
            self.create_mock_transcript('fr', 'French', True),    # Auto French
        ]
        mock_instance.list.return_value = transcripts
        
        best = find_best_english_transcript_source('test_video_id')
        
        assert best is not None
        assert best.language_code == 'en'
        assert best.is_generated is True
    
    @patch('core.services.transcript_service.YouTubeTranscriptApi')
    def test_translation_fallback(self, mock_api):
        """Test fallback to translation when no English available"""
        mock_instance = Mock()
        mock_api.return_value = mock_instance
        
        transcripts = [
            self.create_mock_transcript('es', 'Spanish', False),  # Manual Spanish - should win for translation
            self.create_mock_transcript('fr', 'French', True),    # Auto French
        ]
        mock_instance.list.return_value = transcripts
        
        best = find_best_english_transcript_source('test_video_id')
        
        assert best is not None
        assert best.language_code == 'es'
        assert best.is_generated is False  # Prefer manual for translation
    
    def test_get_priority_for_transcript(self):
        """Test priority assignment logic"""
        # Mock transcript objects
        manual_en = Mock()
        manual_en.language_code = 'en'
        manual_en.is_generated = False
        
        auto_en = Mock()
        auto_en.language_code = 'en'  
        auto_en.is_generated = True
        
        manual_other = Mock()
        manual_other.language_code = 'es'
        manual_other.is_generated = False
        
        auto_other = Mock()
        auto_other.language_code = 'fr'
        auto_other.is_generated = True
        
        # Test priority assignments
        assert get_priority_for_transcript(manual_en, False) == TranscriptPriority.MANUAL_ENGLISH
        assert get_priority_for_transcript(auto_en, False) == TranscriptPriority.AUTO_ENGLISH
        assert get_priority_for_transcript(manual_other, True) == TranscriptPriority.MANUAL_TRANSLATED
        assert get_priority_for_transcript(auto_other, True) == TranscriptPriority.AUTO_TRANSLATED


class TestCachingFunctionality:
    """Test caching system"""
    
    def test_cache_key_generation(self):
        """Test cache key generation is consistent"""
        from core.services.transcript_service import get_cache_key
        
        key1 = get_cache_key('video123', 'en', 'manual')
        key2 = get_cache_key('video123', 'en', 'manual')
        key3 = get_cache_key('video123', 'es', 'manual')
        
        assert key1 == key2  # Same inputs should produce same key
        assert key1 != key3  # Different inputs should produce different keys
    
    def test_cache_operations_without_db(self):
        """Test cache operations handle missing database gracefully"""
        # These should not crash when db_session is None
        cached = get_cached_transcript('video123', 'en', 'manual', None)
        assert cached is None
        
        success = cache_transcript('video123', 'en', 'manual', 'test text', False, None, None)
        assert success is False
        
        cleared = clear_expired_cache(None)
        assert cleared == 0


class TestEnglishTranscriptIntegration:
    """Integration tests for the main get_english_transcript function"""
    
    @patch('core.services.transcript_service.find_best_english_transcript_source')
    @patch('core.services.transcript_service.get_cached_transcript')
    def test_cache_hit_returns_early(self, mock_get_cache, mock_find_best):
        """Test that cache hit returns without API call"""
        # Setup cache hit
        mock_get_cache.return_value = "Cached transcript text"
        
        # Mock database session
        mock_db = Mock()
        
        result = get_english_transcript('video123', None, mock_db)
        
        # Should return cached result
        assert result is not None
        assert result.transcript_text == "Cached transcript text"
        assert "Retrieved from cache" in result.processing_notes
        
        # Should not call find_best_english_transcript_source
        mock_find_best.assert_not_called()
    
    @patch('core.services.transcript_service.find_best_english_transcript_source')
    @patch('core.services.transcript_service.get_cached_transcript')
    @patch('core.services.transcript_service.cache_transcript')
    def test_english_transcript_with_caching(self, mock_cache_fn, mock_get_cache, mock_find_best):
        """Test processing English transcript with caching"""
        # Setup no cache hit
        mock_get_cache.return_value = None
        
        # Setup mock transcript
        mock_transcript = Mock()
        mock_transcript.language_code = 'en'
        mock_transcript.language = 'English'
        mock_transcript.is_generated = False
        
        mock_data = Mock()
        mock_data.to_raw_data.return_value = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0}
        ]
        mock_transcript.fetch.return_value = mock_data
        mock_find_best.return_value = mock_transcript
        
        # Setup cache function
        mock_cache_fn.return_value = True
        
        # Mock database session
        mock_db = Mock()
        
        result = get_english_transcript('video123', None, mock_db)
        
        # Verify result
        assert result is not None
        assert result.transcript_text == "Hello world"
        assert result.language_code == 'en'
        assert result.is_translated is False
        assert result.priority == TranscriptPriority.MANUAL_ENGLISH
        
        # Verify caching was called
        mock_cache_fn.assert_called()
    
    @patch('core.services.transcript_service.find_best_english_transcript_source')
    @patch('core.services.transcript_service.get_cached_transcript')
    @patch('core.services.transcript_service.cache_transcript')
    def test_translation_with_caching(self, mock_cache_fn, mock_get_cache, mock_find_best):
        """Test translation workflow with caching"""
        # Setup no cache hit
        mock_get_cache.return_value = None
        
        # Setup mock Spanish transcript that needs translation
        mock_transcript = Mock()
        mock_transcript.language_code = 'es'
        mock_transcript.language = 'Spanish'
        mock_transcript.is_generated = False
        
        # Mock original transcript data
        mock_data = Mock()
        mock_data.to_raw_data.return_value = [
            {'text': 'Hola mundo', 'start': 0.0, 'duration': 2.0}
        ]
        mock_transcript.fetch.return_value = mock_data
        
        # Mock translation
        mock_translated = Mock()
        mock_translated_data = Mock()
        mock_translated_data.to_raw_data.return_value = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0}
        ]
        mock_translated.fetch.return_value = mock_translated_data
        mock_transcript.translate.return_value = mock_translated
        
        mock_find_best.return_value = mock_transcript
        mock_cache_fn.return_value = True
        
        # Mock database session  
        mock_db = Mock()
        
        result = get_english_transcript('video123', None, mock_db)
        
        # Verify result
        assert result is not None
        assert result.transcript_text == "Hello world"
        assert result.language_code == 'en'
        assert result.is_translated is True
        assert result.translation_source_language == 'es'
        assert result.priority == TranscriptPriority.MANUAL_TRANSLATED
        
        # Verify translation was attempted
        mock_transcript.translate.assert_called_with('en')
    
    @patch('core.services.transcript_service.find_best_english_transcript_source')
    def test_no_transcripts_available(self, mock_find_best):
        """Test handling when no transcripts are available"""
        mock_find_best.return_value = None
        
        result = get_english_transcript('video123')
        
        assert result is None


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @patch('core.services.transcript_service.find_best_english_transcript_source')
    def test_api_error_handling(self, mock_find_best):
        """Test handling of API errors"""
        # Simulate API error
        mock_find_best.side_effect = Exception("YouTube API error")
        
        result = get_english_transcript('video123')
        
        assert result is None
    
    @patch('core.services.transcript_service.find_best_english_transcript_source')
    def test_translation_failure_handling(self, mock_find_best):
        """Test handling when translation fails"""
        # Setup mock transcript that fails translation
        mock_transcript = Mock()
        mock_transcript.language_code = 'es'
        mock_transcript.language = 'Spanish'
        mock_transcript.is_generated = False
        
        mock_data = Mock()
        mock_data.to_raw_data.return_value = [
            {'text': 'Hola mundo', 'start': 0.0, 'duration': 2.0}
        ]
        mock_transcript.fetch.return_value = mock_data
        
        # Mock translation failure
        mock_transcript.translate.side_effect = Exception("Translation API error")
        
        mock_find_best.return_value = mock_transcript
        
        # Test with require_english=False (should use original text)
        prefs = TranscriptPreferences(require_english=False)
        result = get_english_transcript('video123', prefs)
        
        assert result is not None
        assert result.transcript_text == "Hola mundo"  # Original Spanish text
        assert "Translation failed" in result.processing_notes[0]
        
        # Test with require_english=True (should return None)
        prefs_strict = TranscriptPreferences(require_english=True)
        result_strict = get_english_transcript('video123', prefs_strict)
        
        assert result_strict is None


def run_tests():
    """Run all tests"""
    import pytest
    
    # Run pytest on this file
    exit_code = pytest.main([__file__, '-v', '--tb=short'])
    return exit_code == 0


if __name__ == "__main__":
    print("🧪 Running English Transcript Functionality Tests")
    print("=" * 60)
    
    success = run_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! English transcript functionality is working correctly.")
    else:
        print("❌ Some tests failed. Please review the output above.")