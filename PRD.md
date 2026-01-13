# Product Requirements Document (PRD)

## YouTube Content Repurposer

**Version:** 1.0  
**Last Updated:** January 2026

---

## 1. Product Overview

### 1.1 Summary

YouTube Content Repurposer is a tool that transforms YouTube videos and documents into engaging social media content using AI. It extracts transcripts from YouTube videos (or text from documents), analyzes the content, and generates ready-to-use social media assets including Instagram Reels scripts, Tweet threads, and Image Carousel content.

### 1.2 Target Users

- Content creators and influencers
- Social media managers
- Marketing teams and agencies
- E-commerce entrepreneurs
- Educators and course creators

### 1.3 Core Value Proposition

Turn long-form video content into multiple social media assets automatically, saving hours of manual content repurposing work while maintaining brand voice and style consistency.

---

## 2. Product Components

### 2.1 CLI Tool (`repurpose.py`)

A command-line interface for batch processing videos and documents.

**Key Features:**
- Process single or multiple YouTube videos
- Process document files (TXT, MD, DOCX, PDF)
- Read video lists from CSV/TXT files
- Configurable content generation parameters
- Rich console output with progress tracking
- Style presets for different content tones

**Usage Examples:**
```bash
# Single video
python repurpose.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Multiple videos
python repurpose.py "VIDEO_ID1,VIDEO_ID2,VIDEO_ID3"

# Document processing
python repurpose.py article.pdf

# With custom configuration
python repurpose.py videos.txt --carousel-text-max 1000 --min-ideas 10
```

### 2.2 REST API (`main.py`)

A FastAPI-based web service for programmatic access and frontend integration.

**Core Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/transcribe/` | POST | Extract transcript from YouTube video |
| `/transcribe-enhanced/` | POST | Enhanced transcription with metadata |
| `/process-video/` | POST | Generate content from video |
| `/process-video-stream/` | POST | Process video with SSE streaming |
| `/process-videos-bulk/` | POST | Batch process multiple videos |
| `/process-document/` | POST | Generate content from document upload |
| `/process-document-stream/` | POST | Document processing with SSE |
| `/edit-content/` | POST | Edit content with natural language |
| `/videos/` | GET | List all processed videos |
| `/analyze-transcripts/{video_id}` | GET | Analyze available transcripts |
| `/content-styles/presets/` | GET | Get style presets |
| `/content-config/default` | GET | Get default configuration |
| `/health/` | GET | Health check |

---

## 3. Generated Content Types

### 3.1 Instagram Reels

- **Title**: Catchy hook (max 100 chars)
- **Script**: Full spoken script (max 2000 chars)
- **Caption**: Instagram caption with CTAs (max 2200 chars)
- **Hashtags**: Relevant hashtags

### 3.2 Image Carousels

- **Title**: Carousel title (max 100 chars)
- **Caption**: Post caption (max 2200 chars)
- **Slides**: 4-15 slides with:
  - Step heading (max 100 chars)
  - Detailed text content (up to 800 chars per slide)
- **Hashtags**: Relevant hashtags

### 3.3 Tweets

- **Tweet Text**: Main tweet (max 280 chars)
- **Thread**: Optional thread continuation
- **Title**: Internal reference title

---

## 4. Key Features

### 4.1 Transcript Handling

- **English Preference**: Prioritizes manual English transcripts
- **Auto-Translation**: Translates non-English transcripts to English
- **Fallback Chain**: Manual English → Auto English → Translated Manual → Translated Auto
- **Metadata Tracking**: Language, type, confidence scores

### 4.2 Content Style Customization

**Style Presets:**
- `ecommerce_entrepreneur` - Roman Urdu for e-commerce audience
- `professional_business` - Corporate/business tone
- `social_media_casual` - Casual, engaging tone
- `educational_content` - Informative, teaching style
- `fitness_wellness` - Health and motivation focused

**Custom Style Parameters:**
- Target audience
- Call to action
- Content goals
- Language preference
- Tone specification
- Additional instructions

### 4.3 Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `carousel_slide_text_max` | 800 | Max chars per carousel slide |
| `carousel_min_slides` | 4 | Minimum slides per carousel |
| `carousel_max_slides` | 8 | Maximum slides per carousel |
| `reel_script_max` | 2000 | Max chars for reel scripts |
| `min_ideas` | 6 | Minimum content ideas generated |
| `max_ideas` | 8 | Maximum content ideas generated |

### 4.4 Smart Validation & Recovery

- Automatic validation of generated content
- Auto-retry on validation failures
- Field length enforcement
- Schema compliance checking

### 4.5 Natural Language Editing

Edit generated content using plain English prompts:
```json
{
  "video_id": "VIDEO_ID",
  "content_piece_id": "VIDEO_ID_001",
  "edit_prompt": "Make it more engaging and add emojis",
  "content_type": "reel"
}
```

---

## 5. Technical Architecture

### 5.1 Technology Stack

- **Runtime**: Python 3.9+
- **API Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **AI Provider**: Google Gemini API
- **Transcript Source**: YouTube Transcript API
- **Document Parsing**: python-docx, PyPDF2, markdown

### 5.2 Project Structure

```
repurpose-api/
├── main.py                 # FastAPI application
├── repurpose.py           # CLI tool & core logic
├── api/
│   ├── config.py          # Style presets & config
│   ├── models.py          # Pydantic models
│   └── routers/           # API route handlers
├── core/
│   ├── database.py        # DB models & connection
│   ├── content/           # Content models & prompts
│   └── services/          # Business logic services
├── tests/                 # Test suite
├── output/                # Generated content output
└── docs/                  # Documentation
```

### 5.3 Data Flow

1. **Input**: YouTube URL/ID or Document file
2. **Extraction**: Transcript/text extraction with language handling
3. **Idea Generation**: AI analyzes content, generates 6-8 content ideas
4. **Content Generation**: Each idea is expanded into full content piece
5. **Validation**: Content validated against schemas, auto-fixed if needed
6. **Storage**: Saved to database and/or CSV files
7. **Output**: JSON response (API) or CSV/JSON files (CLI)

---

## 6. Integration Requirements

### 6.1 Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
DATABASE_URL=sqlite:///./yt_repurposer.db
HOST=127.0.0.1
PORT=8002
DEBUG=false
LOG_LEVEL=INFO
MAX_CONTENT_PIECES=10
REQUESTS_PER_MINUTE=60
```

