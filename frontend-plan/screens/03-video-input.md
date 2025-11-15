# Video Input Screen

## Overview
Single video processing interface. User inputs YouTube URL, optionally customizes style, and generates content. Focus on simplicity with progressive disclosure for advanced options.

---

## Layout Structure

```
┌────────────────────────────────────────────────────────────┐
│ [Top Nav]                                                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  Process New Video               [Dashboard ←]   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  ╔════════════════════════════════════════════╗  │     │
│  │  ║  Step 1: Video Input                       ║  │     │
│  │  ╚════════════════════════════════════════════╝  │     │
│  │                                                   │     │
│  │  YouTube URL *                                    │     │
│  │  ┌─────────────────────────────────────────┐    │     │
│  │  │ https://youtube.com/watch?v=...  [Paste]│    │     │
│  │  └─────────────────────────────────────────┘    │     │
│  │  Enter the URL of the video you want to process │     │
│  │                                                   │     │
│  │  [Fetch Video Info] ← appears after valid URL   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  Video Preview (after fetch)                      │     │
│  │  ┌──────────────┐  Title: ...                    │     │
│  │  │  [Thumbnail] │  Channel: ...                  │     │
│  │  │              │  Duration: 12:34               │     │
│  │  └──────────────┘  Views: 1.2M                   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  ╔════════════════════════════════════════════╗  │     │
│  │  ║  Step 2: Content Style                     ║  │     │
│  │  ╚════════════════════════════════════════════╝  │     │
│  │                                                   │     │
│  │  Style Preset                                     │     │
│  │  ┌─────────────────────────────────────────┐    │     │
│  │  │ Professional Business ▼                  │    │     │
│  │  └─────────────────────────────────────────┘    │     │
│  │                                                   │     │
│  │  Target Audience: Business professionals         │     │
│  │  Tone: Professional & authoritative              │     │
│  │  Language: English                               │     │
│  │                                                   │     │
│  │  [Customize Style...] (expandable)               │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │  Advanced Options (collapsed by default)          │     │
│  │  [> Show Advanced Options]                        │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │                                                   │     │
│  │              [Generate Content]                   │     │
│  │                                                   │     │
│  └──────────────────────────────────────────────────┘     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Section: Page Header

```
Padding: 32px
Border-bottom: 1px solid --border

Layout: Flex, space-between

Left:
  "Process New Video" (h1, 36px)
  "Transform YouTube videos into engaging social media content"
  (body, --muted-foreground, margin-top: 8px)
  
Right:
  "Back to Dashboard" link (body, --primary)
  Or breadcrumb: Dashboard > Process Video
```

---

## Section: Step 1 - Video Input

```
Card:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-lg
  Padding: 32px
  Margin: 32px

Step Header:
  Background: --primary/5
  Border: 1px solid --primary/20
  Border-radius: --radius
  Padding: 12px 16px
  Font: label, semibold, --primary
  Margin-bottom: 24px
  
Form:
  YouTube URL Field:
    Label: "YouTube URL" + required indicator (*)
    Input: Large size (48px)
    Placeholder: "https://youtube.com/watch?v=..."
    Icon: YouTube logo (left side)
    Paste button (right side, ghost)
    Helper text below: "Enter the URL..."
    
  Validation:
    - Empty: No error shown initially
    - Invalid URL: "Please enter a valid YouTube URL"
    - Valid: Green checkmark icon
    - After valid: Show "Fetch Video Info" button
    
  Fetch Button:
    Appears below input after valid URL
    Secondary button
    Text: "Fetch Video Info"
    Loading state: Spinner + "Fetching..."
```

### States

**Empty**
- Clean slate, ready for input
- Paste button subtle

**Typing**
- Real-time URL validation
- Show checkmark when valid

**Fetching**
- Button disabled, spinner
- Input disabled
- "Fetching video information..." text

**Fetched Success**
- Show Video Preview section
- Enable Step 2
- Auto-scroll to preview

**Fetch Error**
- Error message: "Could not fetch video. Please check the URL."
- Retry button
- Keep input editable

---

## Section: Video Preview

**Only visible after successful fetch**

```
Card:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-lg
  Padding: 24px
  Margin: 32px
  Animation: Slide down + fade in

Layout: Flex, gap: 24px

Left - Thumbnail:
  Width: 200px (desktop), 100% (mobile)
  Aspect: 16:9
  Border-radius: --radius-md
  Object-fit: cover
  Shadow: --shadow-sm
  
