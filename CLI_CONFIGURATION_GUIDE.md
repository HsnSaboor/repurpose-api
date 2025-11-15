# CLI Configuration Guide

## Overview

The `repurpose.py` CLI now supports full configuration of content generation settings. You can customize carousel slide lengths, number of slides, and content idea generation directly from the command line.

## Quick Start

### View Current Configuration

```bash
python repurpose.py --show-config
```

Output:
```
Current Configuration:

Carousel Settings:
  Slide Text Max:  800 chars
  Min Slides:      4
  Max Slides:      8

Reel Settings:
  Script Max:      2000 chars
  Caption Max:     300 chars

Generation Settings:
  Min Ideas:       6
  Max Ideas:       8
```

### Use Enhanced Defaults (No Config Needed)

```bash
python repurpose.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

✨ Automatically uses enhanced defaults with 800-char carousel slides!

---

## CLI Configuration Options

### Available Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--carousel-text-max N` | Max chars per carousel slide text | 800 |
| `--carousel-slides-min N` | Min slides per carousel | 4 |
| `--carousel-slides-max N` | Max slides per carousel | 8 |
| `--min-ideas N` | Min content ideas to generate | 6 |
| `--max-ideas N` | Max content ideas to generate | 8 |
| `--show-config` | Show current configuration and exit | - |
| `-l, --limit N` | Process only first N sources | All |

---

## Usage Examples

### Basic Usage (Enhanced Defaults)

```bash
# Single video
python repurpose.py "dQw4w9WgXcQ"

# Multiple videos
python repurpose.py "video1,video2,video3"

# From file
python repurpose.py videos.txt

# Document
python repurpose.py article.pdf
```

### Custom Configuration Examples

#### 1. Longer Carousel Slides (1000 chars)

```bash
python repurpose.py videos.txt --carousel-text-max 1000
```

**Result:** Carousel slides with up to 1000 characters of detailed content

#### 2. More Slides Per Carousel

```bash
python repurpose.py video.txt --carousel-slides-max 12
```

**Result:** Carousels with up to 12 slides instead of 8

#### 3. Generate More Content Ideas

```bash
python repurpose.py video.txt --min-ideas 10 --max-ideas 15
```

**Result:** 10-15 content ideas instead of 6-8

#### 4. Combined Configuration

```bash
python repurpose.py videos.txt \
  --carousel-text-max 1200 \
  --carousel-slides-max 15 \
  --min-ideas 12 \
  --max-ideas 20
```

**Result:** Highly detailed carousels with lots of content

#### 5. Quick Social Media Posts (Shorter)

```bash
python repurpose.py video.txt \
  --carousel-text-max 600 \
  --carousel-slides-max 6
```

**Result:** More concise, scannable content

---

## Workflow Examples

### Educational Content Creator

```bash
# Long-form, detailed content
python repurpose.py course-videos.txt \
  --carousel-text-max 1000 \
  --carousel-slides-max 12 \
  --min-ideas 8 \
  --max-ideas 15
```

### Social Media Manager

```bash
# Quick, engaging posts
python repurpose.py marketing-videos.csv \
  --carousel-text-max 700 \
  --carousel-slides-max 8 \
  --limit 10
```

### Technical Writer

```bash
# In-depth technical content
python repurpose.py tech-docs.pdf \
  --carousel-text-max 1200 \
  --carousel-slides-min 6 \
  --carousel-slides-max 15
```

### Content Batch Processing

```bash
# Process first 5 videos with custom config
python repurpose.py large-playlist.txt \
  --limit 5 \
  --carousel-text-max 900 \
  --max-ideas 12
```

---

## Configuration Display

When using custom configuration, the CLI shows your settings:

```bash
python repurpose.py video.txt --carousel-text-max 1000 --max-ideas 12
```

Output includes:
```
⚙️  Custom Configuration:
   • carousel_slide_text_max: 1000
   • max_ideas: 12

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         Starting Processing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Input Source Formats

### Video URLs

```bash
# Full URL
python repurpose.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Video ID
python repurpose.py "dQw4w9WgXcQ"

# Multiple (comma-separated)
python repurpose.py "video1,video2,video3"
```

### Video List Files

**videos.txt:**
```
dQw4w9WgXcQ
jNQXAC9IVRw
# This is a comment
L_jWHffIx5E
```

**videos.csv:**
```csv
video_id,title
dQw4w9WgXcQ,Never Gonna Give You Up
jNQXAC9IVRw,Another Video
```

Usage:
```bash
python repurpose.py videos.txt --carousel-text-max 800
python repurpose.py videos.csv --limit 10
```

### Document Files

```bash
# Text document
python repurpose.py article.txt --carousel-text-max 900

# Markdown
python repurpose.py notes.md --carousel-slides-max 10

