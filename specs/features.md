# Features Specification

**Version:** 1.0  
**Last Updated:** January 2026

---

## Feature: URL-to-Markdown Source Support

### Overview

Enable users to add web URLs as Brain sources. The system will fetch the URL content, extract the main text (stripping HTML, scripts, styles, ads, navigation), convert to clean Markdown, and index it in the Brain knowledge base.

### User Stories

1. **As a user**, I want to add a blog post URL to my Brain so I can reference it when creating content.
2. **As a user**, I want the system to automatically extract only the main article content, not headers/footers/ads.
3. **As a user**, I want the extracted content in clean Markdown format for readability.

### Technical Requirements

#### Library Selection: Trafilatura

**Decision:** Use `trafilatura` for URL-to-Markdown conversion.

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| **trafilatura** | Best main content extraction, removes boilerplate, native Markdown output, actively maintained, 5k+ GitHub stars | Heavier dependency | **Selected** |
| html2text | Simple, lightweight | No content filtering, includes nav/ads/footers | Not suitable |
| markdownify | Simple API | No URL fetching, no content filtering | Not suitable |
| html-to-markdown | Fast (Rust-based) | No content extraction logic | Not suitable |

**Trafilatura Advantages:**
- Automatically identifies and extracts main content
- Removes boilerplate (headers, footers, sidebars, ads, navigation)
- Native Markdown output format (`output_format="markdown"`)
- Metadata extraction (title, author, date, description)
- Handles JavaScript-rendered content fallbacks
- Battle-tested: Used by HuggingFace, IBM, and others

#### API Changes

**New source_type:** `url`

```python
# POST /brain/sources
{
  "title": "Article Title",  # Optional - auto-extracted if not provided
  "source_type": "url",
  "url": "https://example.com/article",
  "extract_options": {
    "include_tables": true,
    "include_images": false,
    "include_links": true
  }
}
```

**Response includes:**
```python
{
  "source_id": "src_xxx",
  "title": "Auto-extracted Title",
  "content": "# Markdown Content\n\nExtracted article text...",
  "source_type": "url",
  "source_metadata": {
    "original_url": "https://...",
    "author": "Author Name",
    "date": "2025-01-12",
    "description": "Meta description",
    "sitename": "Example.com"
  }
}
```

#### CLI Changes

```bash
# Add URL to Brain
python repurpose.py --add-url "https://example.com/article"

# Process URL directly (like video/document)
python repurpose.py "https://example.com/article"
```

#### Service Layer

New file: `core/services/url_service.py`

```python
from trafilatura import fetch_url, extract, extract_metadata

class URLExtractor:
    @staticmethod
    def extract_from_url(url: str, include_tables: bool = True) -> dict:
        """
        Fetch URL and extract main content as Markdown.
        Returns: {content, title, metadata}
        """
        downloaded = fetch_url(url)
        if not downloaded:
            raise ValueError(f"Failed to fetch URL: {url}")
        
        content = extract(
            downloaded,
            output_format="markdown",
            include_tables=include_tables,
            include_links=True,
            include_images=False,
        )
        
        metadata = extract_metadata(downloaded)
        
        return {
            "content": content,
            "title": metadata.title if metadata else None,
            "author": metadata.author if metadata else None,
            "date": metadata.date if metadata else None,
            "description": metadata.description if metadata else None,
            "sitename": metadata.sitename if metadata else None,
            "original_url": url,
        }
```

### Acceptance Criteria

1. [ ] `trafilatura` added to requirements.txt
2. [ ] `URLExtractor` service created and tested
3. [ ] API endpoint accepts `source_type: "url"` with URL field
4. [ ] CLI supports `--add-url` flag
5. [ ] CLI auto-detects URLs (not YouTube) and processes as URL source
6. [ ] Extracted content is clean Markdown without HTML artifacts
7. [ ] Metadata (title, author, date) extracted and stored
8. [ ] Error handling for failed fetches, blocked sites, etc.

### Dependencies

- `trafilatura>=2.0.0` (pip install trafilatura)

### Related Files

- `specs/api.md` - Brain source endpoints
- `specs/data.md` - BrainSource schema
- `core/services/url_service.py` - New service
- `api/routers/brain.py` - Endpoint updates
- `repurpose.py` - CLI updates

---

## Future Features (Backlog)

- [ ] Batch URL import from bookmarks file
- [ ] Scheduled URL re-fetch for updated content
- [ ] URL content diff tracking
- [ ] Browser extension for one-click Brain import
- [ ] Vector embeddings using sentence-transformers
- [ ] Brain analytics dashboard
- [ ] Cross-source content synthesis
- [ ] Source clustering and topic graphs
