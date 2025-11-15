# Bulk Processing Screen

## Overview
Process multiple YouTube videos simultaneously. Queue management, batch style application, and progress monitoring. Power-user feature with streamlined UX.

---

## Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│ [Top Nav]                                                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Bulk Video Processing              [Dashboard ←] │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  ╔═══════════════════════════════════════════════╗ │     │
│  │  ║  Step 1: Add Videos                           ║ │     │
│  │  ╚═══════════════════════════════════════════════╝ │     │
│  │                                                    │     │
│  │  [Textarea for URLs]                              │     │
│  │  Or [Upload File] [Import from Channel]          │     │
│  │                                                    │     │
│  │  [Parse Videos]                                   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Video Queue (5 videos)               [Clear All] │     │
│  │                                                    │     │
│  │  ┌──────────────────────────────────────────┐     │     │
│  │  │ 1. [Thumb] Video Title         [Remove]  │     │     │
│  │  │    ID: abc123 • 12:34 • Ready            │     │     │
│  │  └──────────────────────────────────────────┘     │     │
│  │  ┌──────────────────────────────────────────┐     │     │
│  │  │ 2. [Thumb] Video Title         [Remove]  │     │     │
│  │  │    ID: def456 • 8:45 • Ready             │     │     │
│  │  └──────────────────────────────────────────┘     │     │
│  │  ...                                               │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  ╔═══════════════════════════════════════════════╗ │     │
│  │  ║  Step 2: Configure Style (Optional)           ║ │     │
│  │  ╚═══════════════════════════════════════════════╝ │     │
│  │                                                    │     │
│  │  Apply same style to all videos                   │     │
│  │  [Professional Business ▼]                        │     │
│  │                                                    │     │
│  │  ☐ Use different styles per video                 │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │                                                    │     │
│  │              [Start Processing]                    │     │
│  │          Process 5 videos with style X             │     │
│  │                                                    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Section: Page Header

```
Padding: 32px
Border-bottom: 1px solid --border

Layout: Flex, space-between

Left:
  "Bulk Video Processing" (h1, 36px)
  "Process multiple videos at once"
  (body, --muted-foreground)
  
Right:
  "Back to Dashboard" link
  Or breadcrumb navigation
```

---

## Section: Step 1 - Add Videos

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
  Icon: "1" badge

Input Methods (Tabs):
  [Paste URLs] [Upload File] [From Channel]

Tab 1: Paste URLs
  ┌─────────────────────────────────────────────┐
  │ YouTube Video URLs                          │
  │ ───────────────────                         │
  │                                             │
  │ [Textarea - 8 rows]                         │
  │ Paste one URL per line:                     │
  │ https://youtube.com/watch?v=...             │
  │ https://youtube.com/watch?v=...             │
  │ https://youtu.be/...                        │
  │                                             │
  └─────────────────────────────────────────────┘
  
  Helper text: "One URL per line, up to 50 videos"
  Character/line counter
  
Tab 2: Upload File
  ┌─────────────────────────────────────────────┐
  │ Upload Text File                            │
  │ ───────────────                             │
  │                                             │
  │  [Drag & Drop Zone]                         │
  │                                             │
  │  Drop .txt or .csv file here                │
  │  or [Browse Files]                          │
  │                                             │
  │  Accepted formats: TXT, CSV                 │
  │  Max: 50 videos                             │
  │                                             │
  └─────────────────────────────────────────────┘
  
Tab 3: From Channel
  ┌─────────────────────────────────────────────┐
  │ Import from YouTube Channel                 │
  │ ──────────────────────────                  │
  │                                             │
  │ Channel ID or URL                           │
  │ [_______________________________]           │
  │                                             │
  │ Number of recent videos to import           │
  │ [10 ▼]  (Max: 50)                           │
  │                                             │
  │ [Fetch Videos]                              │
  │                                             │
  └─────────────────────────────────────────────┘

[Parse Videos] Button:
  Primary, large
  Full width or prominent
  Text: "Parse Videos" or "Add to Queue"
  Icon: Plus
  
  Disabled until:
    - URLs entered OR file uploaded OR channel videos fetched
    
  Loading:
    Spinner + "Parsing..."
```

---

## Section: Video Queue

**Appears after videos parsed**

```
Card:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-lg
  Padding: 24px
  Margin: 32px
  Animation: Slide down + fade in

Header:
  Flex, space-between
  
  Left:
    "Video Queue" (h3, 24px)
    Count badge: "5 videos"
    
  Right:
    [Clear All] button (ghost, small)
    [Import More] button (secondary, small)