Right - Metadata:
  Title: h3, 24px, 2 lines max
  Channel: body-sm, --muted-foreground
  Duration: body-sm, --muted-foreground
  Views: body-sm, --muted-foreground (optional)
  
  Layout: Stack, gap: 8px
  
  Optional: Transcript preview
    "Preview Transcript" expandable button
    Show first 200 chars in muted text
```

### Mobile Layout
- Stack vertically
- Thumbnail: Full width
- Metadata below

---

## Section: Step 2 - Content Style

```
Card: Same styling as Step 1
Enabled only after video fetched

Step Header: Same as Step 1

Form:
  Style Preset Dropdown:
    Label: "Style Preset"
    Select: Large size
    Default: "Professional Business"
    
    Options:
      - Professional Business
      - Social Media Casual
      - E-commerce Entrepreneur
      - Educational Content
      - Fitness & Wellness
      - Custom (bottom, divider above)
    
  Preset Preview (below dropdown):
    Background: --muted
    Border-radius: --radius
    Padding: 16px
    Font: body-sm
    
    Display:
      • Target Audience: ...
      • Tone: ...
      • Language: ...
      • Call to Action: ...
    
    Icon: Info circle with tooltip
    
  Customize Button:
    Ghost button
    Text: "Customize Style..."
    Icon: Settings
    Click → Expand custom options
```

### Custom Style Options (Collapsed by Default)

**When "Customize Style..." clicked:**

```
Expand with smooth animation
Show all fields:

┌─────────────────────────────────────────┐
│ Custom Style Configuration              │
│                                         │
│ Target Audience                         │
│ [_________________________________]     │
│ E.g., "tech entrepreneurs"              │
│                                         │
│ Content Goal                            │
│ [_________________________________]     │
│ E.g., "education, lead generation"      │
│                                         │
│ Tone                                    │
│ [_________________________________]     │
│ E.g., "professional, inspiring"         │
│                                         │
│ Language                                │
│ [English ▼]                             │
│                                         │
│ Call to Action                          │
│ [_________________________________]     │
│ E.g., "Subscribe for more tips"         │
│                                         │
│ Additional Instructions (optional)      │
│ [________________________________       │
│  ________________________________]      │
│                                         │
│ [Use Preset] [Apply Custom]            │
└─────────────────────────────────────────┘

Fields:
  All text inputs, large size
  Helper text below each
  Character counters where appropriate
  
Buttons:
  "Use Preset" - Cancel custom, go back to preset
  "Apply Custom" - Validate and apply
```

---

## Section: Advanced Options (Collapsed)

```
Card: Same styling
Collapsed by default

Header (collapsed):
  "> Show Advanced Options"
  Ghost button, full width, left-aligned
  Icon: Chevron right
  
When expanded:
  Icon rotates to chevron down
  Content slides down
  
Content:
  ┌─────────────────────────────────────────┐
  │ Content Configuration                   │
  │                                         │
  │ [ ] Force regenerate (even if exists)  │
  │                                         │
  │ Content Ideas Range                     │
  │ Min: [6▼]  Max: [8▼]                    │
  │                                         │
  │ Carousel Slides                         │
  │ Min: [4▼]  Max: [8▼]                    │
  │                                         │
  │ Carousel Slide Length (characters)      │
  │ [800_____]  (slider, 300-1200)          │
  │                                         │
  │ [Reset to Defaults]                     │
  └─────────────────────────────────────────┘
  
Components:
  - Checkbox for force regenerate
  - Number selects for ranges
  - Slider for character length
  - Reset button (ghost, small)
```

---

## Section: Generate Button

```
Position: Fixed bottom on mobile, static on desktop
Background: --background (mobile bar)
Border-top: 1px solid --border (mobile)
Padding: 16px 32px
Text-align: center

Button:
  Primary, large size (48px)
  Width: Full (mobile), auto (desktop)
  Text: "Generate Content"
  Icon: Sparkles or magic wand
  
  Disabled until:
    - Valid video URL
    - Video info fetched
    - Style selected
    
  Hover:
    Scale 1.05
    Shadow increase
    
  Loading:
    Spinner
    Text: "Generating..."
    Disable input
```

---

## Processing Flow

### After "Generate Content" Clicked

**Step 1: Validation**
- Validate all inputs
- Show errors if any
- Auto-focus first error

**Step 2: Submit**
- API call: POST /process-video/
- Show loading overlay or inline progress

**Step 3: Processing**

```
┌─────────────────────────────────────────┐
│  Processing Your Video                  │
│                                         │
│  ┌───────────────────────────────┐     │
│  │  [Progress Bar]       67%     │     │
│  └───────────────────────────────┘     │
│                                         │
│  ✓ Fetching transcript                 │
│  ✓ Analyzing content                   │
│  ⏳ Generating ideas...                │
│  ○ Creating content pieces             │
│                                         │
│  Estimated time: 2 minutes              │
│                                         │
│  [Cancel Processing]                    │
└─────────────────────────────────────────┘

