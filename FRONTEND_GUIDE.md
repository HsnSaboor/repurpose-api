# YouTube Repurposer API Integration Guide

## 1. Introduction

This guide provides comprehensive documentation for integrating with the YouTube Repurposer API. This FastAPI-powered backend service transforms YouTube videos into engaging social media content using AI, including Instagram Reels, Tweets, and Image Carousels with natural language editing capabilities.

**API Technology Stack:**
*   Backend: FastAPI (Python)
*   Database: SQLite with SQLAlchemy
*   AI Integration: Gemini API for content generation
*   External APIs: YouTube Transcript API, yt-dlp

## 2. API Server Setup

Ensure the YouTube Repurposer API server is running before integration:

**Default Configuration:**
*   **Base URL:** `http://127.0.0.1:8002`
*   **Protocol:** HTTP/HTTPS
*   **Data Format:** JSON
*   **Content-Type:** `application/json`

**Starting the Server:**
```bash
uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

**Environment Requirements:**
*   Python 3.9+
*   Required API keys: `GEMINI_API_KEY` (for content generation)
*   Database: SQLite (automatically initialized)

## 3. API Documentation & Testing

**Interactive API Documentation:**
*   **Swagger UI:** `http://127.0.0.1:8002/docs`
*   **ReDoc:** `http://127.0.0.1:8002/redoc`
*   **OpenAPI Schema:** `http://127.0.0.1:8002/openapi.json`

**Health Check:**
*   **Endpoint:** `GET /health/`
*   **Response:** `{"status": "healthy", "message": "YouTube Repurposer API is running", "version": "1.0.0"}`

## 4. Authentication & Security

**Current Authentication:** None (API is open for development)

**Security Considerations for Production:**
*   Implement API key authentication
*   Add rate limiting (currently 60 requests per minute)
*   Use HTTPS in production
*   Validate all inputs client-side before API calls
*   Handle sensitive data (API keys) securely

**CORS Configuration:**
*   API accepts requests from any origin during development
*   Configure appropriate CORS policies for production

## 5. Core API Endpoints

### 5.1. Video Transcription

**Endpoint:** `POST /transcribe/`  
**Purpose:** Extract or retrieve transcript from a YouTube video

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ"
}
```

**Response (Success - 200):**
```json
{
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Never Gonna Give You Up",
  "transcript": "We're no strangers to love...",
  "status": "transcribed"
}
```

**Response (Error - 404):**
```json
{
  "detail": "Transcript not available for video dQw4w9WgXcQ"
}
```

### 5.2. Video Content Processing

**Endpoint:** `POST /process-video/`  
**Purpose:** Generate social media content from YouTube video (includes transcription + AI content generation)

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "force_regenerate": false,
  "style_preset": "professional_business",
  "custom_style": {
    "target_audience": "business professionals",
    "call_to_action": "Contact us for consultation",
    "content_goal": "lead_generation, brand_awareness",
    "language": "English",
    "tone": "Professional",
    "additional_instructions": "Use industry terminology and maintain professional tone"
  }
}
```

**Parameters:**
- `video_id` (required): 11-character YouTube video ID
- `force_regenerate` (optional): Boolean, regenerate content even if exists (default: false)
- `style_preset` (optional): String, predefined style preset name (see Content Style section)
- `custom_style` (optional): Object, custom style configuration (see Content Style section)

**Response (Success - 200):**
```json
{
  "id": 123,
  "youtube_video_id": "dQw4w9WgXcQ",
  "title": "Never Gonna Give You Up",
  "transcript": "We're no strangers to love...",
  "status": "processed",
  "ideas": [
    {
      "type": "reel",
      "hook": "The 80s classic that became a meme",
      "description": "Rick Astley's timeless hit explained"
    }
  ],
  "content_pieces": [
    {
      "content_id": "dQw4w9WgXcQ_001",
      "content_type": "reel",
      "title": "Rick Roll Origins",
      "caption": "The story behind the internet's favorite prank! 🎵",
      "id": "dQw4w9WgXcQ_001"
    },
    {
      "content_id": "dQw4w9WgXcQ_002",
      "content_type": "tweet",
      "text": "Never gonna give you up, never gonna let you down 🎵 The ultimate earworm! #RickRoll",
      "id": "dQw4w9WgXcQ_002"
    }
  ]
}
```

### 5.3. Content Editing

**Endpoint:** `POST /edit-content/`  
**Purpose:** Edit generated content using natural language prompts