### 6.2 API Response Format

```json
{
  "id": 1,
  "youtube_video_id": "VIDEO_ID",
  "title": "Video Title",
  "transcript": "Full transcript text...",
  "status": "completed",
  "ideas": [...],
  "content_pieces": [
    {
      "content_id": "VIDEO_ID_001",
      "content_type": "reel",
      "title": "...",
      "script": "...",
      "caption": "...",
      "hashtags": [...]
    }
  ]
}
```

---

## 7. Output Files (CLI)

| File | Location | Content |
|------|----------|---------|
| `generated_content.csv` | `output/` | Reels and Tweets |
| `{video_id}_carousel_titles.csv` | `output/carousels/` | Carousel metadata |
| `{content_id}_slides.csv` | `output/slides/` | Individual carousel slides |
| `repurpose.log` | `output/` | Processing logs |

---

## 8. Non-Functional Requirements

### 8.1 Performance

- Single video processing: < 60 seconds
- Bulk processing: Parallel execution with thread pool (10 workers)
- Streaming endpoints for real-time progress updates

### 8.2 Reliability

- Automatic retry on AI generation failures (up to 2 retries)
- Database transaction rollback on errors
- Graceful error handling with detailed error messages

### 8.3 Scalability

- Stateless API design
- Configurable rate limiting
- Thread pool for concurrent processing

---

## 9. Brain - Knowledge Base System

### 9.1 Overview

The Brain is a persistent knowledge base that stores all processed sources (videos, documents). Instead of re-entering sources for each content generation, users can leverage their accumulated knowledge base to create content.

### 9.2 Core Capabilities

#### 9.2.1 Knowledge Storage
- All processed videos and documents are automatically indexed in the Brain
- Sources include: transcripts, key topics, embeddings for semantic search
- Tagged and categorized for easy retrieval

#### 9.2.2 Vision-Based Generation (User-Guided Mode)
User provides their idea/thought/vision, and the system:
1. Searches the Brain for relevant sources using semantic matching
2. Matches sources that align with user's vision
3. Combines user's creative direction with matched source knowledge
4. Generates content that represents user's vision backed by source data

**Use Case:** "I want to create a post about productivity hacks for entrepreneurs"
→ System finds relevant sources about productivity, entrepreneurship
→ Generates content using user's angle + source knowledge

#### 9.2.3 Full AI Mode (Autonomous Generation)
User selects sources and quantity, system autonomously generates:

| Mode | Description |
|------|-------------|
| **Single** | Generate 1 content piece from selected source(s) |
| **User-Set Multiple** | User specifies exact count (e.g., 5 posts) |
| **Auto Multiple** | AI determines optimal count based on source richness |

#### 9.2.4 Hybrid Source Selection Mode
Combines user-selected sources with AI-discovered sources:

1. User selects some sources manually from Brain
2. Optionally provides a hint/topic for AI to find additional sources
3. AI augments user selection with relevant sources from Brain
4. Content is generated using the combined source pool

**Use Case:** User selects 2 videos about "marketing" + asks AI to find related sources
→ AI adds 3 more relevant sources about "social media", "branding"
→ Generates content using all 5 sources

| Hybrid Option | Description |
|---------------|-------------|
| **User + AI Augment** | User picks some, AI adds more based on topic/hint |
| **User + AI Fill** | User picks some, AI fills to reach target count |
| **User Primary + AI Support** | User sources are primary, AI sources for context |

### 9.3 Generation Modes Summary

| Mode | Input Required | Output |
|------|----------------|--------|
| **Classic** | Source URL/file | Content from that source |
| **Vision-Based** | User's idea/thought | Content matching vision from Brain |
| **Full AI Single** | Source selection | 1 optimized content piece |
| **Full AI Multiple** | Source selection + count | N content pieces |
| **Full AI Auto** | Source selection | AI-determined count |
| **Hybrid** | User sources + AI hint | Content from combined sources |

---

## 10. Future Considerations

- Additional AI providers (OpenAI, Anthropic)
- More content types (LinkedIn posts, TikTok scripts)
- Scheduled/automated processing
- Team collaboration features
- Analytics and performance tracking
- Direct social media publishing integrations
- Brain analytics (most used sources, topic clusters)
- Cross-source content synthesis
