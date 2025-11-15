# Content Repurposer API - Frontend Developer Guide

## Overview

This is an internal API that repurposes content from **YouTube videos** and **documents** (TXT, MD, DOCX, PDF) into social media posts (Reels, Image Carousels, Tweets). The API extracts text/transcripts, generates content ideas, and creates ready-to-use social media content pieces with customizable styles.

**Base URL:** `http://localhost:8002`

**API Type:** RESTful JSON API

**Authentication:** None (Internal API)

**CORS:** Enabled for `http://localhost:3000` and `http://127.0.0.1:3000`

---

## Quick Start

### Check API Status
```
GET /
```

Returns a welcome message to confirm the API is running.

**Response:**
```json
{
  "message": "Welcome to the FastAPI Repurpose API"
}
```

---

## Core Concepts

### Content Processing Flow

1. **Input** - YouTube video URL OR document file (TXT/MD/DOCX/PDF)
2. **Extraction** - Extract transcript from video OR text from document
3. **Content Generation** - Generate content ideas from extracted text
4. **Content Creation** - Create specific content pieces (Reels, Carousels, Tweets)
5. **Storage** - All processed content stored in database

### Content Types Supported

- **Reel** - Short-form video scripts with hooks, captions, visual suggestions
- **Image Carousel** - Multi-slide carousel posts with titles and descriptions
- **Tweet** - Twitter/X posts with hashtags and calls-to-action

### Content Style Presets

The API supports multiple content styles that determine the tone, language, and target audience of generated content:

- `ecommerce_entrepreneur` - Roman Urdu, for Shopify/DTC brands
- `professional_business` - English, corporate tone
- `social_media_casual` - English, casual and fun
- `educational_content` - English, informative
- `fitness_wellness` - English, motivational

---

## Endpoints Reference

### 1. Content Style Management

#### Get All Style Presets
```
GET /content-styles/presets/
```

Returns all available content style presets with their configurations.

**Response Structure:**
```json
{
  "presets": {
    "preset_key": {
      "name": "Display Name",
      "description": "Description of the style",
      "target_audience": "Who this style is for",
      "language": "Output language",
      "tone": "Content tone"
    }
  }
}
```

**Use Case:** Display available styles in a dropdown/selector in your UI.

---

#### Get Specific Preset Details
```
GET /content-styles/presets/{preset_name}
```

**Path Parameters:**
- `preset_name` - Key of the preset (e.g., `ecommerce_entrepreneur`)

**Response:**
```json
{
  "name": "E-commerce Entrepreneur",
  "description": "For e-commerce entrepreneurs and Shopify store owners",
  "target_audience": "ecom entrepreneurs, Shopify store owners, and DTC brands...",
  "call_to_action": "DM us to launch or fix your store...",
  "content_goal": "education, lead_generation, brand_awareness",
  "language": "Roman Urdu",
  "tone": "Educational and engaging",
  "additional_instructions": "...",
  "content_config": {
    "min_ideas": 6,
    "max_ideas": 8,
    "content_pieces_per_idea": 1,
    "field_limits": {
      "reel_title_max": 100,
      "reel_caption_max": 300,
      "carousel_slide_text_max": 800,
      ...
    }
  }
}
```

**Error Response (404):**
```json
{
  "detail": "Style preset 'invalid_name' not found"
}
```

---

#### Get Default Content Configuration
```
GET /content-config/default
```

Returns the default field length limits and content generation settings.

**Response:**
```json
{
  "description": "Default configuration for content generation",
  "field_limits": {
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
  },
  "min_ideas": 6,
  "max_ideas": 8,
  "content_pieces_per_idea": 1,
  "note": "These are the default settings. You can override them in custom_style.content_config when processing videos/documents."
}
```

**Use Case:** 
- Display configuration options in your UI
- Show users current limits for each content type
- Use as reference when creating custom configurations

**Field Limits Explained:**
- `carousel_slide_text_max: 800` - The slide text is the **primary content** field for carousels and should contain detailed, comprehensive information (400-800 characters recommended)
- `carousel_slide_heading_max: 100` - Short label/title for each slide
- Carousel slides now generate much longer, more detailed content by default

---

#### Get Current Active Configuration
```
GET /content-config/current
```