**Request Body:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "content_piece_id": "dQw4w9WgXcQ_001",
  "edit_prompt": "Make it more engaging and add emojis",
  "content_type": "reel"
}
```

**Parameters:**
- `video_id` (required): Original video ID
- `content_piece_id` (required): ID of content piece to edit
- `edit_prompt` (required): Natural language editing instruction
- `content_type` (required): Type of content ("reel", "tweet", "image_carousel")

**Response (Success - 200):**
```json
{
  "success": true,
  "content_piece_id": "dQw4w9WgXcQ_001",
  "original_content": {
    "title": "Rick Roll Origins",
    "caption": "The story behind the internet's favorite prank!"
  },
  "edited_content": {
    "title": "🎵 Rick Roll Origins: The ULTIMATE Internet Prank! 🎵",
    "caption": "The AMAZING story behind the internet's favorite prank! 🎵✨ You won't believe how this started! 🤯"
  },
  "changes_made": [
    "title changed",
    "caption changed",
    "added emojis",
    "enhanced engagement"
  ]
}
```

### 5.4. Bulk Video Processing

**Endpoint:** `POST /process-videos-bulk/`  
**Purpose:** Process multiple videos in a single request

**Request Body:**
```json
{
  "video_ids": ["dQw4w9WgXcQ", "abc123defgh", "xyz789mnop"]
}
```

**Response (Success - 200):**
```json
[
  {
    "video_id": "dQw4w9WgXcQ",
    "status": "success",
    "details": "Video processed successfully",
    "data": { /* ProcessVideoResponse object */ }
  },
  {
    "video_id": "abc123defgh",
    "status": "error",
    "details": "Transcript not available",
    "data": null
  }
]
```

### 5.5. Channel Video Listing

**Endpoint:** `POST /channel-videos/`  
**Purpose:** Get list of videos from a YouTube channel

**Request Body:**
```json
{
  "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "max_videos": 10
}
```

**Response (Success - 200):**
```json
[
  {
    "videoId": "dQw4w9WgXcQ",
    "title": "Never Gonna Give You Up",
    "duration": "3:33",
    "viewCount": "1000000000",
    "publishedTime": "15 years ago"
  }
]
```

### 5.6. Content Style Management

#### 5.6.1. Get Available Style Presets

**Endpoint:** `GET /content-styles/presets/`  
**Purpose:** Retrieve all available content style presets

**Response (Success - 200):**
```json
{
  "presets": {
    "ecommerce_entrepreneur": {
      "name": "E-commerce Entrepreneur",
      "description": "For e-commerce entrepreneurs and Shopify store owners",
      "target_audience": "ecom entrepreneurs, Shopify store owners, and DTC brands",
      "language": "Roman Urdu",
      "tone": "Educational and engaging"
    },
    "professional_business": {
      "name": "Professional Business",
      "description": "Professional business content for corporate audiences",
      "target_audience": "business professionals, entrepreneurs, and corporate decision makers",
      "language": "English",
      "tone": "Professional and authoritative"
    },
    "social_media_casual": {
      "name": "Social Media Casual",
      "description": "Casual, engaging content for social media audiences",
      "target_audience": "general social media users, millennials, and Gen Z",
      "language": "English",
      "tone": "Casual and fun"
    },
    "educational_content": {
      "name": "Educational Content",
      "description": "Educational and informative content for learners",
      "target_audience": "students, professionals seeking knowledge, lifelong learners",
      "language": "English",
      "tone": "Informative and encouraging"
    },
    "fitness_wellness": {
      "name": "Fitness & Wellness",
      "description": "Health, fitness, and wellness focused content",
      "target_audience": "fitness enthusiasts, health-conscious individuals, wellness seekers",
      "language": "English",
      "tone": "Motivational and supportive"
    }
  }
}
```

#### 5.6.2. Get Specific Style Preset Details

**Endpoint:** `GET /content-styles/presets/{preset_name}`  
**Purpose:** Get detailed information about a specific style preset

**Path Parameters:**
- `preset_name` (required): Name of the style preset (e.g., "professional_business")

**Response (Success - 200):**
```json
{
  "name": "Professional Business",
  "description": "Professional business content for corporate audiences",
  "target_audience": "business professionals, entrepreneurs, and corporate decision makers",
  "call_to_action": "Contact us for consultation, follow for business insights",
  "content_goal": "thought_leadership, brand_awareness, lead_generation",
  "language": "English",
  "tone": "Professional and authoritative",
  "additional_instructions": "Use industry terminology and maintain a professional tone throughout"
}
```

**Response (Error - 404):**
```json
{
  "detail": "Style preset 'invalid_preset' not found"
}
```

## 6. Content Style Configuration

The YouTube Repurposer API supports comprehensive content style customization to ensure generated content matches your brand voice, target audience, and communication goals. You can either use predefined style presets or create completely custom style configurations.

### 6.1. Understanding Content Styles

Content styles influence how the AI generates social media content by providing specific guidelines for:
- **Target Audience**: Who the content is intended for
- **Call to Action**: What action you want readers to take
- **Content Goal**: The purpose of the content (education, lead generation, etc.)
- **Language**: The language for content generation (including Roman Urdu support)
- **Tone**: The overall voice and personality of the content
- **Additional Instructions**: Specific guidelines and requirements

### 6.2. Using Style Presets

#### 6.2.1. Available Presets

1. **`ecommerce_entrepreneur`**
   - **Target**: E-commerce entrepreneurs, Shopify store owners, DTC brands
   - **Language**: Roman Urdu (Urdu words written in English alphabet)
   - **Tone**: Educational and engaging
   - **Focus**: Store launches, design improvements, scaling with ads

2. **`professional_business`**
   - **Target**: Business professionals, entrepreneurs, corporate decision makers
   - **Language**: English
   - **Tone**: Professional and authoritative
   - **Focus**: Thought leadership, brand awareness, lead generation

3. **`social_media_casual`**
   - **Target**: General social media users, millennials, Gen Z
   - **Language**: English
   - **Tone**: Casual and fun
   - **Focus**: Entertainment, engagement, viral content

4. **`educational_content`**
   - **Target**: Students, professionals seeking knowledge, lifelong learners
   - **Language**: English
   - **Tone**: Informative and encouraging
   - **Focus**: Knowledge sharing, community building

5. **`fitness_wellness`**
   - **Target**: Fitness enthusiasts, health-conscious individuals
   - **Language**: English
   - **Tone**: Motivational and supportive
   - **Focus**: Health tips, motivation, positive outcomes

#### 6.2.2. Using Presets in API Calls

**Simple Preset Usage:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "style_preset": "professional_business"
}
```

