# Trafilatura - URL Content Extraction

**Library:** trafilatura  
**Version:** 2.0.0+  
**Purpose:** Extract main content from web URLs as clean Markdown

---

## Overview

Trafilatura is a Python library for web scraping that excels at extracting the **main content** from web pages while automatically removing boilerplate (headers, footers, navigation, ads, sidebars). It outputs clean Markdown format.

**Why Trafilatura over alternatives:**
- Automatically identifies main article content
- Removes clutter (ads, nav, footers) without manual configuration
- Native Markdown output support
- Metadata extraction (author, date, title)
- 5k+ GitHub stars, used by HuggingFace, IBM
- Actively maintained

---

## Installation

```bash
pip install trafilatura
```

---

## Basic Usage

### Extract Content from URL

```python
from trafilatura import fetch_url, extract

# Fetch the HTML
url = "https://example.com/blog/article"
downloaded = fetch_url(url)

# Extract main content as Markdown
content = extract(
    downloaded,
    output_format="markdown",
    include_tables=True,
    include_links=True,
    include_images=False,
)

print(content)
```

### Extract with Metadata

```python
from trafilatura import fetch_url, extract, extract_metadata

url = "https://example.com/blog/article"
downloaded = fetch_url(url)

# Get content
content = extract(downloaded, output_format="markdown")

# Get metadata
metadata = extract_metadata(downloaded)
if metadata:
    print(f"Title: {metadata.title}")
    print(f"Author: {metadata.author}")
    print(f"Date: {metadata.date}")
    print(f"Description: {metadata.description}")
    print(f"Site: {metadata.sitename}")
```

---

## Output Formats

Trafilatura supports multiple output formats:

```python
# Plain text (default)
extract(downloaded)

# Markdown
extract(downloaded, output_format="markdown")

# JSON (includes metadata)
extract(downloaded, output_format="json")

# XML
extract(downloaded, output_format="xml")

# HTML (cleaned)
extract(downloaded, output_format="html")
```

---

## Extraction Options

```python
content = extract(
    downloaded,
    output_format="markdown",
    
    # Content inclusion
    include_tables=True,      # Include tables
    include_links=True,       # Preserve links
    include_images=False,     # Include image references
    include_comments=False,   # Include comment sections
    
    # Precision/Recall tradeoff
    favor_precision=False,    # True = stricter, less content
    favor_recall=False,       # True = more content, may include noise
    
    # Performance
    no_fallback=False,        # True = faster, skip fallback algorithms
    
    # Metadata
    with_metadata=True,       # Include metadata in output
)
```

---

## Error Handling

```python
from trafilatura import fetch_url, extract
from trafilatura.settings import use_config

def safe_extract(url: str) -> dict:
    """Safely extract content with error handling."""
    try:
        downloaded = fetch_url(url)
        
        if downloaded is None:
            return {"error": "Failed to fetch URL", "url": url}
        
        content = extract(downloaded, output_format="markdown")
        
        if content is None or len(content.strip()) < 50:
            return {"error": "No content extracted", "url": url}
        
        return {"content": content, "url": url}
        
    except Exception as e:
        return {"error": str(e), "url": url}
```

---

## Integration with Brain

```python
from trafilatura import fetch_url, extract, extract_metadata
from core.services.brain_service import BrainService

def add_url_to_brain(url: str, brain_service: BrainService) -> dict:
    """Add a URL as a Brain source."""
    
    # Fetch and extract
    downloaded = fetch_url(url)
    if not downloaded:
        raise ValueError(f"Failed to fetch: {url}")
    
    content = extract(downloaded, output_format="markdown", include_tables=True)
    if not content:
        raise ValueError(f"No content extracted from: {url}")
    
    metadata = extract_metadata(downloaded)
    
    # Create Brain source
    source = brain_service.create_source(
        title=metadata.title if metadata else url,
        content=content,
        source_type="url",
        source_metadata={
            "original_url": url,
            "author": metadata.author if metadata else None,
            "date": metadata.date if metadata else None,
            "sitename": metadata.sitename if metadata else None,
        },
    )
    
    return source
```

---

## CLI Usage

Trafilatura also provides a command-line interface:

```bash
# Extract content from URL
trafilatura -u "https://example.com/article"

# Output as Markdown
trafilatura -u "https://example.com/article" --markdown

# Save to file
trafilatura -u "https://example.com/article" --markdown > article.md

# Include tables
trafilatura -u "https://example.com/article" --markdown --tables
```

---

## Performance Tips

1. **Use `no_fallback=True`** for faster extraction when content is predictable
2. **Batch processing:** Use `trafilatura.parallel` for multiple URLs
3. **Caching:** Cache `fetch_url` results to avoid re-downloading

```python
from trafilatura import fetch_url, extract
from trafilatura.parallel import parallel_extraction

# Batch extraction
urls = ["https://example1.com", "https://example2.com"]
results = list(parallel_extraction(urls, output_format="markdown"))
```

---

## Official Documentation

- **Docs:** https://trafilatura.readthedocs.io/
- **GitHub:** https://github.com/adbar/trafilatura
- **PyPI:** https://pypi.org/project/trafilatura/
