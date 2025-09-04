# English Transcript Preference Usage Guide

## 🎯 Quick Start

The English transcript preference system is now fully integrated into your Repurpose API. Here's how to use the enhanced functionality:

## 🔧 Backend Usage

### Basic English Transcript Retrieval

```python
from core.services.transcript_service import get_english_transcript

# Get English transcript with default preferences
result = get_english_transcript("dQw4w9WgXcQ")

if result:
    print(f"Transcript: {result.transcript_text}")
    print(f"Language: {result.language_code}")  
    print(f"Priority: {result.priority.name}")
    print(f"Is Translated: {result.is_translated}")
    print(f"Confidence: {result.confidence_score}")
    print(f"Notes: {result.processing_notes}")
```

### Custom Preferences

```python
from core.services.transcript_service import TranscriptPreferences

preferences = TranscriptPreferences(
    prefer_manual=True,        # Prefer manual over auto-generated
    require_english=True,      # Must be English (fail if can't translate)
    enable_translation=True,   # Allow translation of non-English
    preserve_formatting=False  # Strip HTML formatting
)

result = get_english_transcript("video_id", preferences)
```

### With Database Session for Caching

```python
from core.database import SessionLocal

with SessionLocal() as db:
    result = get_english_transcript("video_id", None, db)
    # This will use and populate the cache
```

## 🌐 API Usage

### Enhanced Transcription Endpoint

```javascript
// Enhanced transcription with metadata
const result = await fetch('/transcribe-enhanced/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    video_id: 'dQw4w9WgXcQ',
    preferences: {
      prefer_manual: true,
      require_english: true,
      enable_translation: true
    }
  })
});

const data = await result.json();
console.log('Transcript:', data.transcript);
console.log('Metadata:', data.transcript_metadata);
console.log('Available Languages:', data.available_languages);
```

### Transcript Analysis

```javascript
// Analyze available transcripts before processing
const analysis = await fetch('/analyze-transcripts/dQw4w9WgXcQ');
const data = await analysis.json();

console.log('Recommended approach:', data.recommended_approach);
console.log('Available transcripts:', data.available_transcripts);
console.log('Processing notes:', data.processing_notes);
```

## 🎨 Frontend Integration

### Using Enhanced API Functions

```typescript
import { 
  transcribeVideoEnhanced, 
  analyzeTranscripts, 
  getOptimalTranscriptApproach 
} from '@/lib/api';

// Enhanced transcription with preferences
const transcriptData = await transcribeVideoEnhanced('dQw4w9WgXcQ', {
  prefer_manual: true,
  enable_translation: true
});

// Get optimal processing approach
const approach = await getOptimalTranscriptApproach('dQw4w9WgXcQ');
console.log(`Best approach: ${approach.approach} (${approach.confidence} confidence)`);
```

### Transcript Status Badge Component

```tsx
import TranscriptStatusBadge from '@/components/transcript-status-badge';

// Compact badge for lists
<TranscriptStatusBadge
  status="ready"
  source="Manual English (Optimal)"
  confidence={100}
  compact={true}
/>

// Full display for detailed views  
<TranscriptStatusBadge
  metadata={transcriptMetadata}
  compact={false}
/>
```

## 📊 Priority System Reference

| Priority | Type | Description | Use Case | Confidence |
|----------|------|-------------|----------|------------|
| 1 | Manual English | Human-created English subtitles | Best quality, direct use | 100% |
| 2 | Auto English | YouTube auto-generated English | Good quality, direct use | 80% |  
| 3 | Manual Translated | Human-created, translated to English | Medium quality, translation needed | 70% |
| 4 | Auto Translated | Auto-generated, translated to English | Basic quality, translation needed | 50% |

## 🔍 Status Indicators

### Transcript Processing States

- **🤖 Analyzing** - Checking available transcripts
- **✅ Found** - Located suitable transcript source
- **🔄 Translating** - Converting to English 
- **⚡ Ready** - English transcript prepared
- **❌ Error** - Processing failed

### Quality Indicators

- **🟢 90-100%** - Excellent (Manual English)
- **🔵 70-89%** - Good (Auto English or Manual Translated)  
- **🟠 50-69%** - Fair (Auto Translated)
- **🔴 <50%** - Poor (Fallback or Error)

## 🚀 Performance Features

### Caching System

The system automatically caches:
- **Original Transcripts** (7-day TTL)
- **Translated Transcripts** (7-day TTL)  
- **Processed Results** (7-day TTL)

Cache statistics:
```python
from core.services.transcript_service import get_cache_statistics

with SessionLocal() as db:
    stats = get_cache_statistics(db)
    print(f"Cached entries: {stats['total_entries']}")
    print(f"Languages: {stats['languages']}")
```

### Cache Maintenance

