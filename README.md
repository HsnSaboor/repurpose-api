# YouTube Repurposer API

🚀 **A FastAPI backend for transforming YouTube videos into engaging social media content using AI**

Transform any YouTube video into Instagram Reels, Tweets, and Image Carousels with natural language editing capabilities. Perfect for content creators, social media managers, and marketing teams.

## ✨ Features

- **🎥 Video Transcription**: Extract accurate transcripts from YouTube videos
- **🤖 AI Content Generation**: Generate Instagram Reels, Tweets, and Image Carousels using advanced LLM
- **✏️ Natural Language Editing**: Edit generated content using simple prompts
- **🔄 Smart Validation**: Automatically retry and fix validation errors to ensure 100% content recovery
- **📦 Bulk Processing**: Process multiple videos simultaneously
- **🌐 REST API**: Complete RESTful API with comprehensive documentation
- **⚡ Fast & Scalable**: Built with FastAPI for high performance

## 🏗️ Project Structure

This project follows a clean, organized structure:

```
├── main.py                    # FastAPI application entry point
├── repurpose.py              # Core content generation logic
├── channelvideos_alt.py      # YouTube channel video utilities
├── core/                     # Core services and database
│   ├── database.py           # Database models and connection
│   └── services/             # Business logic services
├── tests/                    # All test files
├── utilities/                # Database migration and utility scripts
├── output/                   # Generated content output
└── yt_repurposer.db         # SQLite database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Virtual environment tool (venv, uv, conda)
- YouTube Transcript API access
- Gemini API key for content generation

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd repurpose-api
```

2. **Set up virtual environment:**
```bash
# Using uv (recommended)
uv venv
uv pip install -r requirements.txt

# Or using pip
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

4. **Start the server:**
```bash
# Development mode (recommended)
uvicorn main:app --host 127.0.0.1 --port 8002 --reload

# Or using the run script
python run_server.py
```

🎉 **API is now running at:** `http://127.0.0.1:8002`

## 📚 API Documentation

- **Interactive Docs:** [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)
- **ReDoc:** [http://127.0.0.1:8002/redoc](http://127.0.0.1:8002/redoc)
- **Detailed API Guide:** [docs/API.md](docs/API.md)

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (with defaults)
DATABASE_URL=sqlite:///./yt_repurposer.db
HOST=127.0.0.1
PORT=8002
DEBUG=false
LOG_LEVEL=INFO
MAX_CONTENT_PIECES=10
REQUESTS_PER_MINUTE=60
```

## 📖 API Endpoints Overview

### Core Video Processing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/transcribe/` | POST | Extract transcript from YouTube video |
| `/process-video/` | POST | Generate social media content from video |
| `/process-videos-bulk/` | POST | Process multiple videos at once |

### Content Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/edit-content/` | POST | Edit generated content with natural language |
| `/content-styles/presets/` | GET | Get available content style presets |
| `/content-styles/presets/{preset_name}` | GET | Get details of a specific style preset |

### Utilities

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/channel-videos/` | POST | Get videos from a YouTube channel |
| `/health/` | GET | Health check endpoint |

## 🎨 Content Style Customization

The API supports customizable content styles to match your brand voice and target audience.

### Available Style Presets

- **`ecommerce_entrepreneur`**: For e-commerce and Shopify store owners (Roman Urdu)
- **`professional_business`**: Professional business content
- **`social_media_casual`**: Casual, engaging social media content
- **`educational_content`**: Educational and informative content
- **`fitness_wellness`**: Health, fitness, and wellness focused content

### Using Style Presets

```javascript
// Process video with a style preset
const response = await fetch('/process-video/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    video_id: 'dQw4w9WgXcQ',
    style_preset: 'professional_business'
  })
});
```

### Custom Style Configuration

```javascript
// Process video with custom style
const response = await fetch('/process-video/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    video_id: 'dQw4w9WgXcQ',
    custom_style: {
      target_audience: "tech entrepreneurs and startup founders",
      call_to_action: "Subscribe for startup insights",
      content_goal: "education, thought_leadership",
      language: "English",
      tone: "Inspirational and professional",
      additional_instructions: "Use startup terminology and include metrics"
    }
  })
});
```

## 💻 Frontend Integration Examples

### JavaScript/TypeScript

```typescript
// Transcribe a video
const transcriptResponse = await fetch('http://127.0.0.1:8002/transcribe/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ video_id: 'dQw4w9WgXcQ' })
});
const transcript = await transcriptResponse.json();