Overlay:
  Modal or inline card
  Can't be dismissed (except cancel)
  Real-time progress updates
  
Steps:
  Each step shows status:
    ○ Not started (gray)
    ⏳ In progress (amber, animated)
    ✓ Complete (green)
    ✗ Error (red)
```

**Step 4: Success**

```
Success screen:
  ┌─────────────────────────────────────────┐
  │  ✓ Content Generated Successfully!      │
  │                                         │
  │  Generated 8 pieces of content:         │
  │  • 3 Instagram Reels                    │
  │  • 3 Image Carousels                    │
  │  • 2 Twitter Threads                    │
  │                                         │
  │  [View Content] [Process Another]      │
  └─────────────────────────────────────────┘
  
Auto-dismiss after 3 seconds OR
Wait for user action

Actions:
  "View Content" → Navigate to content library (filtered to this video)
  "Process Another" → Reset form, stay on page
```

**Step 5: Error**

```
Error screen:
  ┌─────────────────────────────────────────┐
  │  ✗ Processing Failed                    │
  │                                         │
  │  We couldn't process this video.        │
  │  Error: [Error message from API]        │
  │                                         │
  │  [Try Again] [Contact Support]         │
  └─────────────────────────────────────────┘
  
Actions:
  "Try Again" → Retry same request
  "Contact Support" → Link to support
  "Go Back" → Return to form
```

---

## Responsive Behavior

### Desktop (≥1024px)
- Max-width: 800px, centered
- Generous spacing (32px)
- Side-by-side thumbnail + metadata

### Tablet (768px - 1023px)
- Max-width: 700px
- Moderate spacing (24px)
- Maintain side-by-side layout

### Mobile (<768px)
- Full width with 16px padding
- Stack all elements vertically
- Fixed bottom bar for Generate button
- Larger touch targets (48px min)
- Thumbnail full width

---

## User Interactions Summary

### Initial Load
1. Focus on URL input
2. Paste button appears on hover/focus
3. Helper text visible

### URL Input
1. User types or pastes URL
2. Real-time validation
3. Valid → Show "Fetch Video Info" button
4. Click Fetch → API call → Show preview

### Style Selection
1. Default preset pre-selected
2. User can change preset → Preview updates
3. Click "Customize" → Expand custom form
4. Fill custom fields → "Apply Custom" validates

### Advanced Options
1. Click "Show Advanced" → Expand section
2. Adjust settings
3. Values update form state
4. Click "Reset to Defaults" → Restore default values

### Generate
1. Click "Generate Content" → Validate → Submit
2. Show processing overlay
3. Poll for status OR WebSocket updates
4. Success → Show result → Navigate to library
5. Error → Show error → Retry option

---

## Data Requirements

### API Calls

```javascript
// Fetch video info
GET /video-info?url={youtubeURL}
Response: {
  video_id: string
  title: string
  channel: string
  duration: number
  thumbnail: string
  view_count: number (optional)
}

// Get style presets
GET /content-styles/presets/
Response: {
  presets: StylePreset[]
}

// Process video
POST /process-video/
Body: {
  video_id: string
  style_preset?: string
  custom_style?: CustomStyle
  force_regenerate?: boolean
  content_config?: {
    min_ideas: number
    max_ideas: number
    field_limits: {...}
  }
}
Response: {
  id: number
  youtube_video_id: string
  title: string
  status: "processing" | "completed" | "failed"
  content_pieces: ContentPiece[]
}

// Check processing status
GET /processing-status/{video_id}
Response: {
  status: string
  progress: number (0-100)
  current_step: string
  estimated_time_seconds: number
}
```

---

## Edge Cases

### URL Already Processed
- Show warning: "This video was already processed"
- Options: "View Existing Content" or "Regenerate"

### Transcript Not Available
- Error: "Transcript not available for this video"
- Suggest: Upload manual transcript (future feature)

### API Rate Limit
- Error: "Rate limit reached. Try again in X seconds."
- Show countdown timer
- Disable submit button

### Network Error
- Retry button
- Offline indicator
- Save form state

---

## Accessibility

- All form fields labeled
- Error messages announced
- Focus management through steps
- Keyboard shortcuts (Enter to submit)
- Progress announcements for screen readers
- Color + icon for status
- Skip to content button
