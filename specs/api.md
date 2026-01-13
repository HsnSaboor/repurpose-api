# API Specification

**Version:** 2.0  
**Last Updated:** January 2026  
**Base URL:** `http://127.0.0.1:8002`

---

## 1. Overview

RESTful API built with FastAPI. All endpoints accept and return JSON unless otherwise noted.

### Authentication
Currently: None (local development)  
Future: API key or JWT authentication

### Common Headers
```
Content-Type: application/json
```

---

## 2. Brain Endpoints (NEW in v2.0)

### 2.1 Brain Sources

#### 2.1.1 List Brain Sources

```
GET /brain/sources/?skip=0&limit=50&source_type=youtube
```

List all sources stored in the Brain.

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Max results (default: 50)
- `source_type`: Filter by type: `youtube`, `document`, `text` (optional)
- `search`: Text search in titles/topics (optional)

**Response:**
```json
{
  "sources": [
    {
      "source_id": "dQw4w9WgXcQ",
      "source_type": "youtube",
      "title": "Video Title",
      "summary": "Brief AI-generated summary...",
      "topics": ["marketing", "entrepreneurship"],
      "tags": ["business", "tips"],
      "created_at": "2026-01-12T10:00:00",
      "last_used_at": "2026-01-12T12:00:00",
      "use_count": 5
    }
  ],
  "total": 25,
  "has_more": false
}
```

---

#### 2.1.2 Get Single Source

```
GET /brain/sources/{source_id}
```

**Response:**
```json
{
  "source_id": "dQw4w9WgXcQ",
  "source_type": "youtube",
  "title": "Video Title",
  "content": "Full transcript/text content...",
  "summary": "Brief AI-generated summary...",
  "topics": ["marketing", "entrepreneurship"],
  "tags": ["business", "tips"],
  "metadata": {
    "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "duration": "10:32",
    "language": "en"
  },
  "created_at": "2026-01-12T10:00:00",
  "use_count": 5
}
```

---

#### 2.1.3 Add Source to Brain

```
POST /brain/sources/
```

Manually add a source to the Brain (auto-indexes).

**Request Body:**
```json
{
  "source_type": "youtube",
  "source_id": "dQw4w9WgXcQ",
  "auto_process": true
}
```

Or for text:
```json
{
  "source_type": "text",
  "title": "My Notes",
  "content": "Raw text content to add...",
  "tags": ["personal", "ideas"]
}
```

Or for URL (web article):
```json
{
  "source_type": "url",
  "url": "https://example.com/blog/article",
  "title": "Optional Custom Title",
  "tags": ["research", "marketing"],
  "extract_options": {
    "include_tables": true,
    "include_links": true,
    "include_images": false
  }
}
```

**Response (URL source):**
```json
{
  "source_id": "src_abc123",
  "source_type": "url",
  "title": "Auto-Extracted Article Title",
  "content": "# Article Heading\n\nClean markdown content extracted from the URL...",
  "summary": "AI-generated summary...",
  "topics": ["topic1", "topic2"],
  "source_metadata": {
    "original_url": "https://example.com/blog/article",
    "author": "John Doe",
    "date": "2025-01-10",
    "sitename": "Example Blog"
  },
  "status": "indexed"
}
```

**Response:**
```json
{
  "source_id": "text_abc123",
  "status": "indexed",
  "topics": ["topic1", "topic2"],
  "summary": "AI-generated summary..."
}
```

---

#### 2.1.4 Delete Source from Brain

```
DELETE /brain/sources/{source_id}
```

**Response:**
```json
{
  "deleted": true,
  "source_id": "dQw4w9WgXcQ"
}
```

---

#### 2.1.5 Create Source from URL

```
POST /brain/sources/url
```

Extracts main content from a URL and creates a Brain source.

**Request Body:**
```json
{
  "url": "https://example.com/article",
  "title": "Optional custom title",
  "tags": ["optional", "tags"],
  "extract_options": {
    "include_tables": true,
    "include_links": true,
    "include_images": false
  }
}
```

**Response:**
```json
{
  "source_id": "src_abc123",
  "title": "Article Title",
  "source_type": "url",
  "created_at": "2024-01-15T10:00:00Z",
  "summary": "AI-generated summary...",
  "topics": ["technology", "programming"],
  "tags": ["optional", "tags"],
  "word_count": 1500,
  "source_metadata": {
    "original_url": "https://example.com/article",
    "author": "John Doe",
    "sitename": "Example Blog"
  }
}
```