// Generate content with style preset
const contentResponse = await fetch('http://127.0.0.1:8002/process-video/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    video_id: 'dQw4w9WgXcQ',
    force_regenerate: false,
    style_preset: 'professional_business'
  })
});
const content = await contentResponse.json();

// Or generate content with custom style
const customContentResponse = await fetch('http://127.0.0.1:8002/process-video/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    video_id: 'dQw4w9WgXcQ',
    custom_style: {
      target_audience: "fitness enthusiasts",
      call_to_action: "Follow for daily tips",
      content_goal: "motivation, education",
      language: "English",
      tone: "Motivational"
    }
  })
});
const customContent = await customContentResponse.json();

// Edit content
const editResponse = await fetch('http://127.0.0.1:8002/edit-content/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    video_id: 'dQw4w9WgXcQ',
    content_piece_id: 'dQw4w9WgXcQ_001',
    edit_prompt: 'Make it more engaging and add emojis',
    content_type: 'reel'
  })
});
const editedContent = await editResponse.json();
```

### Python

```python
import requests

API_BASE = "http://127.0.0.1:8002"

# Process video with style preset
response = requests.post(f"{API_BASE}/process-video/", json={
    "video_id": "dQw4w9WgXcQ",
    "force_regenerate": False,
    "style_preset": "professional_business"
})

# Or process with custom style
custom_response = requests.post(f"{API_BASE}/process-video/", json={
    "video_id": "dQw4w9WgXcQ",
    "custom_style": {
        "target_audience": "business professionals",
        "call_to_action": "Contact us for consultation",
        "content_goal": "lead_generation, brand_awareness",
        "language": "English",
        "tone": "Professional"
    }
})

if response.status_code == 200:
    data = response.json()
    print(f"Generated {len(data['content_pieces'])} content pieces")
    
    # Edit the first piece
    if data['content_pieces']:
        first_piece = data['content_pieces'][0]
        edit_response = requests.post(f"{API_BASE}/edit-content/", json={
            "video_id": "dQw4w9WgXcQ",
            "content_piece_id": first_piece['content_id'],
            "edit_prompt": "Make the tone more professional",
            "content_type": first_piece['content_type']
        })
        
        if edit_response.status_code == 200:
            edited = edit_response.json()
            print(f"Successfully edited content: {edited['changes_made']}")
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python tests/test_legacy_endpoints.py

# Test content style functionality
python test_content_styles.py

# Test API manually
curl -X POST "http://127.0.0.1:8002/transcribe/" \
     -H "Content-Type: application/json" \
     -d '{"video_id": "dQw4w9WgXcQ"}'
```

## 🔧 Development

### Adding New Features

1. Add new routes in `app/api/routes/`
2. Implement business logic in `app/core/services/`
3. Update schemas in `app/core/models/schemas.py`
4. Add tests in `tests/`
5. Update documentation

### Database Migrations

```bash
# The app automatically creates tables on startup
# For production, consider using Alembic for migrations
```

## 🚀 Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment guides including:

- Docker deployment
- Cloud platform setup (AWS, GCP, Azure)
- Environment configuration
- Scaling considerations

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the [API documentation](docs/API.md)
- Review the [troubleshooting guide](docs/TROUBLESHOOTING.md)

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices**
