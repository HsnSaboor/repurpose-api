# Google Gemini API Reference

**Official Docs:** https://ai.google.dev/gemini-api/docs  
**OpenAI Compatibility:** https://ai.google.dev/gemini-api/docs/openai  
**Version:** gemini-2.5-flash

---

## Installation

```bash
pip install openai>=1.0.0
```

Uses OpenAI SDK with Gemini's OpenAI-compatible endpoint.

---

## Quick Start

### Get API Key

1. Go to https://aistudio.google.com/apikey
2. Create new API key
3. Add to `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Basic Usage

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_gemini_api_key",
    base_url="https://generativelanguage.googleapis.com/v1beta"
)

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### JSON Mode

```python
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "Return JSON only."},
        {"role": "user", "content": "List 3 colors as JSON array."}
    ],
    response_format={"type": "json_object"},
    temperature=0.7
)

import json
data = json.loads(response.choices[0].message.content)
```

---

## Rate Limits (Free Tier)

| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| gemini-2.5-flash | 10 | 250,000 | 250 |
| gemini-2.5-pro | 5 | 250,000 | 100 |
| gemini-2.5-flash-lite | 15 | 250,000 | 1,000 |

**RPM** = Requests per Minute  
**TPM** = Tokens per Minute  
**RPD** = Requests per Day (resets midnight Pacific)

---

## Rate Limiter Implementation

```python
import threading
import time
from collections import deque

class GeminiRateLimiter:
    def __init__(self, rpm_limit=10, qpd_limit=250):
        self.rpm_limit = rpm_limit
        self.qpd_limit = qpd_limit
        self.request_times = deque()
        self.lock = threading.Lock()
        self.daily_count = 0
        self.last_reset_day = time.localtime().tm_yday
    
    def wait_for_capacity(self):
        while True:
            with self.lock:
                now = time.time()
                current_day = time.localtime().tm_yday
                
                # Reset daily count if new day
                if current_day != self.last_reset_day:
                    self.daily_count = 0
                    self.last_reset_day = current_day
                
                # Remove requests older than 1 minute
                one_minute_ago = now - 60
                while self.request_times and self.request_times[0] < one_minute_ago:
                    self.request_times.popleft()
                
                # Check capacity
                if (self.daily_count < self.qpd_limit and 
                    len(self.request_times) < self.rpm_limit):
                    self.request_times.append(now)
                    self.daily_count += 1
                    return
            
            time.sleep(0.1)  # Wait before retrying
```

---

## Available Models

| Model | Best For | Context |
|-------|----------|---------|
| `gemini-2.5-flash` | General tasks, fast | 1M tokens |
| `gemini-2.5-pro` | Complex reasoning | 1M tokens |
| `gemini-2.5-flash-lite` | High volume, simple | 1M tokens |

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `429 Too Many Requests` | Rate limit exceeded | Implement exponential backoff |
| `401 Unauthorized` | Invalid API key | Check key in Google AI Studio |
| `400 Bad Request` | Invalid request format | Validate JSON structure |
| `RESOURCE_EXHAUSTED` | Quota exceeded | Wait for reset or upgrade tier |

### Exponential Backoff

```python
import time

def call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = 2 ** attempt  # 1, 2, 4 seconds
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

---

## Environment Variables

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

---

## Paid Tier Limits

| Tier | RPM | TPM | RPD |
|------|-----|-----|-----|
| Free | 10 | 250K | 250 |
| Tier 1 | 500 | 2M | 10K |
| Tier 2 ($250+) | 1000 | 4M | 50K |

---

## Related Specs

- [Stack Decisions](../specs/stack.md)
- [API Specification](../specs/api.md)