**Error Responses:**
- `400 Bad Request`: YouTube URLs blocked (use video processing)
- `400 Bad Request`: Private/local URLs blocked
- `400 Bad Request`: Invalid URL format
- `500 Internal Server Error`: Extraction failed

---

#### 2.1.6 Update Source Tags/Topics

```
PATCH /brain/sources/{source_id}
```

**Request Body:**
```json
{
  "tags": ["updated", "tags"],
  "topics": ["new", "topics"]
}
```

---

### 2.2 Vision-Based Generation

#### 2.2.1 Generate from Vision

```
POST /brain/generate/vision
```

User provides their idea/vision, system matches sources and generates content.

**Request Body:**
```json
{
  "vision": "I want to create a post about productivity hacks for busy entrepreneurs",
  "content_types": ["reel", "image_carousel"],
  "max_sources": 3,
  "style_preset": "professional_business",
  "custom_style": null
}
```

**Response:**
```json
{
  "session_id": "sess_abc123",
  "matched_sources": [
    {
      "source_id": "video123",
      "title": "10 Productivity Tips",
      "match_score": 0.92,
      "relevant_snippet": "..."
    },
    {
      "source_id": "doc456",
      "title": "Entrepreneur Guide",
      "match_score": 0.85,
      "relevant_snippet": "..."
    }
  ],
  "content_pieces": [
    {
      "content_id": "brain_001",
      "content_type": "reel",
      "source_ids": ["video123", "doc456"],
      "title": "5 Productivity Hacks...",
      "hook": "...",
      "script_body": "...",
      "caption": "...",
      "hashtags": ["#productivity"]
    }
  ],
  "generation_notes": "Combined insights from 2 sources based on your vision"
}
```

---

### 2.3 Full AI Mode Generation

#### 2.3.1 Generate from Selected Sources

```
POST /brain/generate/auto
```

User selects sources, AI autonomously generates content.

**Request Body:**
```json
{
  "source_ids": ["video123", "doc456"],
  "mode": "single",
  "content_types": ["reel", "image_carousel", "tweet"],
  "style_preset": "professional_business"
}
```

**Mode Options:**
- `single`: Generate 1 best content piece
- `multiple`: Generate exact `count` pieces
- `auto`: AI determines optimal count

For `multiple` mode:
```json
{
  "source_ids": ["video123"],
  "mode": "multiple",
  "count": 5,
  "content_types": ["reel"]
}
```

For `auto` mode:
```json
{
  "source_ids": ["video123", "video456"],
  "mode": "auto",
  "content_types": ["reel", "tweet"]
}
```

**Response:**
```json
{
  "session_id": "sess_xyz789",
  "mode": "auto",
  "source_count": 2,
  "generated_count": 4,
  "content_pieces": [
    {
      "content_id": "brain_auto_001",
      "content_type": "reel",
      "source_ids": ["video123"],
      "title": "...",
      ...
    }
  ],
  "generation_notes": "Generated 4 pieces: 2 reels, 2 tweets based on source richness"
}
```

---

#### 2.3.2 Hybrid Source Selection

```
POST /brain/generate/hybrid
```

Combine user-selected sources with AI-discovered sources.

**Request Body:**
```json
{
  "user_source_ids": ["video123", "doc456"],
  "ai_augment": {
    "enabled": true,
    "hint": "find more sources about social media marketing",
    "max_additional": 3,
    "min_score": 0.7
  },
  "mode": "multiple",
  "count": 5,
  "content_types": ["reel", "image_carousel"],
  "style_preset": "professional_business"
}
```

**AI Augment Options:**

| Option | Description |
|--------|-------------|
| `hint` | Topic/keyword for AI to find related sources |
| `max_additional` | Max sources AI can add (default: 3) |
| `min_score` | Minimum relevance score for AI sources (default: 0.7) |
| `strategy` | `augment` (add to user), `fill` (reach count), `support` (context only) |

**Strategy Examples:**

`augment` - AI adds related sources:
```json
{
  "user_source_ids": ["video123"],
  "ai_augment": {
    "enabled": true,
    "hint": "email marketing",
    "strategy": "augment",
    "max_additional": 3
  }
}
```

`fill` - AI fills to reach target source count:
```json
{
  "user_source_ids": ["video123"],
  "ai_augment": {
    "enabled": true,
    "strategy": "fill",
    "target_source_count": 5
  }
}
```

`support` - AI sources used for context only (not primary content):
```json
{
  "user_source_ids": ["video123", "video456"],
  "ai_augment": {
    "enabled": true,
    "hint": "statistics and data",
    "strategy": "support",
    "max_additional": 2
  }
}
```