Returns the currently active content generation configuration (useful for debugging).

**Response:**
```json
{
  "description": "Currently active configuration for content generation",
  "field_limits": {
    "carousel_slide_text_max": 800,
    ...
  },
  "note": "This shows the active configuration. To use custom limits, pass them in the content_config parameter when processing."
}
```

---

### 2. Video Transcription

#### Basic Transcription
```
POST /transcribe/
```

Extracts English transcript from a YouTube video. This is the simplest transcription endpoint.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
  "transcript": "Full transcript text here...",
  "status": "processed"
}
```

**Response Time:** 50ms-15s (depending on cache)

**Notes:**
- Automatically fetches English transcript (manual or auto-generated)
- Results are cached in database
- Subsequent calls for same video return instantly

---

#### Enhanced Transcription
```
POST /transcribe-enhanced/
```

More detailed transcription with metadata and preferences support.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "preferences": {
    "prefer_manual": true,
    "allow_auto_generated": true,
    "allow_translated": true
  }
}
```

**Request Fields:**
- `video_id` (required) - YouTube video ID (11 characters)
- `preferences` (optional) - Transcript selection preferences
  - `prefer_manual` - Prefer manually created transcripts over auto-generated
  - `allow_auto_generated` - Allow auto-generated transcripts
  - `allow_translated` - Allow translated transcripts

**Response:**
```json
{
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Video title",
  "transcript": "Full transcript text...",
  "transcript_metadata": {
    "language_code": "en",
    "language": "English",
    "is_generated": false,
    "is_translated": false,
    "priority": "MANUAL_ENGLISH",
    "translation_source_language": null,
    "confidence_score": 1.0,
    "processing_notes": ["Details about transcript selection"]
  },
  "available_languages": ["en", "de", "ja"],
  "status": "success"
}
```

**Priority Levels:**
1. `MANUAL_ENGLISH` - Manually created English transcript (highest quality)
2. `AUTO_ENGLISH` - Auto-generated English transcript
3. `MANUAL_TRANSLATED` - Manually created non-English, translated to English
4. `AUTO_TRANSLATED` - Auto-generated non-English, translated to English

---

#### Analyze Available Transcripts
```
GET /analyze-transcripts/{video_id}
```

Analyzes all available transcripts for a video without fetching the actual transcript text.