List of videos:
  ┌──────────────────────────────────────────────┐
  │ 1. ┌────┐ Video Title Here                   │
  │    │Img │ ID: abc123def • Duration: 12:34    │
  │    └────┘ Status: ✓ Ready                    │
  │           [Remove]                  [↑] [↓]  │
  ├──────────────────────────────────────────────┤
  │ 2. ┌────┐ Another Video                      │
  │    │Img │ ID: ghi789jkl • Duration: 8:45     │
  │    └────┘ Status: ✓ Ready                    │
  │           [Remove]                  [↑] [↓]  │
  └──────────────────────────────────────────────┘

Video item:
  Background: --background
  Border: 1px solid --border
  Border-radius: --radius-md
  Padding: 16px
  Margin-bottom: 12px
  Display: Flex
  Gap: 16px
  Align: center
  
  Hover: Border stronger, shadow
  
  Structure:
    [#] [Thumbnail] [Info] [Actions] [Reorder]
    
  Number:
    Font: h6, --muted-foreground
    
  Thumbnail:
    Width: 80px
    Aspect: 16:9
    Border-radius: --radius-sm
    
  Info:
    Flex: 1
    
    Title: h6, line-clamp 1
    Metadata: caption, --muted-foreground
      - Video ID (monospace)
      - Duration
    Status: Badge
      - ✓ Ready (green)
      - ⏳ Processing (amber)
      - ✗ Error (red)
      
  Actions:
    [Remove] button (ghost, small, destructive)
    
  Reorder:
    [↑] [↓] buttons (ghost, small)
    Or drag handle (☰)

States:
  Ready: Default appearance
  Processing: Progress bar below
  Complete: Green border, checkmark
  Error: Red border, error icon
  
Empty state:
  "No videos in queue. Add videos above."
  Icon: Empty box
```

---

## Section: Step 2 - Configure Style

```
Card: Same styling as Step 1

Step Header: "2" badge

Form:
  Apply Style to All Videos
  ────────────────────────────
  
  ☑ Use same style for all videos
  
  Style Preset
  [Professional Business ▼]
  
  Preview:
    Target: Business professionals
    Tone: Professional
    Language: English
    
  [Customize Style...] (expandable)
  
  ──────────────────────────────────
  
  Advanced Options
  ────────────────
  
  ☐ Use different styles per video
    (When checked, show style selector per video in queue)
    
  ☐ Skip videos already processed
  
  ☐ Force regenerate existing content
```

### Per-Video Style (When Enabled)

```
Video queue items show style dropdown:

┌──────────────────────────────────────────────┐
│ 1. [Thumb] Video Title                       │
│    Style: [Professional ▼]      [Remove]    │
├──────────────────────────────────────────────┤
│ 2. [Thumb] Video Title                       │
│    Style: [Casual ▼]             [Remove]    │
└──────────────────────────────────────────────┘

Allows different style per video
More complex but more flexible
```

---

## Section: Process Button

```
Position: Sticky bottom on mobile, static on desktop
Background: --card (mobile bar)
Border-top: 1px solid --border (mobile)
Padding: 24px 32px
Text-align: center

Button:
  Primary, large (48px height)
  Width: Full (mobile), auto (desktop)
  Min-width: 320px
  Text: "Start Processing"
  Icon: Play or sparkles
  
  Below button:
    Caption text: "Process 5 videos with Professional style"
    
  Disabled until:
    - Queue has videos
    - All videos ready (no errors)
    - Style selected (if required)
    
  Loading:
    Spinner
    Text: "Starting..."
```

---

## Processing View

**After "Start Processing" clicked**

```
Replace form with processing status:

┌──────────────────────────────────────────────────┐
│ Processing Videos...                             │
│                                                  │
│ Overall Progress                                 │
│ [████████████░░░░] 60% (3/5 complete)           │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ ✓ Video 1: Complete                        │  │
│ │   Generated 8 content pieces               │  │
│ │   [View Content]                           │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ ✓ Video 2: Complete                        │  │
│ │   Generated 7 content pieces               │  │
│ │   [View Content]                           │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ ⏳ Video 3: Processing...                  │  │
│ │   [Progress Bar] 45%                       │  │
│ │   Generating ideas...                      │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ ○ Video 4: Queued                          │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ ○ Video 5: Queued                          │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ Estimated time remaining: 4 minutes              │
│                                                  │
│ [Cancel All] [Pause]                             │
└──────────────────────────────────────────────────┘

Status indicators:
  ✓ Complete (green)
  ⏳ Processing (amber, animated)
  ✗ Failed (red)
  ○ Queued (gray)

Real-time updates via WebSocket or polling
Can't navigate away (confirm if try)
```

---

## Completion View

**After all videos processed**

```
┌──────────────────────────────────────────────────┐
│ ✓ Processing Complete!                           │
│                                                  │
│ Successfully processed 5 videos                  │
│ Generated 38 total content pieces                │
│                                                  │
│ Summary:                                         │
│ • 5 videos processed                             │
│ • 15 Instagram Reels                             │
│ • 13 Image Carousels                             │
│ • 10 Twitter Threads                             │
│ • 0 errors                                       │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ ✓ Video 1: 8 pieces  [View]                │  │
│ │ ✓ Video 2: 7 pieces  [View]                │  │
│ │ ✓ Video 3: 8 pieces  [View]                │  │
│ │ ✓ Video 4: 7 pieces  [View]                │  │
│ │ ✓ Video 5: 8 pieces  [View]                │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ [View All Content] [Export All] [Process More]  │
│                                                  │
└──────────────────────────────────────────────────┘

Success state:
  Green checkmark
  Summary stats
  List of results
  Action buttons
  
Actions:
  View All Content → Library (filtered)
  Export All → Export modal
  Process More → Reset form
```

---

## Error Handling

### Partial Failure

```
┌──────────────────────────────────────────────────┐
│ ⚠ Processing Complete with Errors                │
│                                                  │
│ Processed 3 of 5 videos successfully             │
│                                                  │
│ ✓ Video 1: Success - 8 pieces                    │
│ ✓ Video 2: Success - 7 pieces                    │
│ ✗ Video 3: Failed - Transcript not available     │
│   [Retry] [View Details]                         │
│ ✓ Video 4: Success - 8 pieces                    │
│ ✗ Video 5: Failed - Invalid video ID             │
│   [Retry] [View Details]                         │
│                                                  │
│ [Retry Failed] [View Successful] [Process More]  │
│                                                  │
└──────────────────────────────────────────────────┘

Shows which succeeded and which failed
Offers retry for failed items
Clear error messages
```

---

## Responsive Behavior

### Desktop (≥1024px)
- Full layout
- Side-by-side elements where possible
- Larger queue preview

### Tablet (768px - 1023px)
- Stack some elements
- Maintain functionality
- Scrollable queue

### Mobile (<768px)
- Single column
- Compact queue items
- Fixed bottom process button
- Collapsible sections
- Smaller thumbnails

---

## User Interactions

### Add Videos Flow
1. Choose input method (paste/upload/channel)
2. Enter URLs or upload file
3. Click "Parse Videos"
4. System validates URLs
5. Fetch video metadata
6. Add to queue with thumbnails
7. Show queue section

### Queue Management
1. Reorder videos (drag or buttons)
2. Remove unwanted videos
3. Clear all and start over
4. Add more videos

### Configure & Process
1. Select style preset (or per-video)
2. Toggle advanced options
3. Review queue one last time
4. Click "Start Processing"
5. Watch progress in real-time
6. View results as complete
7. Access generated content

### During Processing
1. Can pause processing (optional)
2. Can cancel individual videos
3. Can cancel all
4. View real-time status
5. Estimated time updates

---

## Data Requirements

```javascript
// Parse video URLs
POST /bulk/parse-urls
Body: {
  urls: string[]
}
Response: {
  videos: VideoInfo[]
  errors: {url: string, error: string}[]
}

// Fetch channel videos
POST /bulk/channel-videos
Body: {
  channel_id: string
  max_videos: number
}
Response: {
  videos: VideoInfo[]
}

// Start bulk processing
POST /bulk/process
Body: {
  video_ids: string[]
  style_preset?: string
  custom_styles?: {[video_id]: CustomStyle}
  force_regenerate?: boolean
}
Response: {
  batch_id: string
  status: "processing"
}

// Check batch status
GET /bulk/status/{batch_id}
Response: {
  batch_id: string
  total: number
  completed: number
  failed: number
  in_progress: number
  videos: {
    video_id: string
    status: "queued" | "processing" | "complete" | "failed"
    progress: number
    content_pieces?: number
    error?: string
  }[]
}

// Cancel batch
POST /bulk/cancel/{batch_id}
```

---

## Edge Cases

### Duplicate Videos
- Detect duplicates in queue
- Show warning
- Offer: Remove duplicates or keep all

### Rate Limiting
- Show "Queue full" message
- Display wait time
- Offer: Process now or schedule for later

### Invalid URLs
- Highlight invalid URLs during parse
- Allow: Fix or remove
- Block processing until fixed

### Mixed Success/Failure
- Show partial success clearly
- Offer retry for failures
- Don't lose successful results

### Connection Loss
- Save progress
- Resume on reconnect
- Show offline indicator

---

## Performance Considerations

- Process videos sequentially or in batches (API limit)
- Show progress for each video
- Allow background processing (optional)
- Notify when complete (if user navigated away)
- Efficient polling or WebSocket updates

---

## Accessibility

- Keyboard navigation through queue
- Focus management during processing
- Screen reader status announcements
- Progress updates announced
- Error messages accessible
- Pause/cancel keyboard shortcuts