**Frontend Implementation Example:**
```typescript
// Get available presets
const getStylePresets = async () => {
  const response = await fetch(`${API_BASE_URL}/content-styles/presets/`);
  const data = await response.json();
  return data.presets;
};

// Process video with preset
const processWithPreset = async (videoId: string, presetName: string) => {
  const response = await fetch(`${API_BASE_URL}/process-video/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      style_preset: presetName
    })
  });
  return response.json();
};
```

### 6.3. Custom Style Configuration

For complete control over content generation, you can define a custom style configuration.

#### 6.3.1. Custom Style Object Structure

```typescript
interface CustomContentStyle {
  target_audience: string;      // Required: Describe your target audience
  call_to_action: string;       // Required: What action should readers take
  content_goal: string;         // Required: Purpose of the content
  language: string;             // Optional: Language for generation (default: "English")
  tone: string;                 // Optional: Voice and personality (default: "Professional")
  additional_instructions?: string; // Optional: Specific guidelines
}
```

#### 6.3.2. Custom Style Examples

**Tech Startup Style:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "custom_style": {
    "target_audience": "tech entrepreneurs and startup founders",
    "call_to_action": "Subscribe for startup insights and join our community",
    "content_goal": "education, thought_leadership, networking",
    "language": "English",
    "tone": "Inspirational and innovative",
    "additional_instructions": "Use startup terminology, focus on scalability and growth metrics, include success stories when relevant"
  }
}
```

**Personal Brand Style:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "custom_style": {
    "target_audience": "young professionals interested in personal development",
    "call_to_action": "Follow for daily motivation and tag a friend who needs this",
    "content_goal": "inspiration, personal_growth, community_building",
    "language": "English",
    "tone": "Authentic and motivational",
    "additional_instructions": "Use first-person perspective, include personal anecdotes, keep language conversational yet impactful"
  }
}
```

**Multi-language Example (Roman Urdu):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "custom_style": {
    "target_audience": "Pakistani entrepreneurs and small business owners",
    "call_to_action": "Humse contact kren aur apna business grow kren",
    "content_goal": "business_education, lead_generation",
    "language": "Roman Urdu",
    "tone": "Friendly and helpful",
    "additional_instructions": "Use Roman Urdu exclusively - write Urdu words in English alphabet only. Include local business examples and culturally relevant references."
  }
}
```

### 6.4. Frontend Implementation Examples

#### 6.4.1. Enhanced Process Video Function

```typescript
// Enhanced API function with style support
interface ProcessVideoOptions {
  videoId: string;
  forceRegenerate?: boolean;
  stylePreset?: string;
  customStyle?: CustomContentStyle;
}

export async function processVideoWithStyle(options: ProcessVideoOptions): Promise<ProcessVideoResponse> {
  const { videoId, forceRegenerate = false, stylePreset, customStyle } = options;
  
  const requestBody: any = {
    video_id: videoId,
    force_regenerate: forceRegenerate
  };
  
  if (stylePreset) {
    requestBody.style_preset = stylePreset;
  }
  
  if (customStyle) {
    requestBody.custom_style = customStyle;
  }
  
  const response = await fetch(`${API_BASE_URL}/process-video/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  
  return handleResponse<ProcessVideoResponse>(response);
}
```

#### 6.4.2. Style Preset Selector Component

```typescript
// StylePresetSelector.tsx
import { useState, useEffect } from 'react';

interface StylePreset {
  name: string;
  description: string;
  target_audience: string;
  language: string;
  tone: string;
}

