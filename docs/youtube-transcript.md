# YouTube Transcript API Reference

**PyPI:** https://pypi.org/project/youtube-transcript-api/  
**GitHub:** https://github.com/jdepoix/youtube-transcript-api  
**Version:** 1.2.3+

---

## Installation

```bash
pip install youtube-transcript-api
```

---

## Quick Start

```python
from youtube_transcript_api import YouTubeTranscriptApi

# Get transcript
transcript = YouTubeTranscriptApi.get_transcript("dQw4w9WgXcQ")

# Returns list of segments:
# [
#   {"text": "Never gonna give you up", "start": 0.0, "duration": 2.5},
#   {"text": "Never gonna let you down", "start": 2.5, "duration": 2.3},
#   ...
# ]
```

---

## Common Patterns

### Get Full Text

```python
def get_transcript_text(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([segment["text"] for segment in transcript])
```

### Specify Language

```python
# Try English first, fall back to Spanish
transcript = YouTubeTranscriptApi.get_transcript(
    "VIDEO_ID",
    languages=["en", "es", "fr"]
)
```

### List Available Transcripts

```python
transcript_list = YouTubeTranscriptApi.list_transcripts("VIDEO_ID")

for transcript in transcript_list:
    print(f"Language: {transcript.language}")
    print(f"Code: {transcript.language_code}")
    print(f"Auto-generated: {transcript.is_generated}")
    print(f"Translatable: {transcript.is_translatable}")
```

### Translate Transcript

```python
transcript_list = YouTubeTranscriptApi.list_transcripts("VIDEO_ID")

# Find any transcript and translate to English
transcript = transcript_list.find_transcript(["de", "fr", "es"])
translated = transcript.translate("en")
text = translated.fetch()
```

### Manual vs Auto-Generated

```python
transcript_list = YouTubeTranscriptApi.list_transcripts("VIDEO_ID")

# Get manual transcript only
try:
    manual = transcript_list.find_manually_created_transcript(["en"])
    transcript = manual.fetch()
except:
    # Fall back to auto-generated
    auto = transcript_list.find_generated_transcript(["en"])
    transcript = auto.fetch()
```

---

## Fallback Chain Implementation

```python
from youtube_transcript_api import YouTubeTranscriptApi

def get_english_transcript(video_id):
    """
    Priority:
    1. Manual English
    2. Auto-generated English
    3. Manual other → Translate
    4. Auto other → Translate
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try manual English
        try:
            manual_en = transcript_list.find_manually_created_transcript(["en"])
            return manual_en.fetch(), "manual_english"
        except:
            pass
        
        # Try auto English
        try:
            auto_en = transcript_list.find_generated_transcript(["en"])
            return auto_en.fetch(), "auto_english"
        except:
            pass
        
        # Try translate manual
        for transcript in transcript_list:
            if not transcript.is_generated and transcript.is_translatable:
                translated = transcript.translate("en")
                return translated.fetch(), "translated_manual"
        
        # Try translate auto
        for transcript in transcript_list:
            if transcript.is_generated and transcript.is_translatable:
                translated = transcript.translate("en")
                return translated.fetch(), "translated_auto"
        
        return None, None
        
    except Exception as e:
        return None, str(e)
```

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `TranscriptsDisabled` | Video has no captions | Check if video allows captions |
| `NoTranscriptFound` | No transcript in requested language | Use `list_transcripts()` to check available |
| `VideoUnavailable` | Video deleted or private | Verify video is public |
| `TooManyRequests` | Rate limited by YouTube | Add delays between requests |
| `CouldNotRetrieve` | Network error | Retry with backoff |

### Error Handling

```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    TooManyRequests
)

try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
except TranscriptsDisabled:
    print("Captions are disabled for this video")
except NoTranscriptFound:
    print("No transcript available in requested language")
except VideoUnavailable:
    print("Video is unavailable")
except TooManyRequests:
    print("Rate limited - wait before retrying")
except Exception as e:
    print(f"Error: {e}")
```

---

## Transcript Object

```python
{
    "text": str,      # The transcript text
    "start": float,   # Start time in seconds
    "duration": float # Duration in seconds
}
```

---

## Extract Video ID from URL

```python
import re

def extract_video_id(url):
    patterns = [
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
```

---

## Related Specs

- [Stack Decisions](../specs/stack.md)
- [Data Models](../specs/data.md)
