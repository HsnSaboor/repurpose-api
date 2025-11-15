# Dashboard Screen

## Overview
Main landing page after authentication. Provides overview of activity, quick actions, and recent content. Emphasizes speed and clarity.

---

## Layout Structure

```
┌────────────────────────────────────────────────────────────────┐
│ [Top Nav: Logo | Dashboard | Library | Settings | Profile]    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Dashboard                                  [+ New] │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Quick Actions (Prominent CTAs)                      │     │
│  │                                                       │     │
│  │  ┌─────────────────┐  ┌──────────────────┐          │     │
│  │  │  Process Video  │  │  Bulk Processing │          │     │
│  │  │  [Icon]         │  │  [Icon]          │          │     │
│  │  └─────────────────┘  └──────────────────┘          │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Stats Overview                                       │     │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐            │     │
│  │  │ 147  │  │ 89   │  │ 234  │  │ 3.2K │            │     │
│  │  │Videos│  │Reels │  │Tweets│  │Views │            │     │
│  │  └──────┘  └──────┘  └──────┘  └──────┘            │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Recent Content                  [View All →]        │     │
│  │                                                       │     │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐    │     │
│  │  │[Thumb] │  │[Thumb] │  │[Thumb] │  │[Thumb] │    │     │
│  │  │Title   │  │Title   │  │Title   │  │Title   │    │     │
│  │  │Type•ID │  │Type•ID │  │Type•ID │  │Type•ID │    │     │
│  │  │[Edit]  │  │[Edit]  │  │[Edit]  │  │[Edit]  │    │     │
│  │  └────────┘  └────────┘  └────────┘  └────────┘    │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Processing Queue (if any)                            │     │
│  │                                                       │     │
│  │  • Video ID: abc123...  [Progress Bar] 67%          │     │
│  │  • Video ID: def456...  [Progress Bar] 34%          │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Section: Header

### Layout
```
Height: 64px
Background: --card
Border-bottom: 1px solid --border
Padding: 0 32px (desktop), 0 16px (mobile)
Position: sticky, top: 0
Z-index: 20

Structure:
[Logo - 32px] [Nav Links] ────────── [+ New Button] [Avatar]

Logo: 
  Click → Dashboard
  Image + wordmark
  
Nav Links:
  Dashboard (active)
  Library
  Settings
  
New Button:
  Primary button
  Icon + "New" text
  Opens quick action menu
  
Avatar:
  40px circle
  Click → dropdown menu
  (Profile, Settings, Logout)
```

### Mobile (<768px)
```
[☰ Menu] [Logo] ────────────────── [+ Icon] [Avatar]

Hamburger menu opens sidebar overlay
```

---

## Section: Page Title

```
Padding: 32px (desktop), 24px (mobile)
Border-bottom: 1px solid --border

Layout: Flex, space-between, align-center

Left: 
  "Dashboard" (h1, 36px)
  
Right:
  [+ New Video] button (primary, large)
```

---

## Section: Quick Actions

```
Margin: 32px (padding of container)
Display: Grid, 2 columns on desktop, 1 on mobile
Gap: 24px

Card style:
  Border: 2px solid --border
  Border-radius: --radius-lg
  Padding: 32px
  Background: gradient (subtle)
  Hover: lift shadow, scale 1.02
  Cursor: pointer
  Transition: 200ms ease
  
Structure (each card):
  [Icon - 48px, colored]
  Title (h3, 24px)
  Description (body-sm, --muted-foreground)
  Arrow icon (bottom-right)

Action 1 - Process Video:
  Icon: Video (primary blue)
  Title: "Process Video"
  Description: "Transform a YouTube video into social media content"
  Click → Navigate to /video-input
  
Action 2 - Bulk Processing:
  Icon: Layers (carousel pink)
  Title: "Bulk Processing"
  Description: "Process multiple videos at once"
  Click → Navigate to /bulk-processing
```

### Mobile
- Stack vertically
- Slightly smaller padding (24px)
- Icon size: 40px

---

## Section: Stats Overview

```
Margin: 32px
Display: Grid, 4 columns (desktop), 2 columns (mobile)
Gap: 16px

Stat Card:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-md
  Padding: 24px
  Text-align: center
  
Structure:
  Number (display-md, 48px, --foreground, bold)
  Label (body-sm, --muted-foreground)
  Optional icon above number (subtle)
  Optional trend indicator (↑ +12%)
  
Stats:
  1. Videos Processed
  2. Reels Generated
  3. Tweets Generated  
  4. Total Content Pieces (or Views/Engagement if available)
```

### Interactions
- Hover: Subtle shadow
- Optional: Click to filter content library by type

---

## Section: Recent Content

```
Margin: 32px
Background: --card
Border: 1px solid --border
Border-radius: --radius-lg
Padding: 24px

Header:
  "Recent Content" (h3, 24px)
  "View All →" link (body, --primary)
  Flex, space-between
  Margin-bottom: 20px

Grid:
  4 columns (desktop xl), 3 (desktop), 2 (tablet), 1 (mobile)
  Gap: 16px
  