interface StylePresetSelectorProps {
  onPresetSelect: (presetName: string) => void;
  selectedPreset?: string;
}

export const StylePresetSelector: React.FC<StylePresetSelectorProps> = ({
  onPresetSelect,
  selectedPreset
}) => {
  const [presets, setPresets] = useState<Record<string, StylePreset>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPresets = async () => {
      try {
        const response = await fetch('/content-styles/presets/');
        const data = await response.json();
        setPresets(data.presets);
      } catch (error) {
        console.error('Failed to load style presets:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPresets();
  }, []);

  if (loading) return <div>Loading style presets...</div>;

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium">Content Style Preset</label>
      <select 
        value={selectedPreset || ''}
        onChange={(e) => onPresetSelect(e.target.value)}
        className="w-full p-2 border rounded-md"
      >
        <option value="">Choose a style preset...</option>
        {Object.entries(presets).map(([key, preset]) => (
          <option key={key} value={key}>
            {preset.name} - {preset.description}
          </option>
        ))}
      </select>
      {selectedPreset && presets[selectedPreset] && (
        <div className="p-3 bg-gray-50 rounded-md text-sm">
          <p><strong>Target:</strong> {presets[selectedPreset].target_audience}</p>
          <p><strong>Language:</strong> {presets[selectedPreset].language}</p>
          <p><strong>Tone:</strong> {presets[selectedPreset].tone}</p>
        </div>
      )}
    </div>
  );
};
```

### 6.5. Content Style Benefits Summary

The Content Style system provides powerful customization capabilities:

**Key Benefits:**
- **Brand Consistency**: Ensure all generated content matches your brand voice
- **Audience Targeting**: Tailor content for specific demographics and interests
- **Multi-language Support**: Generate content in different languages including Roman Urdu
- **Flexible Implementation**: Choose from presets or create completely custom styles
- **Easy Integration**: Simple API parameters with comprehensive TypeScript support
- **Scalable Content**: Generate content that resonates with your audience at scale

**Best Practices:**
- Use presets for quick, consistent results
- Create custom styles for unique brand requirements
- Test different styles to optimize engagement
- Combine styles with force_regenerate for A/B testing
- Monitor content performance to refine style configurations

**Use Cases:**
- **E-commerce**: Product marketing in Roman Urdu for Pakistani market
- **Corporate**: Professional thought leadership content
- **Social Media**: Engaging, casual content for younger audiences  
- **Education**: Clear, informative content for learners
- **Fitness**: Motivational content for health-conscious users

## 7. Interacting with the FastAPI Backend from Next.js

Effectively interacting with the FastAPI backend is crucial for the frontend's functionality. This section details how to construct requests, handle responses, and manage data flow, particularly concerning data originating from the backend's SQLite database.

You can use the native `fetch` API (as shown in examples) or a library like `axios` to make requests to your backend.

### 7.1. Environment Variable for API URL

Ensure your API base URL is configured. Create a `.env.local` file in the root of your Next.js project:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
Access this in your code via `process.env.NEXT_PUBLIC_API_URL`.

### 7.2. Core Principles of API Interaction

*   **Backend as the Single Source of Truth**: The FastAPI backend manages all business logic, data validation, and direct database interactions (SQLite). The Next.js frontend should **never** attempt to access the database directly. All data operations are mediated through API calls.
*   **Statelessness (Primarily)**: Aim for stateless API interactions where possible. If session management or authentication is introduced, ensure secure handling of tokens or session identifiers.

### 7.3. Constructing Valid API Requests

#### 7.3.1. Request Payloads (JSON)

All POST requests sending data to the backend should use JSON payloads. Refer to the Pydantic models defined in the FastAPI backend (primarily in [`main.py`](main.py:1)) as the definitive source for request body structures.

*   **`/transcribe/` (POST)**:
    ```json
    {
      "video_id": "YOUR_YOUTUBE_VIDEO_ID" // e.g., "dQw4w9WgXcQ"
    }
    ```
    (Corresponds to a Pydantic model like `VideoIDRequest` in the backend)

*   **`/process-video/` (POST)**:
    ```json
    {
      "video_id": "YOUR_YOUTUBE_VIDEO_ID",
      "force_regenerate": false, // Optional, boolean
      "style_preset": "professional_business", // Optional, string
      "custom_style": { // Optional, object
        "target_audience": "business professionals",
        "call_to_action": "Contact us for consultation",
        "content_goal": "lead_generation, brand_awareness",
        "language": "English",
        "tone": "Professional"
      }
    }
    ```
    (Corresponds to a Pydantic model like `ProcessVideoRequest` in the backend)

*   **`/channel/videos/` (POST)**:
    ```json
    {
      "channel_id": "YOUR_CHANNEL_ID_OR_USERNAME", // e.g., "UCXXXX" or "ChannelName"
      "max_videos": 10 // Integer
    }
    ```
    (Corresponds to a Pydantic model like `ChannelVideosRequestData` in the backend)

#### 7.3.2. HTTP Headers

*   **`Content-Type: application/json`**: Essential for POST/PUT requests sending JSON data. The backend uses this to correctly parse the incoming request body.
*   **`Accept: application/json`**: While often not strictly required if the server only sends JSON, it's good practice to indicate that the client expects a JSON response.
*   **`Authorization`**: If authentication is implemented (e.g., JWT tokens), this header would carry the token: `Authorization: Bearer YOUR_TOKEN`. (Currently not implemented in the base API).

#### 7.3.3. Client-Side Validation

Before sending data to the API, perform client-side validation to provide immediate feedback to the user and reduce unnecessary API calls. This does not replace backend validation but enhances user experience.

*   **Use libraries**: `zod`, `yup`, or `joi` can define schemas for your forms and validate data.
*   **Simple checks**: For basic validation, inline checks can suffice.

**Example: Basic input validation for `video_id`**
```typescript
// In your component or form handling logic
const videoIdInput = "someUserInput";
if (!videoIdInput || !/^[a-zA-Z0-9_-]{11}$/.test(videoIdInput)) {
  setError("Invalid YouTube Video ID. It should be 11 characters long and contain letters, numbers, hyphens, or underscores.");
  setLoading(false);
  return; // Prevent API call
}
// Proceed with API call
```

### 7.4. Handling and Parsing API Responses

Robust response handling is key to a stable frontend.

#### 7.4.1. API Utility Functions and Response Handler

The provided `lib/api.ts` structure with a `handleResponse` function is a good foundation.

```typescript
// lib/api.ts (enhanced conceptual structure)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Define request/response interfaces (ideally generated from OpenAPI spec or shared types)
interface TranscribeRequest {
  video_id: string;
}

