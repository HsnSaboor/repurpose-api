# Technology Stack Specification

**Version:** 1.0  
**Last Updated:** January 2026

---

## 1. Runtime Environment

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.9+ (tested on 3.13) | Required for type hints and async features |
| OS | Linux/macOS/Windows | Cross-platform compatible |

---

## 2. Core Framework

### 2.1 Web Framework: FastAPI

**Selected:** FastAPI  
**Version:** Latest (via pip)

#### Decision Matrix

| Criteria | FastAPI | Flask | Django REST |
|----------|---------|-------|-------------|
| Async Support | ✅ Native | ⚠️ Limited | ⚠️ Limited |
| Auto API Docs | ✅ Swagger/ReDoc | ❌ Manual | ⚠️ Via DRF |
| Type Validation | ✅ Pydantic | ❌ Manual | ⚠️ Serializers |
| Performance | ✅ High | ⚠️ Medium | ⚠️ Medium |
| Learning Curve | ✅ Low | ✅ Low | ⚠️ Medium |
| SSE/Streaming | ✅ Native | ⚠️ Manual | ⚠️ Manual |

**Rationale:** FastAPI provides native async support critical for concurrent AI API calls, automatic OpenAPI documentation, and Pydantic integration for request/response validation.

---

## 3. Database Layer

### 3.1 Database: SQLite

**Selected:** SQLite  
**ORM:** SQLAlchemy

#### Decision Matrix

| Criteria | SQLite | PostgreSQL | MongoDB |
|----------|--------|------------|---------|
| Setup Complexity | ✅ Zero | ⚠️ Requires Server | ⚠️ Requires Server |
| File-Based | ✅ Yes | ❌ No | ❌ No |
| Concurrent Writes | ⚠️ Limited | ✅ Excellent | ✅ Good |
| Scalability | ⚠️ Single Node | ✅ Horizontal | ✅ Horizontal |
| Dev/Prod Parity | ⚠️ Dev Only | ✅ Production | ✅ Production |

**Rationale:** SQLite is sufficient for single-user/small-team deployments. For production scaling, migration to PostgreSQL is recommended via SQLAlchemy's database-agnostic design.

**Migration Path:** Change `DATABASE_URL` to `postgresql://...` and install `psycopg2-binary`.

---

## 4. AI Provider

### 4.1 LLM: Google Gemini

**Selected:** Google Gemini API  
**Model:** `gemini-2.5-flash`  
**Interface:** OpenAI-compatible SDK

#### Decision Matrix

| Criteria | Gemini | OpenAI GPT-4 | Anthropic Claude |
|----------|--------|--------------|------------------|
| Cost (per 1M tokens) | ✅ $0.075 | ⚠️ $10-30 | ⚠️ $3-15 |
| Free Tier | ✅ 250 req/day | ❌ None | ❌ None |
| JSON Mode | ✅ Native | ✅ Native | ⚠️ Via Prompt |
| Speed | ✅ Fast | ⚠️ Medium | ⚠️ Medium |
| Context Window | ✅ 1M tokens | ⚠️ 128K | ✅ 200K |

**Rationale:** Gemini offers the best cost-to-performance ratio for content generation. The generous free tier (250 requests/day for Flash) enables development without cost concerns.

#### Rate Limits (Free Tier - gemini-2.5-flash)

| Metric | Limit |
|--------|-------|
| Requests per Minute (RPM) | 10 |
| Tokens per Minute (TPM) | 250,000 |
| Requests per Day (RPD) | 250 |

**Implementation:** Custom `GeminiRateLimiter` class with thread-safe queuing.

---

## 5. Transcript Extraction

### 5.1 YouTube Transcript API

**Package:** `youtube-transcript-api`

#### Capabilities
- Extract manual and auto-generated transcripts
- Multi-language support
- Translation to target language
- Transcript metadata (language, type)

#### Fallback Chain
1. Manual English transcript
2. Auto-generated English transcript
3. Manual non-English → Translate to English
4. Auto-generated non-English → Translate to English

---

## 6. Document Processing

### 6.1 Supported Formats

| Format | Package | Notes |
|--------|---------|-------|
| PDF | `pypdf` | Text extraction only |
| DOCX | `python-docx` | Full text + formatting |
| Markdown | `markdown2` | Renders to text |
| TXT | Built-in | UTF-8 with chardet |

---

## 6.2 URL Content Extraction

### Trafilatura

**Package:** `trafilatura>=2.0.0`  
**Purpose:** Extract main content from web URLs as clean Markdown

#### Decision Matrix

| Criteria | Trafilatura | html2text | markdownify |
|----------|-------------|-----------|-------------|
| Main Content Extraction | ✅ Automatic | ❌ None | ❌ None |
| Boilerplate Removal | ✅ Headers/footers/ads | ❌ None | ❌ None |
| Markdown Output | ✅ Native | ✅ Yes | ✅ Yes |
| Metadata Extraction | ✅ Title/author/date | ❌ None | ❌ None |
| URL Fetching | ✅ Built-in | ❌ External | ❌ External |
| Maintenance | ✅ Active (5k+ stars) | ⚠️ Moderate | ⚠️ Moderate |

**Rationale:** Trafilatura is the only library that automatically identifies and extracts main article content while removing navigation, ads, and boilerplate. This is critical for clean Brain source indexing.

#### Usage

```python
from trafilatura import fetch_url, extract, extract_metadata

downloaded = fetch_url("https://example.com/article")
content = extract(downloaded, output_format="markdown")
metadata = extract_metadata(downloaded)
```

**Documentation:** [docs/trafilatura.md](../docs/trafilatura.md)

---

## 7. CLI Framework

### 7.1 Rich Console

**Package:** `rich`

#### Features Used
- Progress bars with spinners
- Console rule dividers
- Colored output
- Tables for configuration display

---

## 8. Validation Layer

### 8.1 Pydantic

**Version:** v2 (via FastAPI dependency)

#### Usage
- Request/Response validation
- Content model schemas
- Configuration validation
- Auto-retry on validation failures

---

## 9. Dependencies Summary

### Core Dependencies
```
fastapi
uvicorn
pydantic
pydantic-settings
python-dotenv
sqlalchemy
```

### AI & Transcript
```
openai>=1.0.0  # Used for Gemini OpenAI-compatible endpoint
youtube-transcript-api
```

### Document Processing
```
pypdf
python-docx
markdown2
chardet
python-multipart
```

### CLI & Utilities
```
rich
pandas
```

### Testing
```
pytest
requests
```

---

## 10. Future Stack Considerations

| Need | Recommended Addition |
|------|---------------------|
| Production Database | PostgreSQL + `psycopg2-binary` |
| Caching | Redis + `redis-py` |
| Task Queue | Celery or `arq` |
| Multiple AI Providers | LiteLLM abstraction layer |
| Monitoring | Prometheus + Grafana |
| Container Deployment | Docker + docker-compose |

---

## 11. Reference Documentation

| Tool | Doc Link |
|------|----------|
| FastAPI | [docs/fastapi.md](../docs/fastapi.md) |
| SQLAlchemy | [docs/sqlalchemy.md](../docs/sqlalchemy.md) |
| Google Gemini | [docs/gemini.md](../docs/gemini.md) |
| YouTube Transcript API | [docs/youtube-transcript.md](../docs/youtube-transcript.md) |
| Pydantic | [docs/pydantic.md](../docs/pydantic.md) |
| Rich Console | [docs/rich.md](../docs/rich.md) |
