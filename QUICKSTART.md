# Quick Start Guide - Content Repurposer

Complete guide to get both backend and frontend running.

## Prerequisites

- Python 3.8+ (for backend)
- Bun (for frontend) - Install: `curl -fsSL https://bun.sh/install | bash`
- API keys configured in `.env` file

## Start the Backend API

```bash
# From project root
cd /home/saboor/code/repurpose-api

# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
uvicorn main:app --reload --port 8002
```

Backend will be available at: **http://localhost:8002**

### Verify Backend
```bash
curl http://localhost:8002
# Should return: {"message": "Welcome to the FastAPI Repurpose API"}
```

## Start the Frontend

Open a new terminal:

```bash
# Navigate to frontend directory
cd /home/saboor/code/repurpose-api/frontend

# Install dependencies (first time only)
bun install

# Start development server
bun run dev
```

Frontend will be available at: **http://localhost:3000**

## Using the Application

### 1. Open Browser
Navigate to: **http://localhost:3000**

### 2. Dashboard
- View statistics and recent content
- Click "Process Video" or "Content Library"

### 3. Process a Video
1. Click "Process Video" from dashboard
2. Enter a YouTube URL (e.g., `https://youtube.com/watch?v=VIDEO_ID`)
3. Click "Fetch Video Info"
4. Select a style preset (default: Professional Business)
5. Click "Generate Content"
6. Wait for processing (1-2 minutes)
7. View results in Content Library

### 4. Browse Content Library
- View all generated content
- Search by title or ID
- Filter by type (Reels, Carousels, Tweets)
- Copy content to clipboard
- Switch between grid and list views

## API Endpoints

The backend provides these endpoints:

- `GET /` - Welcome message
- `GET /videos/` - List all processed videos
- `POST /process-video/` - Process a new video
- `GET /content-styles/presets/` - Get available style presets
- `POST /edit-content/` - Edit generated content

## Environment Configuration

### Backend (.env)
```env
OPENAI_API_KEY=your_key_here
# Other API keys as needed
```

### Frontend (frontend/.env)
```env
VITE_API_URL=http://localhost:8002
```

## Troubleshooting

### Backend Issues

**Database not found:**
```bash
# Initialize database
python -c "from core.database import init_db; init_db()"
```

**Port 8002 already in use:**
```bash
# Find and kill process
lsof -ti:8002 | xargs kill -9
# Or use a different port
uvicorn main:app --reload --port 8003
```

### Frontend Issues

**Module not found:**
```bash
cd frontend
rm -rf node_modules
bun install
```

**Build errors:**
```bash
cd frontend
rm -rf .vite dist
bun run build
```

**API connection issues:**
- Verify backend is running: `curl http://localhost:8002`
- Check CORS configuration in `main.py`
- Ensure frontend .env file has correct API URL

### Common Issues

**CORS Errors:**
The backend is configured to allow `localhost:3000`. If you change the frontend port, update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Video Processing Fails:**
- Check OpenAI API key is set
- Verify video has English captions
- Check backend logs for detailed errors

## Production Deployment

### Backend
```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002
```

### Frontend
```bash
cd frontend

# Build for production
bun run build

# Serve with any static server
bunx serve dist
# Or use nginx, Apache, etc.
```

## Features

### ✅ Working
- Dashboard with statistics
- Video processing from YouTube URLs
- Content generation (Reels, Carousels, Tweets)
- Style preset selection
- Content library with search/filter
- Copy to clipboard
- Responsive design

### 🚫 Not Implemented (By Design)
- Authentication/Login
- User accounts
- Permissions

### 📋 Potential Future Features
- Content editing with AI
- Bulk video processing
- Export to files
- Preview modals
- Dark mode
- Settings page

## Architecture

```
┌─────────────────┐         HTTP          ┌──────────────────┐
│                 │ ◄──────────────────► │                  │
│  React Frontend │    REST API           │  FastAPI Backend │
│  (Port 3000)    │   (Port 8002)         │                  │
│                 │                        │                  │
└─────────────────┘                        └──────────────────┘
        │                                           │
        │                                           │
        ▼                                           ▼
   Browser                                   ┌──────────────┐
   localStorage                              │   SQLite DB  │
                                             │   PostgreSQL │
                                             └──────────────┘
```

## Tech Stack

### Frontend
- React 19 + TypeScript
- Vite (build tool)
- TailwindCSS 4 (styling)
- React Router 7 (navigation)
- Axios (HTTP client)
- Bun (package manager)

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- OpenAI API (content generation)
- youtube-transcript-api (transcript extraction)
- SQLite/PostgreSQL (database)

## Performance

- Frontend: < 300KB gzipped
- Backend: < 100ms response time (non-processing endpoints)
- Video processing: 1-3 minutes (depends on video length and API)
- Hot reload: Instant (both frontend and backend)

## Support

For issues or questions:
1. Check backend logs: `tail -f logs/api.log`
2. Check frontend console: Browser DevTools
3. Review API documentation: `http://localhost:8002/docs`

## License

Same as parent project.

---

**Ready to start? Run both commands in separate terminals and visit http://localhost:3000!** 🚀