interface TranscriptResponse {
  youtube_video_id: string;
  title?: string | null;
  transcript: string;
  status?: string | null;
}

interface ProcessVideoRequest {
  video_id: string;
  force_regenerate?: boolean;
  style_preset?: string;
  custom_style?: CustomContentStyle;
}

interface CustomContentStyle {
  target_audience: string;
  call_to_action: string;
  content_goal: string;
  language?: string;
  tone?: string;
  additional_instructions?: string;
}

// Define other response types (ContentIdea, Reel, Tweet, etc.) as needed
// For brevity, ProcessVideoResponse is simplified here
interface ProcessVideoResponse {
  id?: number | null;
  youtube_video_id: string;
  title?: string | null;
  transcript?: string | null;
  status?: string | null;
  ideas?: any[] | null; // Replace 'any' with actual type
  content_pieces?: any[] | null; // Replace 'any' with actual type
  // ... other fields
}

interface ChannelVideosRequest {
  channel_id: string;
  max_videos: number;
}

// Define other specific response types for channel videos, etc.

interface ApiErrorDetail {
  loc?: (string | number)[];
  msg: string;
  type: string;
}

interface ApiErrorResponse {
  detail?: string | ApiErrorDetail[]; // FastAPI often uses 'detail'
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetailMessage = `API Error (${response.status}): ${response.statusText}`;
    try {
      const errorData: ApiErrorResponse = await response.json();
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorDetailMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Handle FastAPI validation errors
          errorDetailMessage = errorData.detail.map(err => `${err.loc?.join(' -> ')}: ${err.msg}`).join('; ');
        }
      }
    } catch (e) {
      // Response was not JSON or error parsing JSON
      // errorDetailMessage remains as statusText
    }
    // Consider creating custom error classes
    throw new Error(errorDetailMessage);
  }
  // If response.status is 204 No Content, response.json() will fail.
  if (response.status === 204) {
    return undefined as T; // Or an appropriate representation for "no content"
  }
  return response.json() as Promise<T>;
}

