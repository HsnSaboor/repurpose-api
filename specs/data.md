# Data Model Specification

**Version:** 2.0  
**Last Updated:** January 2026

---

## 1. Database Schema

### 1.1 Videos Table (Legacy - Brain Sources)

Primary table for storing processed YouTube videos and documents. Now serves as the Brain's source storage.

```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status VARCHAR,
    youtube_video_id VARCHAR NOT NULL,
    title VARCHAR,
    transcript TEXT,
    video_url VARCHAR,
    repurposed_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Enhanced transcript metadata
    transcript_language VARCHAR(10),
    transcript_type VARCHAR(20),      -- 'manual' | 'auto_generated'
    is_translated BOOLEAN DEFAULT FALSE,
    source_language VARCHAR(10),
    translation_confidence FLOAT,
    transcript_priority VARCHAR(20),
    processing_notes TEXT,             -- JSON string
    
    -- Brain indexing fields (v2.0)
    is_indexed BOOLEAN DEFAULT FALSE,
    indexed_at DATETIME,
    source_type VARCHAR(20),           -- 'youtube' | 'document' | 'text'
    tags TEXT,                         -- JSON array of tags
    topics TEXT,                       -- JSON array of extracted topics
    summary TEXT,                      -- AI-generated summary
    embedding_id VARCHAR(100)          -- Reference to vector embedding
);

CREATE INDEX idx_videos_indexed ON videos(is_indexed);
CREATE INDEX idx_videos_source_type ON videos(source_type);
```

### 1.2 Brain Sources Table (New)

Unified view of all knowledge sources in the Brain.

```sql
CREATE TABLE brain_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id VARCHAR(100) NOT NULL UNIQUE,  -- Normalized ID
    source_type VARCHAR(20) NOT NULL,        -- 'youtube' | 'document' | 'text'
    title VARCHAR(500),
    content TEXT NOT NULL,                   -- Full text content
    summary TEXT,                            -- AI-generated summary (200-500 chars)
    topics TEXT,                             -- JSON array: ["topic1", "topic2"]
    tags TEXT,                               -- JSON array: ["tag1", "tag2"]
    metadata TEXT,                           -- JSON: source-specific metadata
    
    -- Indexing
    embedding BLOB,                          -- Vector embedding for semantic search
    embedding_model VARCHAR(50),             -- Model used for embedding
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME,
    use_count INTEGER DEFAULT 0
);

CREATE INDEX idx_brain_sources_type ON brain_sources(source_type);
CREATE INDEX idx_brain_sources_last_used ON brain_sources(last_used_at);
```

### 1.3 Brain Generation Sessions Table

Tracks content generation sessions using Brain sources.

```sql
CREATE TABLE brain_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    mode VARCHAR(20) NOT NULL,               -- 'vision' | 'full_ai_single' | 'full_ai_multiple' | 'full_ai_auto'
    
    -- Input
    user_vision TEXT,                        -- User's idea/thought (for vision mode)
    selected_source_ids TEXT,                -- JSON array of source IDs
    requested_count INTEGER,                 -- For multiple mode
    
    -- Matching (for vision mode)
    matched_source_ids TEXT,                 -- JSON array of matched source IDs
    match_scores TEXT,                       -- JSON: {source_id: score}
    
    -- Output
    generated_count INTEGER,
    generated_content TEXT,                  -- JSON array of generated pieces
    
    -- Style
    style_preset VARCHAR(50),
    custom_style TEXT,                       -- JSON
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    status VARCHAR(20) DEFAULT 'pending'     -- 'pending' | 'processing' | 'completed' | 'failed'
);
```

### 1.4 Transcript Cache Table

Cache for storing transcript data to avoid repeated API calls.

```sql
CREATE TABLE transcript_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(50) NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    transcript_type VARCHAR(20) NOT NULL,
    transcript_text TEXT NOT NULL,
    is_translated BOOLEAN DEFAULT FALSE,
    source_language VARCHAR(10),
    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transcript_cache_video_id ON transcript_cache(video_id);
```

---

## 2. Content Models

### 2.1 Content Types Enum

```python
class ContentType(str, Enum):
    REEL = "reel"
    IMAGE_CAROUSEL = "image_carousel"
    TWEET = "tweet"
```

### 2.2 Content Idea Schema

Generated during idea generation phase.

```json
{
  "suggested_content_type": "reel" | "image_carousel" | "tweet",
  "suggested_title": "string (max 100 chars)",
  "relevant_transcript_snippet": "string",
  "type_specific_suggestions": {
    // Optional type-specific hints
  }
}
```

### 2.3 Reel Schema

```json
{
  "content_id": "VIDEO_ID_001",
  "content_type": "reel",
  "title": "string (max 100 chars)",
  "caption": "string (max 300 chars)",
  "hook": "string (max 200 chars)",
  "script_body": "string (max 2000 chars)",
  "visual_suggestions": "string (optional)",
  "hashtags": ["string"]
}
```

#### Field Constraints

