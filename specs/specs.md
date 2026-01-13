# Specifications Index

**Version:** 2.0  
**Last Updated:** January 2026

This directory contains functional requirements, schemas, and API contracts for the YouTube Content Repurposer.

---

## Documents

| File | Description |
|------|-------------|
| [stack.md](./stack.md) | Technology stack with decision matrices |
| [data.md](./data.md) | Database schemas and content models (v2.0: Brain tables) |
| [api.md](./api.md) | REST API endpoint specifications (v2.0: Brain endpoints) |
| [features.md](./features.md) | Feature specifications (URL-to-Markdown, etc.) |

---

## Quick Reference

### Tech Stack
- **Runtime:** Python 3.9+
- **Framework:** FastAPI
- **Database:** SQLite (SQLAlchemy ORM)
- **AI Provider:** Google Gemini (gemini-2.5-flash)
- **CLI:** Rich console

### Content Types
- Instagram Reels (script, hook, caption)
- Image Carousels (4-8 slides)
- Tweets (280 char limit, optional thread)

### Key Endpoints (Classic)
- `POST /process-video/` - Generate content from video
- `POST /process-document/` - Generate content from document
- `POST /edit-content/` - Natural language editing
- `GET /videos/` - List processed content

### Brain Endpoints (v2.0)
- `GET /brain/sources/` - List all Brain sources
- `POST /brain/sources/` - Add source to Brain
- `POST /brain/generate/vision` - Vision-based generation
- `POST /brain/generate/auto` - Full AI mode generation
- `POST /brain/generate/hybrid` - Hybrid source selection (user + AI)
- `POST /brain/search` - Semantic search

---

## Guidelines

1. All specs must be versioned
2. Breaking changes require a new spec version
3. Specs are the source of truth - code must conform to specs
4. Update specs BEFORE implementing changes