**Path Parameters:**
- `video_id` - YouTube video ID

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
    },
    {
      "language_code": "de-DE",
      "language": "German (Germany)",
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

**Recommended Approaches:**
- `manual_english` - Best quality available
- `auto_english` - Good quality, auto-generated
- `manual_translated` - Requires translation
- `auto_translated` - Lower quality, requires translation

**Use Case:** Show users which transcript quality they'll get before processing.

---

### 3. Video Processing

#### Process Video (Non-Streaming)
```
POST /process-video/
```

Complete video processing: transcription → content ideas → content pieces. This is a blocking request that returns when processing is complete.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "force_regenerate": false,
  "style_preset": "ecommerce_entrepreneur",
  "custom_style": {
    "target_audience": "young entrepreneurs",
    "call_to_action": "Sign up for our course",
    "content_goal": "education",
    "language": "English",
    "tone": "Motivational",
    "additional_instructions": "Use emojis and keep it energetic",
    "content_config": {
      "min_ideas": 5,
      "max_ideas": 10,
      "field_limits": {
        "carousel_slide_text_max": 1000,
        "carousel_min_slides": 5,
        "carousel_max_slides": 10
      }
    }
  }
}
```

**Request Fields:**
- `video_id` (required) - YouTube video ID
- `force_regenerate` (optional, default: false) - Regenerate content even if exists
- `style_preset` (optional) - Use a predefined style preset
- `custom_style` (optional) - Override with custom style configuration
  - `target_audience` - Who the content is for
  - `call_to_action` - CTA to include
  - `content_goal` - Purpose of the content
  - `language` - Output language
  - `tone` - Content tone/style
  - `additional_instructions` - Extra guidance for content generation
  - `content_config` (optional) - Configure content generation behavior
    - `min_ideas` - Minimum number of content ideas (default: 6)
    - `max_ideas` - Maximum number of content ideas (default: 8)
    - `field_limits` (optional) - Override field length limits per content type
      - See `/content-config/default` endpoint for all available limits
      - Common overrides:
        - `carousel_slide_text_max` (default: 800) - Length of carousel slide content
        - `carousel_min_slides` (default: 4) - Minimum carousel slides
        - `carousel_max_slides` (default: 8) - Maximum carousel slides
        - `reel_script_max` (default: 2000) - Length of reel scripts

**Important:** 
- Use either `style_preset` OR `custom_style`, not both. 
- If neither provided, uses default ecommerce style.
- The `content_config` can be nested in `custom_style` to customize limits per request
- Carousel slide text is now generated with much more detail by default (400-800 chars)

**Response:**
```json
{
  "id": 1,
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up...",
  "transcript": "Full transcript...",
  "status": "completed",
  "ideas": [
    {
      "suggested_content_type": "reel",
      "suggested_title": "Apne Ecom Dream Ko Kabhi Na Chhodo!",
      "relevant_transcript_snippet": "Never gonna give you up",
      "type_specific_suggestions": {
        "script": "Full script text...",
        "visual_elements": "Description of visuals...",
        "call_to_action": "DM us..."
      }
    }
  ],
  "content_pieces": [
    {
      "content_id": "dQw4w9WgXcQ_001",
      "content_type": "reel",
      "title": "Content title",
      "caption": "Full caption text",
      "hook": "Opening hook",
      "script_body": "Full script with scene descriptions",
      "visual_suggestions": "Detailed visual guidance",
      "hashtags": ["#tag1", "#tag2"],
      "call_to_action": "Action text",
      "estimated_duration": "30-45 seconds",
      "music_suggestion": "Upbeat, energetic",
      "target_audience": "ecom entrepreneurs"
    }
  ]
}
```

**Response Time:** 30-60 seconds for new videos, <1 second for cached videos

**Status Field Values:**
- `processing` - Currently being processed
- `completed` - Successfully processed
- `processed` - Already processed (cached)
- `failed` - Processing failed

**Content Piece Types:**

**Reel Fields:**
- `content_id` - Unique identifier
- `content_type` - Always "reel"
- `title` - Title for the reel
- `caption` - Instagram/TikTok caption
- `hook` - Opening line (first 3 seconds)
- `script_body` - Complete script with scene descriptions
- `visual_suggestions` - Guidance for video creator
- `hashtags` - Array of relevant hashtags
- `call_to_action` - CTA text
- `estimated_duration` - Expected video length
- `music_suggestion` - Music style recommendation
- `target_audience` - Who this content is for

**Image Carousel Fields:**
- `content_id` - Unique identifier
- `content_type` - Always "image_carousel"
- `title` - Main title (max 100 chars)
- `caption` - Post caption (max 300 chars)
- `slides` - Array of slide objects (4-8 slides):
  - `slide_number` - Sequential slide number
  - `step_number` - Step number in the carousel
  - `step_heading` - Short heading/label for the slide (max 100 chars)
  - `text` - **PRIMARY CONTENT FIELD** - Detailed, comprehensive slide content (400-800 chars)
    - This is where the value is - should contain 3-5 sentences with specifics, examples, and actionable information
    - Not just a caption - think mini-article or detailed explanation
- `hashtags` - Array of hashtags
- `call_to_action` - CTA text
- `design_notes` - Design guidance
- `target_audience` - Intended audience

**Note on Carousel Slides:** The `text` field is the main content carrier and is now generated with much more detail by default. The `step_heading` is just a short label, while `text` contains the substantive information.

**Tweet Fields:**
- `content_id` - Unique identifier
- `content_type` - Always "tweet"
- `tweet_text` - Main tweet content (280 char limit)
- `thread_tweets` - Array of follow-up tweets (if thread)
- `hashtags` - Array of hashtags
- `call_to_action` - CTA text
- `engagement_hooks` - Tips to boost engagement
- `target_audience` - Intended audience

---

#### Process Video (Streaming)
```
POST /process-video-stream/
```

Same as `/process-video/` but returns Server-Sent Events (SSE) for real-time progress updates.

**Request Body:** Same as `/process-video/`

**Response Type:** `text/event-stream`

**Event Format:**
```
data: {"status": "started", "message": "Starting video processing...", "progress": 0}