**Response:**
```json
{
  "session_id": "sess_hybrid_001",
  "sources": {
    "user_selected": [
      {"source_id": "video123", "title": "Marketing Basics"}
    ],
    "ai_discovered": [
      {"source_id": "video789", "title": "Social Media Tips", "match_score": 0.89},
      {"source_id": "doc234", "title": "Email Campaigns", "match_score": 0.82}
    ],
    "total_count": 3
  },
  "content_pieces": [
    {
      "content_id": "hybrid_001",
      "content_type": "reel",
      "primary_source_ids": ["video123"],
      "supporting_source_ids": ["video789"],
      "title": "...",
      ...
    }
  ],
  "generation_notes": "Used 1 user source + 2 AI-discovered sources"
}
```

---

### 2.4 Brain Search

#### 2.4.1 Semantic Search

```
POST /brain/search
```

Search Brain sources using semantic similarity.

**Request Body:**
```json
{
  "query": "tips for growing an e-commerce business",
  "limit": 10,
  "source_types": ["youtube", "document"],
  "min_score": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "source_id": "video123",
      "title": "E-commerce Growth Strategies",
      "score": 0.94,
      "snippet": "Relevant excerpt from content...",
      "topics": ["ecommerce", "growth"]
    }
  ],
  "total": 5
}
```

---

## 3. Classic Endpoints

### 2.1 Health Check

```
GET /
```

**Response:**
```json
{
  "message": "Welcome to the FastAPI Repurpose API"
}
```

---

### 2.2 Transcription

#### 2.2.1 Basic Transcription

```
POST /transcribe/
```

Extract transcript from YouTube video.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "preferences": null
}
```

**Response:**
```json
{
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "transcript": "Full transcript text...",
  "status": "processed"
}
```

**Error Responses:**
- `400`: Invalid video ID format
- `404`: Video not found or no transcript available
- `500`: Transcript extraction failed

---

#### 2.2.2 Enhanced Transcription

```
POST /transcribe-enhanced/
```

Enhanced transcription with metadata and language info.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "preferences": {
    "prefer_manual": true,
    "require_english": false,
    "enable_translation": true,
    "fallback_languages": ["en", "es", "fr", "de"]
  }
}
```

**Response:**
```json
{
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "transcript": "Full transcript text...",
  "transcript_metadata": {
    "language_code": "en",
    "language": "English",
    "is_generated": false,
    "is_translated": false,
    "priority": "MANUAL_ENGLISH",
    "translation_source_language": null,
    "confidence_score": 1.0,
    "processing_notes": []
  },
  "available_languages": ["en", "es", "fr"],
  "status": "success"
}
```

---

#### 2.2.3 Transcript Analysis

```
GET /analyze-transcripts/{video_id}
```

Analyze available transcripts for a video.

**Response:**
```json
{
  "youtube_video_id": "dQw4w9WgXcQ",
  "available_transcripts": [
    {
      "language_code": "en",
      "language": "English",
      "is_generated": false,
      "is_translatable": true
    }
  ],
  "recommended_approach": "manual_english",
  "processing_notes": [
    "Manual English transcript available - highest quality"
  ]
}
```

---

### 2.3 Video Processing

#### 2.3.1 Process Single Video

```
POST /process-video/
```

Generate social media content from YouTube video.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "force_regenerate": false,
  "style_preset": "professional_business",
  "custom_style": null
}
```

Or with custom style:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "force_regenerate": true,
  "style_preset": null,
  "custom_style": {
    "target_audience": "tech entrepreneurs",
    "call_to_action": "Subscribe for startup insights",
    "content_goal": "education",
    "language": "English",
    "tone": "Inspirational",
    "additional_instructions": "Use startup terminology",
    "content_config": {
      "min_ideas": 10,
      "max_ideas": 15,
      "field_limits": {
        "carousel_slide_text_max": 1000
      }
    }
  }
}
```

**Response:**
```json
{
  "id": 1,
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "transcript": "Full transcript...",
  "status": "completed",
  "ideas": [
    {
      "suggested_content_type": "reel",
      "suggested_title": "Top 5 Tips",
      "relevant_transcript_snippet": "...",
      "type_specific_suggestions": {}
    }
  ],
  "content_pieces": [
    {
      "content_id": "dQw4w9WgXcQ_001",
      "content_type": "reel",
      "title": "Top 5 Tips for Success",
      "caption": "...",
      "hook": "Want to know the secret?",
      "script_body": "...",
      "visual_suggestions": "...",
      "hashtags": ["#tips", "#success"]
    }
  ]
}
```

