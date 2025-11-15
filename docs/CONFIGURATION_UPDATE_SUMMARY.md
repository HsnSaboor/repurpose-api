# Configuration Update Summary

## Changes Made

This document summarizes the changes made to make field lengths and settings configurable per content type, and to increase the default carousel slide content length.

---

## 1. Enhanced Carousel Slide Content

### Default Slide Text Length Increased

**Before:** `carousel_slide_text_max: 300` characters  
**After:** `carousel_slide_text_max: 800` characters

The carousel slide `text` field is now recognized as the **primary content field** and generates much more detailed content by default.

### Improved Content Generation Prompts

Updated the system prompts to emphasize:
- Slide text should be **400-800 characters** (aim for longer, more detailed content)
- Include **3-5 sentences** with actionable information, examples, or explanations
- Provide context, reasoning, or supporting details - not just a single statement
- Think of it as a **mini-article or detailed explanation**, not just a caption

### Example Prompt Changes

**Updated carousel schema in system prompt:**
```
"text": "<string, DETAILED TEXT CONTENT - This is the PRIMARY content field. 
Write 3-5 sentences with specific details, examples, actionable tips, or 
explanations. Make it comprehensive and valuable. Min 400 chars recommended, 
max 800 chars. Do NOT repeat the heading - only provide the detailed explanation.>"
```

---

## 2. Fully Configurable Field Limits

### Default Configuration Structure

All field limits are now stored in `DEFAULT_FIELD_LIMITS` dictionary in `repurpose.py`:

```python
DEFAULT_FIELD_LIMITS = {
    "reel_title_max": 100,
    "reel_caption_max": 300,
    "reel_hook_max": 200,
    "reel_script_max": 2000,
    "carousel_title_max": 100,
    "carousel_caption_max": 300,
    "carousel_slide_heading_max": 100,
    "carousel_slide_text_max": 800,  # Increased from 300
    "carousel_min_slides": 4,
    "carousel_max_slides": 8,
    "tweet_title_max": 100,
    "tweet_text_max": 280,
    "tweet_thread_item_max": 280
}
```

### Configuration Functions

Added utility functions for managing limits:

- `update_field_limits(new_limits: dict)` - Update global field limits
- `get_field_limit(key: str) -> int` - Get a specific field limit
- `CURRENT_FIELD_LIMITS` - Global variable storing active configuration

---

## 3. Enhanced Content Generation Config

### Extended ContentFieldLimits Model (main.py)

```python
class ContentFieldLimits(BaseModel):
    # Reel fields
    reel_title_max: int = Field(100, description="Max length for reel titles")
    reel_caption_max: int = Field(300, description="Max length for reel captions")
    reel_hook_max: int = Field(200, description="Max length for reel hooks")
    reel_script_max: int = Field(2000, description="Max length for reel scripts")
    
    # Carousel fields
    carousel_title_max: int = Field(100, description="Max length for carousel titles")
    carousel_caption_max: int = Field(300, description="Max length for carousel captions")
    carousel_slide_heading_max: int = Field(100, description="Max length for carousel slide headings")
    carousel_slide_text_max: int = Field(800, description="Max length for carousel slide text (detailed content)")
    carousel_min_slides: int = Field(4, description="Minimum number of slides in carousel")
    carousel_max_slides: int = Field(8, description="Maximum number of slides in carousel")
    
    # Tweet fields
    tweet_title_max: int = Field(100, description="Max length for tweet titles")
    tweet_text_max: int = Field(280, description="Max length for tweet text")
    tweet_thread_item_max: int = Field(280, description="Max length for thread continuation items")
```

### ContentGenerationConfig Model

```python
class ContentGenerationConfig(BaseModel):
    min_ideas: int = Field(6, description="Minimum number of content ideas to generate")
    max_ideas: int = Field(8, description="Maximum number of content ideas to generate")
    content_pieces_per_idea: int = Field(1, description="Number of content pieces per idea")
    field_limits: ContentFieldLimits = Field(default_factory=ContentFieldLimits)
```

---

## 4. New API Endpoints

### GET /content-config/default

Returns the default content generation configuration including all field limits.

**Response:**
```json
{
  "description": "Default configuration for content generation",
  "field_limits": {
    "carousel_slide_text_max": 800,
    ...
  },
  "min_ideas": 6,
  "max_ideas": 8,
  "note": "These are the default settings. You can override them in custom_style.content_config when processing videos/documents."
}
```

### GET /content-config/current

Returns the currently active content generation configuration.

**Response:**
```json
{
  "description": "Currently active configuration for content generation",
  "field_limits": {
    "carousel_slide_text_max": 800,
    ...
  },
  "note": "This shows the active configuration. To use custom limits, pass them in the content_config parameter when processing."
}
```

