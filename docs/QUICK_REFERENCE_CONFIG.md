# Configuration Quick Reference

## 🎯 Quick Start

### View Default Settings
```bash
curl http://localhost:8002/content-config/default
```

### Use Default Enhanced Settings (No Config Needed)
```json
{
  "video_id": "ABC123"
}
```
✨ **Result:** Carousel slides with 400-800 chars of detailed content (auto-enabled!)

---

## 📋 Default Values (Already Enhanced!)

| Setting | Default | Description |
|---------|---------|-------------|
| `carousel_slide_text_max` | **800** | Max chars per slide (⭐ INCREASED from 300) |
| `carousel_min_slides` | 4 | Minimum slides |
| `carousel_max_slides` | 8 | Maximum slides |
| `min_ideas` | 6 | Min content ideas |
| `max_ideas` | 8 | Max content ideas |

**Note:** The slide **text** field (not heading) is now the primary content with 400-800 chars of detailed information!

---

## 🔧 Common Customizations

### 1. Longer Carousel Slides
```json
{
  "video_id": "ABC123",
  "custom_style": {
    "language": "English",
    "content_config": {
      "field_limits": {
        "carousel_slide_text_max": 1000
      }
    }
  }
}
```

### 2. More Slides Per Carousel
```json
{
  "video_id": "ABC123",
  "custom_style": {
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

### 3. More Content Ideas
```json
{
  "video_id": "ABC123",
  "custom_style": {
    "language": "English",
    "content_config": {
      "min_ideas": 10,
      "max_ideas": 15
    }
  }
}
```

### 4. Full Customization
```json
{
  "video_id": "ABC123",
  "custom_style": {
    "target_audience": "developers",
    "language": "English",
    "tone": "Technical",
    "content_config": {
      "min_ideas": 8,
      "max_ideas": 12,
      "field_limits": {
        "carousel_slide_text_max": 1200,
        "carousel_min_slides": 5,
        "carousel_max_slides": 10,
        "reel_script_max": 2500
      }
    }
  }
}
```

---

## 📏 All Configurable Field Limits

### Reel Fields
| Field | Default | Description |
|-------|---------|-------------|
| `reel_title_max` | 100 | Title length |
| `reel_caption_max` | 300 | Caption length |
| `reel_hook_max` | 200 | Hook length |
| `reel_script_max` | 2000 | Script length |

### Carousel Fields
| Field | Default | Description |
|-------|---------|-------------|
| `carousel_title_max` | 100 | Title length |
| `carousel_caption_max` | 300 | Caption length |
| `carousel_slide_heading_max` | 100 | Slide heading |
| `carousel_slide_text_max` | **800** | **Slide content** ⭐ |
| `carousel_min_slides` | 4 | Min slides |
| `carousel_max_slides` | 8 | Max slides |

### Tweet Fields
| Field | Default | Description |
|-------|---------|-------------|
| `tweet_title_max` | 100 | Title length |
| `tweet_text_max` | 280 | Tweet text |
| `tweet_thread_item_max` | 280 | Thread item |

---

## 🌐 API Endpoints

### Configuration Endpoints
```bash
GET /content-config/default          # View defaults
GET /content-config/current          # View active config
GET /content-styles/presets/{name}   # Get preset with config
```

### Processing Endpoints (Accept content_config)
```bash
POST /process-video/           # Process video with config
POST /process-document/        # Process document with config
POST /process-video-stream/    # Stream processing with config
```

---

## 💡 Pro Tips

### Best Practices

1. **Start with defaults** - Already optimized for most use cases
2. **Increase gradually** - Test with +100-200 char increments
3. **Match platform** - Different platforms prefer different lengths
4. **Consider audience** - Technical audiences accept longer content

### When to Increase Limits

**Carousel slide text (>800 chars):**
- Educational/technical content
- In-depth tutorials
- Professional audiences
- Long-form content preference

**Number of slides (>8):**
- Step-by-step guides
- Comprehensive tutorials
- Process documentation

**Number of ideas (>8):**
- Long videos (>30 min)
- Rich, varied content
- Multiple content types needed

### When to Decrease Limits

**Carousel slide text (<800 chars):**
- Quick tips/hacks
- Visual-heavy content
- Social media optimization
- Mobile-first audiences

**Number of slides (<4):**
- Simple concepts
- Quick wins/tips
- Teaser content

---

## 🔄 Migration from Old System

**No action needed!** Your existing code automatically benefits from:
- Longer, more detailed carousel slides (800 chars vs 300)
- Better content quality
- All existing requests work as-is

**To use new features**, just add `content_config` to your requests.

---

## 📚 Full Documentation

- **[CONTENT_CONFIGURATION_GUIDE.md](./CONTENT_CONFIGURATION_GUIDE.md)** - Complete guide
- **[api_guide.md](./api_guide.md)** - API reference
- **[README.md](./README.md)** - Getting started

---

## ❓ FAQ

**Q: Do I need to change my existing code?**  
A: No! Existing code works better automatically.

**Q: What's the difference between heading and text?**  
A: `step_heading` is a short label (max 100 chars). `text` is the main content (400-800 chars with details).

**Q: Can I use different configs for different videos?**  
A: Yes! Pass `content_config` in each request.

**Q: Will this work with documents too?**  
A: Yes! Same config works with `/process-document/`.

**Q: What if I exceed a limit?**  
A: Content is automatically regenerated (up to 2 retries) to meet limits.

---

## 🎯 Common Use Cases

### Educational Content Creator
```json
{
  "content_config": {
    "field_limits": {
      "carousel_slide_text_max": 1000,
      "carousel_max_slides": 12
    }
  }
}
```

### Social Media Manager (Quick Posts)
```json
{
  "content_config": {
    "field_limits": {
      "carousel_slide_text_max": 600,
      "carousel_max_slides": 6
    }
  }
}
```

### Technical Blog Writer
```json
{
  "content_config": {
    "min_ideas": 10,
    "max_ideas": 15,
    "field_limits": {
      "carousel_slide_text_max": 1200,
      "reel_script_max": 2500
    }
  }
}
```

### Marketing Agency (Variety)
```json
{
  "content_config": {
    "min_ideas": 12,
    "max_ideas": 20,
    "field_limits": {
      "carousel_slide_text_max": 900,
      "carousel_max_slides": 10
    }
  }
}
```

---

**Last Updated:** 2025-11-15  
**Status:** ✅ Production Ready