| Field | Max Length | Required |
|-------|------------|----------|
| `content_id` | - | Yes |
| `title` | 100 | Yes |
| `caption` | 300 | No |
| `hook` | 200 | Yes |
| `script_body` | 2000 | Yes |
| `visual_suggestions` | - | No |
| `hashtags` | - | No |

### 2.4 Image Carousel Schema

```json
{
  "content_id": "VIDEO_ID_002",
  "content_type": "image_carousel",
  "title": "string (max 100 chars)",
  "caption": "string (max 300 chars)",
  "slides": [
    {
      "slide_number": 1,
      "step_number": 1,
      "step_heading": "string (max 100 chars)",
      "text": "string (max 800 chars)"
    }
  ],
  "hashtags": ["string"]
}
```

#### Carousel Constraints

| Field | Constraint |
|-------|------------|
| `slides` | 4-8 slides (configurable) |
| `step_heading` | Max 100 chars |
| `text` | Max 800 chars per slide |

### 2.5 Tweet Schema

```json
{
  "content_id": "VIDEO_ID_003",
  "content_type": "tweet",
  "title": "string (max 100 chars)",
  "tweet_text": "string (max 280 chars)",
  "thread_continuation": ["string (max 280 chars each)"],
  "hashtags": ["string"]
}
```

---

## 3. Configuration Models

### 3.1 Field Limits Configuration

```json
{
  "reel_title_max": 100,
  "reel_caption_max": 300,
  "reel_hook_max": 200,
  "reel_script_max": 2000,
  "carousel_title_max": 100,
  "carousel_caption_max": 300,
  "carousel_slide_heading_max": 100,
  "carousel_slide_text_max": 800,
  "carousel_min_slides": 4,
  "carousel_max_slides": 8,
  "tweet_title_max": 100,
  "tweet_text_max": 280,
  "tweet_thread_item_max": 280
}
```

### 3.2 Content Generation Config

```json
{
  "min_ideas": 6,
  "max_ideas": 8,
  "content_pieces_per_idea": 1,
  "field_limits": { /* FieldLimitsConfig */ }
}
```

### 3.3 Style Preset Schema

```json
{
  "name": "string",
  "description": "string",
  "target_audience": "string",
  "call_to_action": "string",
  "content_goal": "string",
  "language": "English",
  "tone": "Professional",
  "additional_instructions": "string (optional)",
  "content_config": { /* ContentGenerationConfig */ }
}
```

---

## 4. API Request/Response Models

### 4.1 Transcribe Request

```json
{
  "video_id": "string (required)",
  "preferences": {
    "prefer_manual": true,
    "require_english": false,
    "enable_translation": true,
    "fallback_languages": ["en", "es", "fr"]
  }
}
```

### 4.2 Process Video Request

```json
{
  "video_id": "string (required)",
  "force_regenerate": false,
  "style_preset": "string (optional)",
  "custom_style": {
    "target_audience": "string",
    "call_to_action": "string",
    "content_goal": "string",
    "language": "English",
    "tone": "Professional",
    "additional_instructions": "string (optional)",
    "content_config": { /* optional overrides */ }
  }
}
```

### 4.3 Process Video Response

```json
{
  "id": 1,
  "youtube_video_id": "VIDEO_ID",
  "title": "Video Title",
  "transcript": "Full transcript...",
  "status": "completed",
  "ideas": [ /* ContentIdea[] */ ],
  "content_pieces": [ /* Reel | ImageCarousel | Tweet */ ]
}
```

### 4.4 Edit Content Request

```json
{
  "video_id": "string",
  "content_piece_id": "VIDEO_ID_001",
  "edit_prompt": "Make it more engaging",
  "content_type": "reel" | "image_carousel" | "tweet"
}
```

### 4.5 Edit Content Response

```json
{
  "video_id": "string",
  "content_piece_id": "string",
  "content_type": "string",
  "original_content": { /* original piece */ },
  "edited_content": { /* modified piece */ },
  "changes_made": ["list of changes"],
  "status": "success" | "error"
}
```

---

## 5. Data Flow

```
┌─────────────────┐
│   Input Source  │
│ (URL/File/Doc)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Transcript    │
│   Extraction    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Idea Generator │
│  (6-8 ideas)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Content Generator│
│ (per idea)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validation    │
│   + Auto-Fix    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Storage      │
│  (DB + Files)   │
└─────────────────┘
```

---

## 6. Storage Formats

### 6.1 Database Storage

The `repurposed_text` field stores content in this format:

```
Ideas:
[{'suggested_content_type': 'reel', ...}, ...]

Content Pieces:
{
  "content_id": "...",
  ...
}

---

{
  "content_id": "...",
  ...
}
```

### 6.2 CSV Output (CLI)

#### generated_content.csv
```csv
Video URL,Video Title,Content ID,Content Type,Title,Generated Content JSON
```

#### {video_id}_carousel_titles.csv
```csv
Content ID,Video URL,Title,Caption,Hashtags,Slides Count
```

#### {content_id}_slides.csv
```csv
slide_number,step_number,step_heading,text
```