---

#### 2.3.2 Process Video with Streaming

```
POST /process-video-stream/
```

Same as `/process-video/` but returns Server-Sent Events (SSE) for real-time progress.

**Response:** `text/event-stream`

```
data: {"status": "started", "message": "Starting video processing...", "progress": 0}

data: {"status": "fetching_info", "message": "Fetching video information...", "progress": 10}

data: {"status": "transcribing", "message": "Extracting English transcript...", "progress": 30}

data: {"status": "generating_content", "message": "Generating content ideas...", "progress": 60}

data: {"status": "complete", "progress": 100, "data": {...}}
```

---

#### 2.3.3 Bulk Video Processing

```
POST /process-videos-bulk/
```

Process multiple videos in sequence.

**Request Body:**
```json
{
  "video_ids": ["VIDEO_ID_1", "VIDEO_ID_2", "VIDEO_ID_3"]
}
```

**Response:**
```json
[
  {
    "video_id": "VIDEO_ID_1",
    "status": "success",
    "details": "Processed successfully.",
    "data": { /* ProcessVideoResponse */ }
  },
  {
    "video_id": "VIDEO_ID_2",
    "status": "error",
    "details": "HTTP 404: Video not found",
    "data": null
  }
]
```

---

### 2.4 Document Processing

#### 2.4.1 Process Document

```
POST /process-document/
```

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file`: Document file (TXT, MD, DOCX, PDF)
- `force_regenerate`: boolean (default: false)
- `style_preset`: string (optional)
- `custom_style`: JSON string (optional)

**Response:** Same as `/process-video/`

---

#### 2.4.2 Process Document with Streaming

```
POST /process-document-stream/
```

Same as `/process-document/` but returns SSE for progress.

---

### 2.5 Content Management

#### 2.5.1 List All Videos

```
GET /videos/?skip=0&limit=100
```

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Max results (default: 100)

**Response:**
```json
{
  "videos": [
    {
      "id": 1,
      "youtube_video_id": "dQw4w9WgXcQ",
      "title": "Video Title",
      "transcript": "...",
      "status": "completed",
      "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
      "created_at": "2026-01-12T10:00:00",
      "ideas": [],
      "content_pieces": []
    }
  ],
  "total": 1
}
```

---

#### 2.5.2 Edit Content

```
POST /edit-content/
```

Edit generated content using natural language prompts.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "content_piece_id": "dQw4w9WgXcQ_001",
  "edit_prompt": "Make the tone more casual and add emojis",
  "content_type": "reel"
}
```

**Response:**
```json
{
  "success": true,
  "content_piece_id": "dQw4w9WgXcQ_001",
  "original_content": { /* original piece */ },
  "edited_content": { /* modified piece */ },
  "changes_made": ["'caption' changed", "'hook' changed"],
  "error_message": null
}
```

---

### 2.6 Configuration

#### 2.6.1 Get Style Presets

```
GET /content-styles/presets/
```

**Response:**
```json
{
  "presets": {
    "ecommerce_entrepreneur": {
      "name": "ecommerce_entrepreneur",
      "description": "For e-commerce and Shopify store owners",
      "target_audience": "...",
      ...
    },
    "professional_business": {...}
  }
}
```

---

#### 2.6.2 Get Specific Preset

```
GET /content-styles/presets/{preset_name}
```

**Response:**
```json
{
  "name": "professional_business",
  "description": "Professional business content",
  "target_audience": "business professionals",
  "call_to_action": "Contact us for consultation",
  "content_goal": "lead_generation",
  "language": "English",
  "tone": "Professional",
  "content_config": {...}
}
```

---

#### 2.6.3 Get Default Configuration

```
GET /content-config/default
```

**Response:**
```json
{
  "min_ideas": 6,
  "max_ideas": 8,
  "content_pieces_per_idea": 1,
  "field_limits": {
    "reel_title_max": 100,
    "carousel_slide_text_max": 800,
    ...
  }
}
```

---

#### 2.6.4 Get Current Configuration

```
GET /content-config/current
```

Returns the currently active configuration (may differ from default if overridden).

---

## 3. Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Schema mismatch |
| 500 | Internal Server Error |

---

## 4. CORS Configuration

Allowed origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

All methods and headers are allowed for development.

---

## 5. Rate Limiting

Currently handled at the AI provider level (Gemini):
- 10 requests per minute
- 250 requests per day (free tier)

Future: Implement application-level rate limiting via `REQUESTS_PER_MINUTE` env var.