data: {"status": "fetching_info", "message": "Fetching video information...", "progress": 10}

data: {"status": "transcribing", "message": "Extracting English transcript...", "progress": 30}

data: {"status": "transcript_ready", "message": "English transcript extracted (MANUAL_ENGLISH)", "progress": 50}

data: {"status": "generating_content", "message": "Generating content ideas...", "progress": 60}

data: {"status": "ideas_generated", "message": "Content ideas generated, creating pieces...", "progress": 75}

data: {"status": "content_generated", "message": "Content pieces generated successfully", "progress": 90}

data: {"status": "complete", "progress": 100, "data": {...full response object...}}
```

**Status Values:**
- `started` - Processing initiated
- `found_existing` - Video already processed, loading from cache
- `fetching_info` - Getting video title and metadata
- `transcribing` - Extracting transcript
- `transcript_ready` - Transcript extracted successfully
- `generating_content` - Creating content ideas
- `ideas_generated` - Ideas created, generating pieces
- `content_generated` - Content pieces created
- `complete` - All done, data included in event
- `error` - Processing failed, message in event

**Use Case:** Display a progress bar or step indicator in your UI.

**Important:** The final `complete` event contains the full response object in the `data` field.

---

#### Bulk Video Processing
```
POST /process-videos-bulk/
```

Process multiple videos in a single request. Videos are processed sequentially.

**Request Body:**
```json
{
  "video_ids": ["dQw4w9WgXcQ", "jNQXAC9IVRw", "9bZkp7q19f0"]
}
```

**Response:**
```json
[
  {
    "video_id": "dQw4w9WgXcQ",
    "status": "success",
    "details": "Processed successfully.",
    "data": {
      "id": 1,
      "youtube_video_id": "dQw4w9WgXcQ",
      "title": "...",
      "status": "completed",
      "ideas": [...],
      "content_pieces": [...]
    }
  },
  {
    "video_id": "invalid_id",
    "status": "error",
    "details": "HTTP 404: Video not found"
  }
]
```

**Response Array Items:**
- `video_id` - The video that was processed
- `status` - "success" or "error"
- `details` - Human-readable status message
- `data` - Full video response object (only if successful)

**Processing Time:** 30-60 seconds per new video

**Note:** This endpoint can take several minutes if processing multiple new videos. Consider using individual `/process-video-stream/` calls for better UX.

---

### 4. Video Management

#### Get All Videos
```
GET /videos/?skip=0&limit=10
```

Retrieve all processed videos from the database with pagination.

**Query Parameters:**
- `skip` (optional, default: 0) - Number of videos to skip
- `limit` (optional, default: 100, max: 100) - Number of videos to return

**Response:**
```json
{
  "videos": [
    {
      "id": 1,
      "youtube_video_id": "dQw4w9WgXcQ",
      "title": "Rick Astley - Never Gonna Give You Up...",
      "transcript": "Full transcript...",
      "status": "processed",
      "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
      "created_at": "2025-11-15T13:00:00",
      "ideas": [],
      "content_pieces": []
    }
  ],
  "total": 10
}
```

**Response Fields:**
- `videos` - Array of video objects
- `total` - Total number of videos returned (not total in database)

**Video Object Fields:**
- `id` - Internal database ID
- `youtube_video_id` - YouTube video ID
- `title` - Video title
- `transcript` - Full transcript text
- `status` - Processing status
- `thumbnail_url` - YouTube thumbnail URL (maxresdefault quality)
- `video_url` - Full YouTube watch URL
- `created_at` - When video was first processed (ISO 8601 format)
- `ideas` - Array of content ideas (parsed from database)
- `content_pieces` - Array of generated content pieces (parsed from database)

**Pagination:**
- Use `skip` to paginate through results
- Maximum `limit` is 100 per request
- To get next page: `skip = skip + limit`

---

### 5. Content Editing

#### Edit Content Piece
```
POST /edit-content/
```

Edit a generated content piece using natural language instructions.

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "content_piece_id": "dQw4w9WgXcQ_001",
  "edit_prompt": "Make the content more engaging and add emojis",
  "content_type": "reel"
}
```