export async function transcribeVideo(videoId: string): Promise<TranscriptResponse> {
  const response = await fetch(`${API_BASE_URL}/transcribe/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ video_id: videoId } as TranscribeRequest),
  });
  return handleResponse<TranscriptResponse>(response);
}

export async function processVideo(
  videoId: string, 
  forceRegenerate: boolean = false,
  stylePreset?: string,
  customStyle?: CustomContentStyle
): Promise<ProcessVideoResponse> {
  const requestBody: ProcessVideoRequest = {
    video_id: videoId,
    force_regenerate: forceRegenerate
  };
  
  if (stylePreset) {
    requestBody.style_preset = stylePreset;
  }
  
  if (customStyle) {
    requestBody.custom_style = customStyle;
  }
  
  const response = await fetch(`${API_BASE_URL}/process-video/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  return handleResponse<ProcessVideoResponse>(response);
}

export async function getChannelVideos(channelId: string, maxVideos: number): Promise<any[]> { // Replace 'any[]' with actual type
    const response = await fetch(`${API_BASE_URL}/channel/videos/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({ channel_id: channelId, max_videos: maxVideos } as ChannelVideosRequest),
    });
    return handleResponse<any[]>(response);
}

// Content Style API Functions
export async function getStylePresets(): Promise<Record<string, any>> {
    const response = await fetch(`${API_BASE_URL}/content-styles/presets/`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    });
    const data = await handleResponse<{presets: Record<string, any>}>(response);
    return data.presets;
}

export async function getStylePreset(presetName: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/content-styles/presets/${presetName}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        },
    });
    return handleResponse<any>(response);
}
```

#### 7.4.2. HTTP Status Codes

Understand and handle common HTTP status codes:

*   **`200 OK`**: Standard success for GET, PUT, PATCH. Response body contains the resource.
*   **`201 Created`**: Success for POST requests that create a new resource. Response body often contains the created resource.
*   **`204 No Content`**: Success, but no content in the response body (e.g., after a successful DELETE). The `handleResponse` function should account for this.
*   **`400 Bad Request`**: Client error (e.g., malformed JSON, invalid parameters not caught by client-side validation). The response body usually contains error details.
*   **`401 Unauthorized`**: Authentication is required and has failed or has not yet been provided.
*   **`403 Forbidden`**: Authenticated, but not authorized to access the resource.
*   **`404 Not Found`**: The requested resource/endpoint does not exist.
*   **`422 Unprocessable Entity`**: FastAPI's default for request validation errors (Pydantic model validation). The response body will contain a `detail` field with an array of error locations and messages. The enhanced `handleResponse` above attempts to parse this.
*   **`500 Internal Server Error`**: A generic error on the server. The response body might contain some details, but often it's a sign of an unhandled exception in the backend.

#### 7.4.3. Frontend Validation of Received Data

Even with TypeScript, if API responses are not strictly typed or if there's a chance of API contract drift, consider validating the structure of received data.

*   **Libraries**: `zod` is excellent for this. Define a schema for the expected response and parse the data.

```typescript
// Conceptual example using Zod for response validation
import { z } from "zod";

const transcriptResponseSchema = z.object({
  youtube_video_id: z.string(),
  title: z.string().optional().nullable(),
  transcript: z.string(),
  status: z.string().optional().nullable(),
  // Add other fields as expected
});

// Inside your API call's .then() or after await
// const rawData = await handleResponse<any>(response); // Get raw data first
// try {
//   const validatedData = transcriptResponseSchema.parse(rawData);
//   // Use validatedData, now type-safe and structure-verified
//   setTranscriptResult(validatedData);
// } catch (validationError) {
//   console.error("Frontend data validation failed:", validationError.errors);
//   setError("Received unexpected data format from the server. Please try again.");
// }
```

#### 7.4.4. Displaying Informative Error Messages

Provide clear, user-friendly error messages.

*   **Specific errors**: If the API returns detailed validation messages (e.g., from FastAPI's 422 response), display them. "Video ID is required" is better than "Bad Request."
*   **General errors**: For network issues or 500 errors, a message like "An unexpected error occurred. Please try again later or contact support." is appropriate.
*   **UI feedback**: Use toasts, alert components, or inline messages near the relevant form fields.

```tsx
// In your component's error display logic
// {error && <p className="text-red-500">Error: {error}</p>} // (from original example)
// Enhanced:
{error && (
  <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg" role="alert">
    <span className="font-medium">Error:</span> {error}
  </div>
)}
```

### 7.5. Bulk Video Processing: `POST /process-videos-bulk/`

This endpoint allows for processing multiple videos in a single API request, which can be more efficient than sending individual requests for each video.

*   **Endpoint Purpose**: Process multiple videos in a single request.
*   **Method & URL**: `POST /process-videos-bulk/`
*   **Request Body**:
    The request body must be a JSON object containing a `video_ids` key. The value of `video_ids` should be a list of strings, where each string is a unique video ID. This structure corresponds to the backend's `BulkVideoProcessRequest` Pydantic model.

    **Example:**
    ```json
    {
      "video_ids": ["youtube_id_1", "youtube_id_2", "another_id"]
    }
    ```

*   **Frontend Request Example (Next.js with `fetch`)**:
    Here's how you might call this endpoint from a Next.js component. Ensure your `API_BASE_URL` is correctly defined, typically from an environment variable like `process.env.NEXT_PUBLIC_API_URL`.

    ```typescript
    // In your API utility file (e.g., lib/api.ts) or directly in a component
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    interface BulkVideoProcessResponseItem {
      video_id: string;
      status: 'success' | 'error' | 'pending' | string; // string for flexibility if other statuses exist
      details: string;
    }
    
    async function processVideosInBulk(videoIds: string[]): Promise<BulkVideoProcessResponseItem[]> {
      try {
        const response = await fetch(`${API_BASE_URL}/process-videos-bulk/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json', // Good practice
          },
          body: JSON.stringify({ video_ids: videoIds }),
        });

        if (!response.ok) {
          let errorDetailMessage = `API Error (${response.status}): ${response.statusText}`;
          try {
            const errorData = await response.json();
            if (errorData.detail) {
                 if (typeof errorData.detail === 'string') {
                    errorDetailMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) { // FastAPI validation errors
                    errorDetailMessage = errorData.detail.map((err: any) => `${err.loc?.join(' -> ')}: ${err.msg}`).join('; ');
                } else {
                    errorDetailMessage = JSON.stringify(errorData.detail);
                }
            }
          } catch (e) {
            // Response was not JSON or error parsing JSON
          }
          throw new Error(errorDetailMessage);
        }
        
        return response.json() as Promise<BulkVideoProcessResponseItem[]>;
      } catch (error) {
        console.error("Error processing videos in bulk:", error);
        if (error instanceof Error) {
            throw error;
        }
        throw new Error('An unknown error occurred during bulk video processing.');
      }
    }

    // Example usage in a component:
    // 
    // const MyComponent = () => {
    //   const [results, setResults] = useState<BulkVideoProcessResponseItem[]>([]);
    //   const [error, setError] = useState<string | null>(null);
    //   const [isLoading, setIsLoading] = useState(false);
    //
    //   const handleBulkProcess = async (ids: string[]) => {
    //     setIsLoading(true);
    //     setError(null);
    //     try {
    //       const data = await processVideosInBulk(ids);
    //       setResults(data);
    //     } catch (e: any) {
    //       setError(e.message || "Failed to process videos.");
    //     } finally {
    //       setIsLoading(false);
    //     }
    //   };
    //   
    //   // Call handleBulkProcess(["id1", "id2", "id3"]) when needed
    //   // Then render results, loading state, or error message
    // };
    ```

*   **Response Body**:
    The backend responds with a JSON list of objects. Each object in the list provides details about the processing status for one of the requested video IDs. This structure corresponds to the backend's `BulkVideoProcessResponseItem` Pydantic model.

    **Example:**
    ```json
    [
      {"video_id": "youtube_id_1", "status": "success", "details": "Video processed and repurposed text generated."},
      {"video_id": "youtube_id_2", "status": "error", "details": "Failed to fetch video transcript."},
      {"video_id": "another_id", "status": "pending", "details": "Processing initiated."}
    ]
    ```

*   **Handling the Response**:
    The frontend should iterate through the response array. For each item (representing a `BulkVideoProcessResponseItem`), it can check the `video_id`, `status`, and `details` to update the UI accordingly. This could involve:
    *   Displaying a success message for successfully processed videos.
    *   Showing an error message for videos that failed.
    *   Indicating a pending or in-progress status for others.
    *   Updating specific UI elements tied to each video ID.
### 7.6. Data Flow and Integrity (SQLite via FastAPI)

The FastAPI backend uses an SQLite database to persist data like video details, transcripts, and generated content.

#### 7.6.1. API as the Data Mediator

*   **All database interactions are handled by FastAPI.** The frontend requests data or initiates data changes through API calls.
*   **Fetching Data**: To display data stored in the database (e.g., a list of previously transcribed videos, details of a specific video), the frontend will call GET endpoints (e.g., `GET /videos/`, `GET /videos/{video_id}/`). *Note: These GET endpoints for fetching persisted collections or items might need to be added to the FastAPI backend if not already present; the current guide primarily focuses on POST endpoints for processing.*
*   **Modifying Data**: Operations like creating new entries (e.g., submitting a video for processing via `POST /process-video/`), updating, or deleting records are all done via specific API endpoints (POST, PUT, DELETE).

#### 7.6.2. Interpreting Database-Originated Data

When the frontend receives data from an API call that originated from the database:
*   Ensure your TypeScript interfaces or validation schemas accurately reflect the data structure.
*   Map the data fields to your UI components correctly. For example, a `video.title` from the API response would populate a title display element.

#### 7.6.3. Frontend Caching and Data Consistency

To improve performance and user experience, you might cache API responses on the client-side. Libraries like React Query (TanStack Query) or SWR are highly recommended for this, as they handle caching, background updates, and stale-while-revalidate logic.

If implementing manual caching or using simpler state management:

*   **Cache Invalidation**: After any operation that modifies data on the backend (e.g., `POST /process-video/`, or any PUT/DELETE requests), ensure that related cached data is invalidated or refetched.
    *   **Example**: If you display a list of processed videos fetched via `GET /processed-videos/`, after a successful `POST /process-video/` for a new video, the list should be refetched or the new item should be added to the cached list.
*   **Optimistic Updates**: For a snappier UI, you can optimistically update the frontend state immediately upon user action, assuming success. Then, on API response, confirm or revert the change.
    *   **Example**: When a user clicks "Transcribe," you might immediately show a "Transcription in progress..." status in the UI for that video, even before the API call completes.
*   **Polling for Long-Running Tasks**: If operations like video processing are long-running, the initial API call might return a "processing started" response. The frontend might then need to poll a status endpoint (e.g., `GET /process-video/{task_id}/status`) periodically to get updates, or use WebSockets if the backend supports real-time communication.

### 7.7. Example API Usage in a Component (Conceptual Enhancement)

The example component from the original guide (`app/page.tsx`) provides a good starting point. Consider these enhancements:

*   **Typed state**: Use the defined TypeScript interfaces for `transcriptResult` and `processResult`.
*   **More granular loading states**: `isLoadingTranscript`, `isProcessingVideo`.
*   **Parsing API errors**: The `catch` block in `handleTranscribe` and `handleProcess` can use the error message from the enhanced `handleResponse`.

```tsx
// Example in a React component (e.g., app/page.tsx) - conceptual enhancements
"use client";

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
// Assuming api.ts is in @/lib/api and exports typed functions and interfaces
import { transcribeVideo, processVideo, TranscriptResponse, ProcessVideoResponse } from '@/lib/api'; 
import { Progress } from "@/components/ui/progress"; // Example for progress display

