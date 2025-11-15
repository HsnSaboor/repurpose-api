# 🎯 Project Files Overview

This document provides a quick overview of the organized project structure and how to use it.

## 📁 Directory Structure

```
app/                              # Main application package
├── main.py                       # FastAPI application entry point
├── api/routes/                   # API endpoints
│   ├── videos.py                 # Video processing (transcribe, process)
│   ├── content.py               # Content editing
│   └── utils.py                 # Health check, channel videos
├── core/
│   ├── config/settings.py       # App configuration with environment variables
│   ├── database/connection.py   # Database setup and dependency
│   ├── models/
│   │   ├── video.py             # SQLAlchemy database models
│   │   └── schemas.py           # Pydantic request/response models
│   └── services/                # Business logic
│       ├── content_service.py   # AI content generation
│       ├── transcript_service.py # YouTube transcript fetching
│       └── video_service.py     # Video metadata and channel info

docs/                            # Comprehensive documentation
├── API.md                       # Complete API reference
├── DEPLOYMENT.md               # Production deployment guide
├── DEVELOPMENT.md              # Development setup guide
└── TROUBLESHOOTING.md          # Common issues and solutions

Legacy files (still functional):
├── main.py                      # Original FastAPI app (still works)
├── repurpose.py                # Original content generation logic
├── core/database.py            # Original database setup
└── run_server.py               # Server runner (updated for new structure)
```

## 🚀 Quick Start Commands

```bash
# Start with new organized structure
python -m app.main

# Or start with legacy structure (still works)
python run_server.py

# Run tests
python -m pytest tests/ -v

# Install dependencies
uv pip install -r requirements.txt
# or
pip install -r requirements.txt
```

## 📚 Documentation Quick Links

- **API Reference**: [docs/API.md](docs/API.md) - Complete API documentation
- **Development Guide**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - Setup and development workflow
- **Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Production deployment
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues and fixes

## 🔧 Configuration

1. **Copy environment template**: `cp .env.example .env`
2. **Add your Gemini API key**: Edit `.env` file
3. **Start the server**: `python -m app.main`

## 📡 API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /` | API information |
| `GET /health/` | Health check |
| `POST /api/v1/transcribe/` | Extract video transcript |
| `POST /api/v1/process-video/` | Generate social media content |
| `POST /api/v1/edit-content/` | Edit generated content |
| `POST /api/v1/process-videos-bulk/` | Process multiple videos |
| `POST /channel-videos/` | Get channel video list |

## 🛠️ For Frontend Developers

- **Interactive API Docs**: http://127.0.0.1:8002/docs
- **API Documentation**: [docs/API.md](docs/API.md)
- **Example Integrations**: See API.md for JavaScript/Python/cURL examples
- **Error Handling**: All endpoints return consistent JSON error responses

## 🔄 Migration Notes

The project maintains backward compatibility:
- ✅ All existing API endpoints work unchanged
- ✅ Database schema is the same
- ✅ Environment variables are compatible
- ✅ Legacy `main.py` and `repurpose.py` still functional

New features:
- 🆕 Organized code structure for better maintainability
- 🆕 Comprehensive documentation
- 🆕 Better error handling and validation
- 🆕 Enhanced configuration management
- 🆕 Production-ready deployment guides

## 📞 Support

- **Issues**: Create GitHub issues for bugs
- **Documentation**: Check docs/ folder for guides
- **API Testing**: Use `/docs` endpoint for interactive testing