# Content Configuration Guide

## Overview

This guide explains how to configure content generation settings and field limits per content type in the Repurpose API. You can customize field lengths, number of ideas generated, and slides per carousel to match your specific needs.

## Table of Contents

1. [Default Configuration](#default-configuration)
2. [Field Limits Explained](#field-limits-explained)
3. [How to Override Configuration](#how-to-override-configuration)
4. [Configuration Endpoints](#configuration-endpoints)
5. [Examples](#examples)
6. [Best Practices](#best-practices)

---

## Default Configuration

### View Default Settings

To view the default configuration:

```bash
GET /content-config/default
```

**Default Values:**

```json
{
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
  "content_pieces_per_idea": 1
}
```

---

## Field Limits Explained

### Reel Fields

| Field | Default | Description |
|-------|---------|-------------|
| `reel_title_max` | 100 | Maximum length for reel titles |
| `reel_caption_max` | 300 | Maximum length for Instagram/TikTok captions |
| `reel_hook_max` | 200 | Maximum length for the opening hook (first 3-5 seconds) |
| `reel_script_max` | 2000 | Maximum length for the complete video script |

### Carousel Fields

| Field | Default | Description |
|-------|---------|-------------|
| `carousel_title_max` | 100 | Maximum length for carousel main title |
| `carousel_caption_max` | 300 | Maximum length for post caption |
| `carousel_slide_heading_max` | 100 | Maximum length for each slide's heading/label |
| `carousel_slide_text_max` | 800 | **Maximum length for slide text content** (PRIMARY CONTENT FIELD) |
| `carousel_min_slides` | 4 | Minimum number of slides to generate |
| `carousel_max_slides` | 8 | Maximum number of slides to generate |

**Important Note on Carousel Slides:**

The `carousel_slide_text_max` field has been **increased from 300 to 800 characters** by default. This is the **primary content field** where the value lies. The AI is instructed to generate:

- **400-800 characters** of detailed, comprehensive content per slide
- **3-5 sentences** with specific details, examples, and actionable information
- Content that reads like a **mini-article or detailed explanation**, not just a caption
- Information that is self-contained and doesn't rely solely on the heading

The `step_heading` is just a short label (max 100 chars), while the `text` field contains the substantive information.

### Tweet Fields

| Field | Default | Description |
|-------|---------|-------------|
| `tweet_title_max` | 100 | Maximum length for internal tweet title |
| `tweet_text_max` | 280 | Maximum length for main tweet (Twitter/X limit) |
| `tweet_thread_item_max` | 280 | Maximum length for each thread continuation tweet |

### Content Generation Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `min_ideas` | 6 | Minimum number of content ideas to generate |
| `max_ideas` | 8 | Maximum number of content ideas to generate |
| `content_pieces_per_idea` | 1 | Number of content pieces per idea |

---

## How to Override Configuration

You can override the default configuration when processing videos or documents by including a `content_config` object in your `custom_style`.

### Option 1: Using Custom Style with Content Config

```json
{
  "video_id": "dQw4w9WgXcQ",
  "custom_style": {
    "target_audience": "developers and tech enthusiasts",
    "call_to_action": "Follow for more coding tips",
    "content_goal": "education",
    "language": "English",
    "tone": "Technical but friendly",
    "content_config": {
      "min_ideas": 5,
      "max_ideas": 10,
      "field_limits": {
        "carousel_slide_text_max": 1000,
        "carousel_min_slides": 5,
        "carousel_max_slides": 10,
        "reel_script_max": 2500
      }
    }
  }
}
```

### Option 2: Using Style Preset

Style presets can include their own `content_config`:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "style_preset": "educational_content"
}
```

The preset's configuration will be applied automatically. Check preset details:

```bash
GET /content-styles/presets/educational_content
```

---

## Configuration Endpoints

### 1. Get Default Configuration

```bash
GET /content-config/default
```

Returns the baseline configuration used when no overrides are provided.

### 2. Get Current Active Configuration

```bash
GET /content-config/current
```

Returns the currently active configuration (useful for debugging).

### 3. Get Preset Configuration

```bash
GET /content-styles/presets/{preset_name}
```

Returns the complete preset including its `content_config`.

---

## Examples

### Example 1: Longer Carousel Slides

Generate carousels with more detailed content (1000 chars per slide):

```json
{
  "video_id": "ABC123",
  "custom_style": {
    "target_audience": "business professionals",
    "language": "English",
    "content_config": {
      "field_limits": {
        "carousel_slide_text_max": 1000
      }
    }
  }
}
```

### Example 2: More Slides Per Carousel

Generate carousels with 6-12 slides instead of 4-8:

```json
{
  "video_id": "ABC123",
  "custom_style": {
    "target_audience": "students",
    "language": "English",
    "content_config": {
      "field_limits": {
        "carousel_min_slides": 6,
        "carousel_max_slides": 12
      }
    }
  }
}
```

### Example 3: Generate More Content Ideas

Generate 10-15 content ideas instead of 6-8:

```json
{
  "video_id": "ABC123",
  "custom_style": {
    "target_audience": "content creators",
    "language": "English",
    "content_config": {
      "min_ideas": 10,
      "max_ideas": 15
    }
  }
}
```

### Example 4: Shorter Captions for Twitter-Style Content

Generate shorter captions suitable for Twitter-like platforms:

```json
{
  "video_id": "ABC123",
  "custom_style": {
    "target_audience": "Twitter users",
    "language": "English",
    "content_config": {
      "field_limits": {
        "reel_caption_max": 140,
        "carousel_caption_max": 140
      }
    }
  }
}
```

### Example 5: Long-Form Reel Scripts

Generate longer, more detailed reel scripts:

```json
{
  "video_id": "ABC123",
  "custom_style": {
    "target_audience": "educators",
    "language": "English",
    "content_config": {
      "field_limits": {
        "reel_script_max": 3000,
        "reel_hook_max": 300
      }
    }
  }
}
```

### Example 6: Document Processing with Custom Config

```bash
POST /process-document/
Content-Type: multipart/form-data

file: [your-file.pdf]
custom_style: {
  "target_audience": "researchers",
  "language": "English",
  "content_config": {
    "min_ideas": 8,
    "max_ideas": 12,
    "field_limits": {
      "carousel_slide_text_max": 1200,
      "carousel_max_slides": 15
    }
  }
}
```

---

## Best Practices

### 1. Carousel Slide Text Length

**Default (800 chars)** is optimal for most use cases:
- Provides 3-5 sentences of detailed information
- Fits well on Instagram/LinkedIn carousels
- Balances detail with readability

**Increase to 1000-1200 chars when:**
- Content is highly educational or technical
- Target audience expects in-depth information
- You're creating long-form carousel content

**Decrease to 400-600 chars when:**
- Content needs to be more scannable
- Visual elements are more important than text
- Target platform favors brevity

### 2. Number of Slides

**Default (4-8 slides)** works for most content:
- Maintains engagement without being overwhelming
- Standard for Instagram/LinkedIn carousels
- Good balance of information delivery

**Increase slides (10-15) when:**
- Content is step-by-step tutorials
- You have comprehensive information to share
- Creating educational series

**Decrease slides (3-5) when:**
- Content is simple or focused
- Target audience prefers quick consumption
- Creating teaser or highlight content

### 3. Number of Ideas

**Default (6-8 ideas)** provides good variety:
- Multiple content types (reels, carousels, tweets)
- Enough options to choose from
- Balanced processing time

**Increase ideas (10-15) when:**
- Source content is rich and varied
- You need more content options
- Building a content calendar

**Decrease ideas (3-5) when:**
- Source content is focused/short
- You only need a few pieces
- Faster processing is needed

### 4. Combining Configurations

You can mix and match settings for optimal results:

```json
{
  "content_config": {
    "min_ideas": 8,
    "max_ideas": 12,
    "field_limits": {
      "carousel_slide_text_max": 900,
      "carousel_min_slides": 5,
      "carousel_max_slides": 10,
      "reel_script_max": 2500
    }
  }
}
```

### 5. Testing Configuration

1. Start with defaults
2. Process a sample video
3. Review generated content
4. Adjust specific limits based on results
5. Iterate until satisfied

---

## Validation and Limits

The API automatically validates content against configured limits:

- Content exceeding limits will be regenerated automatically (up to 2 retries)
- Validation errors are logged for debugging
- Successfully validated content is returned

**Hard Limits (Cannot Override):**
- `tweet_text_max`: Cannot exceed 280 (Twitter/X platform limit)
- `carousel_slide_heading_max`: Should stay under 100 for readability
- Minimum values must be positive integers

---

## Summary

- **Default carousel slide text is now 800 chars** (increased from 300)
- **Carousel slides are generated with 400-800 chars of detailed content by default**
- All field limits and generation settings are **fully configurable**
- Override settings using `content_config` in `custom_style`
- View defaults at `/content-config/default`
- Each request can have custom configuration
- Configuration is validated and enforced by the API

---

**For more information, see:**
- [API Guide](./api_guide.md) - Complete API reference
- [Quick Start](./QUICK_START.md) - Get started quickly
- Interactive docs at `http://localhost:8002/docs`