**Request Fields:**
- `video_id` (required) - YouTube video ID
- `content_piece_id` (required) - ID of the content piece to edit
- `edit_prompt` (required) - Natural language description of changes
- `content_type` (required) - Type: "reel", "image_carousel", or "tweet"

**Response:**
```json
{
  "success": true,
  "content_piece_id": "dQw4w9WgXcQ_001",
  "original_content": {
    "content_id": "dQw4w9WgXcQ_001",
    "content_type": "reel",
    "title": "Original title",
    "caption": "Original caption..."
  },
  "edited_content": {
    "content_id": "dQw4w9WgXcQ_001",
    "content_type": "reel",
    "title": "New engaging title! 🎬",
    "caption": "New caption with emojis 🚀..."
  },
  "changes_made": [
    "Added emojis to title and caption",
    "Made language more engaging and conversational",
    "Shortened some sentences for better flow"
  ],
  "error_message": null
}
```

**Error Response:**
```json
{
  "success": false,
  "content_piece_id": "dQw4w9WgXcQ_001",
  "original_content": null,
  "edited_content": null,
  "changes_made": null,
  "error_message": "Content piece with ID 'dQw4w9WgXcQ_001' not found"
}
```

**Edit Prompt Examples:**
- "Make it shorter"
- "Add more emojis"
- "Change tone to be more professional"
- "Remove the technical jargon"
- "Make the hook more attention-grabbing"
- "Translate to English" (if original is in Roman Urdu)

**Processing Time:** 5-15 seconds

**Note:** The edited content automatically replaces the original in the database.

---

## Error Responses

All endpoints return standard HTTP status codes and JSON error responses.

### Error Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

**200 OK** - Request successful

**404 Not Found** - Resource not found
```json
{
  "detail": "Video with ID 'invalid_id' not found"
}
```

**422 Unprocessable Entity** - Invalid request data
```json
{
  "detail": [
    {
      "loc": ["body", "video_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "An unexpected error occurred while processing video ID xyz"
}
```

---

## Data Models

### Video ID Format
YouTube video IDs are 11 characters, alphanumeric with hyphens and underscores.

**Valid:** `dQw4w9WgXcQ`, `jNQXAC9IVRw`

**Invalid:** `https://youtube.com/watch?v=...` (use ID only)

**Extraction:** If you have a full URL, extract the `v` parameter value.

### Content ID Format
Content IDs follow the pattern: `{video_id}_{sequence_number}`

**Examples:** `dQw4w9WgXcQ_001`, `dQw4w9WgXcQ_002`

### Thumbnail URLs
Thumbnails are generated from YouTube CDN:
```
https://img.youtube.com/vi/{video_id}/maxresdefault.jpg
```

**Available qualities:**
- `maxresdefault.jpg` - 1920×1080 (may not exist for all videos)
- `hqdefault.jpg` - 480×360
- `mqdefault.jpg` - 320×180
- `default.jpg` - 120×90

---

## Performance Characteristics

### Response Times (Typical)

| Endpoint | Cached | New |
|----------|--------|-----|
| Basic endpoints | <100ms | N/A |
| Content style presets | <100ms | N/A |
| Transcribe (basic) | <100ms | 5-15s |
| Transcribe (enhanced) | <100ms | 10-20s |
| Analyze transcripts | <100ms | 2-5s |
| Get all videos | <100ms | N/A |
| Process video | <1s | 30-60s |
| Process video stream | <1s | 30-60s |
| Bulk processing | Varies | 30-60s per video |
| Edit content | N/A | 5-15s |

### Rate Limits
No rate limiting currently implemented. This is an internal API.

### Caching Behavior
- Transcripts are cached indefinitely in the database
- Once a video is processed, subsequent calls return cached data instantly
- Use `force_regenerate: true` to bypass cache and regenerate content

---

## Best Practices

### Video Processing
1. **Check if video exists first:** Call `GET /videos/` or try transcription first
2. **Use streaming for new videos:** Better UX with progress updates
3. **Don't regenerate unnecessarily:** Use cached data when possible
4. **Handle long processing times:** New videos take 30-60 seconds