### Enhanced GET /content-styles/presets/{preset_name}

Now includes `content_config` in the response showing the preset's configuration.

---

## 5. Updated System Prompts

### Dynamic Field Limits in Prompts

All system prompts now use dynamic field limits from `CURRENT_FIELD_LIMITS`:

**Carousel Generation:**
```python
f"carousel_slide_text_max: {limits['carousel_slide_text_max']} chars"
```

**Validation Error Fixing:**
```python
f"slide text: Must be {limits['carousel_slide_text_max']} characters or less"
```

**Content Editing:**
```python
f"slide text: Maximum {limits['carousel_slide_text_max']} characters"
```

---

## 6. How to Use Custom Configuration

### Method 1: Via Custom Style Object

```json
{
  "video_id": "ABC123",
  "custom_style": {
    "target_audience": "developers",
    "language": "English",
    "content_config": {
      "min_ideas": 10,
      "max_ideas": 15,
      "field_limits": {
        "carousel_slide_text_max": 1000,
        "carousel_min_slides": 5,
        "carousel_max_slides": 10
      }
    }
  }
}
```

### Method 2: Via Style Preset

Presets automatically include their `content_config`:

```json
{
  "video_id": "ABC123",
  "style_preset": "educational_content"
}
```

### Method 3: Document Upload

```bash
POST /process-document/
Content-Type: multipart/form-data

file: document.pdf
custom_style: {
  "target_audience": "researchers",
  "content_config": {
    "field_limits": {
      "carousel_slide_text_max": 1200
    }
  }
}
```

---

## 7. Updated Documentation

### New Files Created

1. **CONTENT_CONFIGURATION_GUIDE.md** - Comprehensive guide on configuration
   - Default settings
   - Field limits explained
   - Override methods
   - Examples and best practices

### Updated Files

2. **api_guide.md** - Updated with:
   - New configuration endpoints
   - Extended request examples showing `content_config`
   - Detailed carousel field descriptions
   - Notes about slide text length increase

3. **main.py** - Enhanced with:
   - New configuration models
   - New endpoints for config inspection
   - Updated preset responses to include config

4. **repurpose.py** - Enhanced with:
   - Improved system prompts for detailed carousel content
   - Dynamic field limit usage throughout
   - Updated validation error messages
   - Configuration management functions

---

## 8. Validation & Error Handling

All validation functions now use dynamic limits:

- Initial content validation against configured limits
- Automatic retry with corrected limits if validation fails
- Clear error messages showing configured limits
- Up to 2 automatic retries for validation errors

---

## 9. Benefits

### For Users

1. **More Detailed Carousel Content** - Slides now contain 2-3x more information by default
2. **Full Control** - Customize any field limit per content type
3. **Flexible Generation** - Control number of ideas and slides generated
4. **Easy Discovery** - New endpoints to view and understand configuration
5. **Per-Request Config** - Different limits for different use cases

### For Developers

1. **Centralized Configuration** - Single source of truth for limits
2. **Dynamic System Prompts** - Prompts automatically reflect configured limits
3. **Easy Testing** - Can override limits for testing without code changes
4. **Better Validation** - Validation messages show actual configured limits
5. **Extensible** - Easy to add new configurable fields

---

## 10. Testing

### Tested Functionality

✅ Configuration functions work correctly  
✅ Default configuration endpoint returns proper values  
✅ Current configuration endpoint works  
✅ Preset endpoint includes content_config  
✅ Field limits reflect new defaults (carousel_slide_text_max: 800)

### Manual Testing Recommended

- Process a video with default settings
- Process a video with custom `content_config`
- Verify carousel slides contain 400-800 chars of detailed content
- Test validation with edge cases
- Try different combinations of limits

---

## 11. Breaking Changes

**None** - All changes are backward compatible:

- Default behavior improved (longer carousel content)
- Existing requests work without modifications
- New `content_config` parameter is optional
- API responses include new fields but maintain structure

---

## 12. Migration Notes

### For Existing Users

**No action required** - Your existing code will work as-is but will benefit from:
- More detailed carousel slide content (800 chars instead of 300)
- Ability to customize limits if needed

### To Use New Features

Simply add `content_config` to your `custom_style`:

```json
{
  "custom_style": {
    "target_audience": "...",
    "content_config": {
      "field_limits": {
        "carousel_slide_text_max": 1000
      }
    }
  }
}
```

---

## Summary

The configuration system is now fully flexible and allows per-request customization of:
- Field length limits for all content types
- Number of ideas generated
- Number of slides per carousel
- All generation behavior

The default carousel slide content is now much more detailed (800 chars with 3-5 sentences) making it more valuable and informative for end users.

All changes maintain backward compatibility while providing powerful new customization options.