Content Card (compact):
  ┌─────────────────┐
  │  [Thumbnail]    │ ← 16:9, rounded-top
  ├─────────────────┤
  │ [Type] [Status] │ ← Badges
  │                 │
  │ Title (line-2)  │ ← h6, 16px, semibold
  │ Video ID        │ ← caption, mono, muted
  │                 │
  │ [Edit] [Copy]   │ ← Small ghost buttons
  └─────────────────┘
  
Thumbnail:
  Aspect: 16:9
  Border-radius: --radius-md --radius-md 0 0
  Object-fit: cover
  Default: Gradient placeholder with icon
  
Type Badge:
  "Reel" / "Carousel" / "Tweet"
  Content-type accent color
  Small size
  
Status Badge:
  "Ready" (green) / "Processing" (amber) / "Error" (red)
  
Actions:
  Edit button → Open content editor
  Copy button → Copy content to clipboard + toast
```

### Empty State
```
Text-align: center
Padding: 64px
Icon: 64px (video + sparkles)
Title: "No content yet"
Description: "Process your first video to get started"
Button: "Process Video" (primary)
```

### Loading State
```
Show 4 skeleton cards
Pulsing animation
Maintain layout
```

---

## Section: Processing Queue

**Only visible when videos are processing**

```
Margin: 32px
Background: --warning-subtle
Border: 1px solid --warning/20
Border-radius: --radius-lg
Padding: 20px

Header:
  Icon: Refresh (spinning)
  "Processing Queue" (h6, 18px)
  
List item:
  Flex, align-center
  Gap: 16px
  Padding: 12px 0
  Border-bottom: 1px solid --border (except last)
  
  Structure:
  [Video icon] Video ID • abc123... [Progress] 67% [Cancel ×]
  
  Progress bar:
    Height: 8px
    Width: 200px
    Background: --muted
    Fill: --primary
    Rounded
    
  Cancel button:
    Ghost, small
    Icon only (×)
    Hover: --destructive
```

### States
- **Processing**: Animated progress bar
- **Complete**: Green checkmark, auto-remove after 3s
- **Error**: Red icon, stays visible, click for details

---

## Responsive Breakpoints

### Desktop (≥1280px)
- Full layout as designed
- 4-column recent content grid
- Stats in single row

### Tablet (768px - 1279px)
- 3-column recent content
- Stats in single row (might wrap)
- Reduce paddings to 24px

### Mobile (<768px)
- Single column everything
- Quick actions stack
- Stats in 2×2 grid
- Recent content 1-2 columns
- Smaller typography
- Hamburger navigation

---

## User Interactions

### Page Load
1. Fetch dashboard data (stats, recent content, processing queue)
2. Show skeleton loaders during fetch
3. Populate sections with data
4. Poll for processing queue updates (every 5s)

### Quick Action Click
1. Click "Process Video"
   → Navigate to /video-input
2. Click "Bulk Processing"
   → Navigate to /bulk-processing

### Recent Content Interactions
1. Click card → Navigate to content detail/editor
2. Click "Edit" → Open editor modal or page
3. Click "Copy" → Copy to clipboard + success toast
4. Click "View All" → Navigate to /library

### Processing Queue
1. Watch progress update in real-time
2. Click "Cancel" → Confirm modal → Cancel processing
3. Auto-refresh when complete → New item in Recent Content

### Header Interactions
1. Click "+ New" → Dropdown menu:
   - Process Video
   - Bulk Processing
   - (Quick action shortcuts)
2. Click Avatar → Dropdown:
   - Profile
   - Settings
   - Logout

---

## Data Requirements

### API Calls on Load
```
GET /dashboard/stats
Response: {
  videos_processed: number
  reels_generated: number
  tweets_generated: number
  carousels_generated: number
  total_content: number
}

GET /content/recent?limit=8
Response: {
  content_pieces: ContentPiece[]
}

GET /processing/queue (if any processing)
Response: {
  queue: ProcessingItem[]
}
```

### WebSocket (Optional)
- Real-time updates for processing queue
- Live stats updates
- New content notifications

---

## Edge Cases

### No Content Yet
- Show empty state in Recent Content
- Stats show 0 with encouragement message
- Emphasize quick action cards

### Processing Queue Full
- Show message "Queue is full, please wait"
- Disable "Process Video" buttons
- Show estimated wait time

### API Error
- Show error toast
- Retry button
- Fallback to cached data if available

### Long Video Titles
- Truncate with ellipsis (2 lines max)
- Show full title on hover (tooltip)

---

## Performance Considerations

- Lazy load thumbnail images
- Virtualize long lists if needed
- Cache dashboard data (5 min)
- Prefetch common routes (library, settings)
- Optimize polling (exponential backoff if no changes)

---

## Accessibility

- Skip to main content link
- Keyboard navigation (Tab, Enter)
- Screen reader labels for stats
- ARIA live region for processing updates
- Focus management on navigation
- Color + icon + text for status (not color alone)