### Content Style Selection
1. **Let users choose style:** Present style presets in a dropdown
2. **Preview style details:** Show target audience and language before processing
3. **Custom styles for power users:** Provide advanced form for custom style

### Error Handling
1. **Handle 404s gracefully:** Video not found, invalid preset, etc.
2. **Retry on 500s:** Server errors may be transient
3. **Validate video IDs client-side:** Check format before making requests
4. **Show meaningful error messages:** Parse error details for user-friendly messages

### Performance
1. **Implement timeouts:** Set at least 60 seconds for processing endpoints
2. **Show loading states:** Processing takes time, keep users informed
3. **Cache video lists:** Don't fetch `/videos/` on every page load
4. **Paginate video lists:** Don't load all videos at once

---

## Common Integration Patterns

### Pattern 1: Quick Transcription Only
1. User enters YouTube URL
2. Extract video ID
3. Call `POST /transcribe/` with video ID
4. Display transcript to user

### Pattern 2: Full Content Generation
1. User enters YouTube URL and selects style preset
2. Extract video ID
3. Call `POST /process-video-stream/` with video ID and style
4. Display progress bar updating with SSE events
5. When complete, display generated content pieces
6. Allow user to edit individual pieces with `POST /edit-content/`

### Pattern 3: Video Library
1. On page load, call `GET /videos/?skip=0&limit=20`
2. Display video cards with thumbnails and titles
3. Implement "Load More" with pagination
4. User clicks video to view full details and content

### Pattern 4: Batch Processing
1. User uploads CSV of YouTube URLs
2. Extract video IDs
3. Call `POST /process-videos-bulk/` with all IDs
4. Display progress and results for each video
5. Handle individual failures gracefully

---

## API Documentation

Interactive API documentation is available at:

**Swagger UI:** http://localhost:8002/docs

**ReDoc:** http://localhost:8002/redoc

**OpenAPI Spec:** http://localhost:8002/openapi.json

Use these for testing endpoints and viewing detailed schema information.

---

## Important Notes

### YouTube Video Requirements
- Video must have an available transcript (manual or auto-generated)
- Video must be public or unlisted (not private)
- Age-restricted videos may not work
- Live streams and premieres may not have transcripts

### Language Handling
- API prioritizes English transcripts automatically
- If English not available, translates from best available language
- Some styles generate content in Roman Urdu (Urdu in English alphabet)
- Check style preset language before processing

### Content Generation
- Content is generated using LLM (AI)
- Quality depends on transcript quality
- Short videos (<1 min) may produce less content
- Very long videos (>1 hour) work but take longer

### Database
- All processed data is stored permanently
- No automatic cleanup or expiration
- Content pieces are stored as JSON in database
- Videos can be re-processed with `force_regenerate: true`

### Limitations
- Maximum 100 videos per list request
- No built-in authentication (internal API only)
- No webhook support for async operations
- No bulk editing endpoint (edit one piece at a time)

---

## Support & Troubleshooting

### Common Issues

**"No transcript found for video"**
- Video doesn't have any available transcripts
- Try a different video

**"Timeout waiting for response"**
- Processing takes longer than expected
- Increase client timeout to at least 60 seconds

**"Invalid video ID"**
- Wrong format provided
- Extract 11-character ID from YouTube URL

**"Content piece not found"**
- Video hasn't been processed yet
- Wrong content_piece_id format
- Process video first with `/process-video/`

### Debugging
1. Check server logs at console where API is running
2. Use interactive docs at `/docs` to test endpoints
3. Verify request format matches documentation exactly
4. Check HTTP status codes for error types

---

## Version Information

**API Version:** 0.1.3

**Last Updated:** 2025-11-15

**Status:** Production Ready ✅

---

**End of API Guide**

---

## 6. Document Processing

### Upload and Process Document
```
POST /process-document/
```

Upload a document file (TXT, MD, DOCX, PDF) and generate social media content from its text.

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `file` (required) - The document file to upload
- `force_regenerate` (optional, default: false) - Regenerate even if document was previously processed
- `style_preset` (optional) - Name of a style preset to use
- `custom_style` (optional) - JSON string with custom style configuration
  - Same structure as in `/process-video/` endpoint
  - Can include `content_config` with `field_limits` to customize content generation
  - Example: `{"target_audience": "developers", "language": "English", "content_config": {"field_limits": {"carousel_slide_text_max": 1000}}}`