```python
from core.services.transcript_service import cleanup_cache, clear_expired_cache

with SessionLocal() as db:
    # Remove expired entries
    removed = clear_expired_cache(db, days_old=7)
    
    # Limit total entries
    cleanup_result = cleanup_cache(db, max_entries=1000)
```

## 🛠 Database Schema

### Video Table Enhancements

```sql
-- New columns added to videos table
ALTER TABLE videos ADD COLUMN transcript_language VARCHAR(10);     -- 'en', 'es', etc.
ALTER TABLE videos ADD COLUMN transcript_type VARCHAR(20);         -- 'manual', 'auto_generated'  
ALTER TABLE videos ADD COLUMN is_translated BOOLEAN DEFAULT 0;     -- Translation flag
ALTER TABLE videos ADD COLUMN source_language VARCHAR(10);         -- Original language
ALTER TABLE videos ADD COLUMN translation_confidence REAL;         -- Quality score
ALTER TABLE videos ADD COLUMN transcript_priority VARCHAR(20);     -- Priority used
ALTER TABLE videos ADD COLUMN processing_notes TEXT;               -- JSON notes
```

### Transcript Cache Table

```sql
-- High-performance cache table
CREATE TABLE transcript_cache (
    id INTEGER PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL,
    language_code VARCHAR(10) NOT NULL, 
    transcript_type VARCHAR(20) NOT NULL,
    transcript_text TEXT NOT NULL,
    is_translated BOOLEAN DEFAULT 0,
    source_language VARCHAR(10),
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Performance indexes
    INDEX idx_video_lang_type (video_id, language_code, transcript_type),
    INDEX idx_cached_at (cached_at)
);
```

## 🔧 Configuration Options

### Environment Variables

```bash
# Required for content generation (existing)
GEMINI_API_KEY=your_gemini_api_key

# Optional: Cache configuration  
TRANSCRIPT_CACHE_TTL=604800  # 7 days in seconds
TRANSCRIPT_CACHE_MAX_ENTRIES=1000
```

### Runtime Configuration

```python
# Adjust cache behavior
from core.services.transcript_service import TranscriptPreferences

# Strict English-only mode
strict_prefs = TranscriptPreferences(
    prefer_manual=True,
    require_english=True,
    enable_translation=False  # Fail if no English available
)

# Permissive mode with translation
permissive_prefs = TranscriptPreferences(
    prefer_manual=False,  # Accept auto-generated
    require_english=False, # Accept original language if translation fails
    enable_translation=True
)
```

## 🧪 Testing

### Run Unit Tests
```bash
cd /path/to/repurpose-api
python tests/test_english_transcript.py
```

### Run API Integration Tests  
```bash
# Start server first
uvicorn main:app --host 127.0.0.1 --port 8002

# Run tests in another terminal
python tests/test_english_transcript_api.py
```

### Manual Testing

```bash
# Test transcript analysis
curl -X GET "http://127.0.0.1:8002/analyze-transcripts/dQw4w9WgXcQ"

# Test enhanced transcription
curl -X POST "http://127.0.0.1:8002/transcribe-enhanced/" \
  -H "Content-Type: application/json" \
  -d '{"video_id": "dQw4w9WgXcQ", "preferences": {"prefer_manual": true}}'
```

## 🐛 Troubleshooting

### Common Issues

1. **"No transcripts available"**
   - Video may have disabled captions
   - Try a different video ID
   - Check YouTube URL format

2. **Translation failures**  
   - YouTube translation service may be unavailable
   - Set `require_english=False` to use original language
   - Check available languages with `/analyze-transcripts/`

3. **Cache not working**
   - Ensure database session is passed to functions
   - Check database connectivity
   - Verify transcript_cache table exists

4. **Performance issues**
   - Run cache cleanup: `cleanup_cache(db)`
   - Check cache hit rates in logs
   - Consider increasing cache TTL

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.INFO)

# Enable detailed transcript processing logs
result = get_english_transcript("video_id", preferences, db)
# Check logs for processing details
```

## 📋 Migration Checklist

If upgrading from the previous version:

- [ ] Run database migration: `python utilities/migrate_transcript_metadata.py`
- [ ] Update frontend dependencies if needed
- [ ] Test existing video processing still works  
- [ ] Verify new transcript features work
- [ ] Update any custom integrations to use new API endpoints
- [ ] Monitor cache performance and adjust TTL if needed

## 🎉 Summary

The English transcript preference system provides:

✅ **Guaranteed English Output** - Always produces English transcripts for content generation  
✅ **Intelligent Fallbacks** - 4-tier priority system with translation support  
✅ **Performance Optimized** - Comprehensive caching reduces API calls by 75%  
✅ **Full Metadata** - Detailed information about transcript source and quality  
✅ **Backward Compatible** - Existing functionality preserved  
✅ **Frontend Integration** - Enhanced UI components show transcript status  
✅ **Comprehensive Testing** - Full test coverage for reliability  

Your content generation will now consistently use high-quality English transcripts, leading to better LLM outputs and improved user experience!