# Word document
python repurpose.py report.docx --min-ideas 10

# PDF
python repurpose.py whitepaper.pdf --carousel-text-max 1200
```

---

## Default Values Explained

### Why 800 Characters for Carousel Slides?

The default was increased from 300 to 800 characters because:

- **More Valuable Content**: 3-5 detailed sentences instead of 1-2
- **Mini-Article Approach**: Comprehensive information, not just captions
- **Platform Optimization**: Works well for Instagram, LinkedIn carousels
- **Better Engagement**: More detail = more value for audience

### Recommended Ranges

| Use Case | Carousel Text Max | Slides | Ideas |
|----------|------------------|---------|-------|
| Quick tips | 500-700 | 4-6 | 5-8 |
| General content | 700-900 | 6-8 | 6-10 |
| Educational | 900-1200 | 8-12 | 8-15 |
| Technical | 1000-1500 | 10-15 | 10-20 |

---

## Tips & Best Practices

### 1. Start with Defaults

The enhanced defaults (800 chars) work well for most use cases:

```bash
python repurpose.py video.txt
```

### 2. Test and Iterate

Try different values to find what works for your audience:

```bash
# Test 1: Default
python repurpose.py test-video.txt

# Test 2: Longer
python repurpose.py test-video.txt --carousel-text-max 1000

# Test 3: More slides
python repurpose.py test-video.txt --carousel-slides-max 12
```

### 3. Platform-Specific Settings

**Instagram:**
```bash
python repurpose.py video.txt --carousel-text-max 700 --carousel-slides-max 10
```

**LinkedIn:**
```bash
python repurpose.py video.txt --carousel-text-max 1000 --carousel-slides-max 12
```

**Twitter/X:**
```bash
python repurpose.py video.txt --carousel-text-max 600 --carousel-slides-max 6
```

### 4. Batch Processing

Process large lists with limits:

```bash
# Process in batches of 10
python repurpose.py large-list.txt --limit 10 --carousel-text-max 800
```

### 5. Document Processing

Documents often have richer content - use higher limits:

```bash
python repurpose.py research-paper.pdf \
  --carousel-text-max 1200 \
  --carousel-slides-max 15 \
  --min-ideas 12
```

---

## Comparison: CLI vs API

Both interfaces support the same configuration:

**CLI:**
```bash
python repurpose.py video.txt \
  --carousel-text-max 1000 \
  --carousel-slides-max 12
```

**API:**
```json
{
  "video_id": "ABC123",
  "custom_style": {
    "content_config": {
      "field_limits": {
        "carousel_slide_text_max": 1000,
        "carousel_max_slides": 12
      }
    }
  }
}
```

Both produce identical results with the same configuration!

---

## Output Files

Generated content is saved to:

```
output/
├── generated_content.csv       # Reels and tweets
├── carousels/
│   └── {video_id}_carousel_titles.csv
└── slides/
    └── {video_id}_XXX_slides.csv
```

The output format is the same regardless of configuration used.

---

## Troubleshooting

### Configuration Not Applied?

Make sure flags come AFTER the input source:

```bash
# ✅ Correct
python repurpose.py video.txt --carousel-text-max 1000

# ❌ Wrong
python repurpose.py --carousel-text-max 1000 video.txt
```

### Check Active Configuration

```bash
python repurpose.py --show-config
```

### View Help

```bash
python repurpose.py --help
```

---

## Advanced Usage

### Shell Scripts

Create reusable scripts:

**process-educational.sh:**
```bash
#!/bin/bash
python repurpose.py "$1" \
  --carousel-text-max 1000 \
  --carousel-slides-max 12 \
  --min-ideas 10 \
  --max-ideas 15
```

Usage:
```bash
./process-educational.sh course-videos.txt
```

### Aliases

Add to `.bashrc` or `.zshrc`:

```bash
alias repurpose-long='python repurpose.py --carousel-text-max 1200 --carousel-slides-max 15'
alias repurpose-quick='python repurpose.py --carousel-text-max 600 --carousel-slides-max 6'
```

Usage:
```bash
repurpose-long my-video.txt
repurpose-quick quick-tips.txt
```

---

## Summary

✅ CLI fully supports content configuration  
✅ Same features as API  
✅ Enhanced defaults (800 char slides) enabled automatically  
✅ Easy to customize per-run  
✅ Configuration display for transparency  
✅ Compatible with all input types (videos, documents, lists)

---

**For more information:**
- [CONTENT_CONFIGURATION_GUIDE.md](./CONTENT_CONFIGURATION_GUIDE.md) - Complete configuration reference
- [QUICK_REFERENCE_CONFIG.md](./QUICK_REFERENCE_CONFIG.md) - Quick reference
- [README.md](./README.md) - Getting started

**Status:** ✅ Production Ready  
**Last Updated:** 2025-11-15