**Supported File Formats:**
- `.txt` - Plain text files
- `.md`, `.markdown` - Markdown files
- `.docx` - Microsoft Word documents
- `.pdf` - PDF documents

**Response:** Same as `/process-video/` endpoint

**Response Time:** 30-60 seconds for new documents

**Example using curl:**
```bash
curl -X POST http://localhost:8002/process-document/ \
  -F "file=@article.pdf" \
  -F "force_regenerate=false" \
  -F "style_preset=professional_business"
```

**Notes:**
- Maximum file size depends on server configuration
- PDF text extraction quality depends on PDF structure
- Scanned PDFs (images) won't work - text must be extractable
- Encrypted PDFs won't work

---

### Upload and Process Document (Streaming)
```
POST /process-document-stream/
```

Same as `/process-document/` but returns Server-Sent Events for real-time progress tracking.

**Content-Type:** `multipart/form-data`

**Form Fields:** Same as `/process-document/`

**Response Type:** `text/event-stream`

**Event Format:**
```
data: {"status": "started", "message": "Processing document...", "progress": 0}

data: {"status": "uploading", "message": "Reading file: article.pdf", "progress": 10}

data: {"status": "parsing", "message": "Extracting text from .pdf file...", "progress": 30}

data: {"status": "text_extracted", "message": "Extracted 5234 characters from PDF", "progress": 50}

data: {"status": "generating_content", "message": "Generating content ideas...", "progress": 60}

data: {"status": "ideas_generated", "message": "Generated 3 content ideas", "progress": 75}

data: {"status": "content_generated", "message": "Created 5 content pieces", "progress": 90}

data: {"status": "complete", "progress": 100, "data": {...full response...}}
```

**Status Values:**
- `started` - Processing initiated
- `uploading` - Reading uploaded file
- `parsing` - Extracting text from document
- `text_extracted` - Text successfully extracted
- `generating_content` - Creating content ideas
- `ideas_generated` - Ideas created, generating pieces
- `content_generated` - Content pieces created
- `complete` - All done, data included
- `error` - Processing failed

**Example using curl:**
```bash
curl -N -X POST http://localhost:8002/process-document-stream/ \
  -F "file=@notes.md" \
  -F "style_preset=ecommerce_entrepreneur"
```

**Use Case:** Perfect for showing upload and processing progress in UI

---

## Document vs Video Processing

Both document and video processing follow the same pipeline:

1. **Extract Text**
   - Videos: Get transcript from YouTube
   - Documents: Parse file and extract text

2. **Generate Ideas**
   - Same AI process for both
   - Uses extracted text to generate content ideas

3. **Create Content**
   - Same content generation for both
   - Produces Reels, Carousels, and Tweets

4. **Store Results**
   - Both stored in same database format
   - Can be retrieved via `/videos/` endpoint

**Key Differences:**
- Videos have `youtube_video_id` and metadata
- Documents use filename (without extension) as ID
- Documents stored with `document://filename` as URL
- Video thumbnails vs no thumbnails for documents

---

## Document Processing Best Practices

### File Preparation
1. **Clean Text:** Remove unnecessary formatting
2. **Structure:** Use headings and paragraphs
3. **Length:** Minimum 500 characters recommended
4. **Format:** Use formats that preserve text structure (DOCX, MD preferred over PDF)

### PDF Considerations
1. **Text-based PDFs only** - OCR/scanned PDFs won't work
2. **No encryption** - Encrypted PDFs cannot be processed
3. **Good structure** - PDFs with proper text layers work best
4. **Tables** - Text in tables may not extract perfectly

### Performance
- TXT/MD files: Fast parsing (< 1 second)
- DOCX files: Moderate (1-2 seconds)
- PDF files: Slower (2-5 seconds) depending on complexity

### Error Handling
```json
// Unsupported format
{
  "detail": "Unsupported file format: .doc. Supported: .txt, .md, .docx, .pdf"
}

// Empty or too short
{
  "detail": "Document appears to be empty or too short (< 50 characters)"
}

// Parsing failed
{
  "detail": "Failed to process document: [error details]"
}
```

---