export default function HomePage() {
  const [videoId, setVideoId] = useState('');
  const [transcriptResult, setTranscriptResult] = useState<TranscriptResponse | null>(null);
  const [processResult, setProcessResult] = useState<ProcessVideoResponse | null>(null);
  
  const [isLoadingTranscript, setIsLoadingTranscript] = useState(false);
  const [isProcessingVideo, setIsProcessingVideo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0); // For long tasks

  // Simulate progress for demo
  useEffect(() => {
    if (isLoadingTranscript || isProcessingVideo) {
      let currentProgress = 0;
      const interval = setInterval(() => {
        currentProgress += 10;
        if (currentProgress <= 100) {
          setProgress(currentProgress);
        } else {
          clearInterval(interval);
        }
      }, 200);
      return () => clearInterval(interval);
    } else {
      setProgress(0);
    }
  }, [isLoadingTranscript, isProcessingVideo]);

  const handleTranscribe = async () => {
    if (!videoId.trim()) {
      setError("Please enter a YouTube Video ID.");
      return;
    }
    // Basic client-side validation example
    if (!/^[a-zA-Z0-9_-]{11}$/.test(videoId)) {
        setError("Invalid YouTube Video ID format. It should be 11 characters.");
        return;
    }

    setIsLoadingTranscript(true);
    setError(null);
    setTranscriptResult(null);
    setProgress(0);
    try {
      const data = await transcribeVideo(videoId);
      setTranscriptResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to transcribe video.");
    } finally {
      setIsLoadingTranscript(false);
    }
  };

  const handleProcess = async () => {
    if (!videoId.trim()) {
      setError("Please enter a YouTube Video ID.");
      return;
    }
     if (!/^[a-zA-Z0-9_-]{11}$/.test(videoId)) {
        setError("Invalid YouTube Video ID format. It should be 11 characters.");
        return;
    }
    setIsProcessingVideo(true);
    setError(null);
    setProcessResult(null);
    setProgress(0);
    try {
      // Assuming forceRegenerate is false for this example
      const data = await processVideo(videoId, false); 
      setProcessResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to process video.");
    } finally {
      setIsProcessingVideo(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">YouTube Repurposer Frontend</h1>
      <div className="mb-4 space-y-2">
        <Input
          type="text"
          placeholder="Enter YouTube Video ID (e.g., dQw4w9WgXcQ)"
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
          className="max-w-sm"
          aria-label="YouTube Video ID"
        />
      </div>
      <div className="space-x-2 mb-4">
        <Button onClick={handleTranscribe} disabled={isLoadingTranscript || isProcessingVideo}>
          {isLoadingTranscript ? 'Transcribing...' : 'Get Transcript'}
        </Button>
        <Button onClick={handleProcess} disabled={isLoadingTranscript || isProcessingVideo}>
          {isProcessingVideo ? 'Processing...' : 'Process Video'}
        </Button>
      </div>

      {(isLoadingTranscript || isProcessingVideo) && progress > 0 && (
        <div className="my-4 max-w-sm">
          <Progress value={progress} className="w-full" />
          <p className="text-sm text-muted-foreground text-center mt-1">{progress}%</p>
        </div>
      )}

      {error && (
        <div className="my-4 p-3 border border-destructive bg-destructive/10 text-destructive rounded-md max-w-md">
          <h3 className="font-semibold">Error</h3>
          <p>{error}</p>
        </div>
      )}

      {transcriptResult && (
        <div className="mt-6 p-4 border rounded-md bg-card">
          <h2 className="text-xl font-semibold mb-2">Transcript Result</h2>
