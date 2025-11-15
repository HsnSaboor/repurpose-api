# Content Generation Results Screen

## Overview
Displays generated content immediately after processing. Shows all content pieces with ability to preview, edit, copy, or export. This is the "success" destination after video processing.

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [Top Nav]                                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Content Generated ✓         [Process Another →] │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Video Info                                        │     │
│  │  ┌────────┐  Video Title                          │     │
│  │  │[Thumb] │  ID: abc123def                        │     │
│  │  └────────┘  Generated: 8 content pieces          │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Filters & Actions                                 │     │
│  │  [All ▼] [Export All] [Copy All]                  │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Content Grid                                      │     │
│  │                                                    │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐             │     │
│  │  │ Reel #1 │ │ Reel #2 │ │ Reel #3 │             │     │
│  │  │ [Preview│ │ [Preview│ │ [Preview│             │     │
│  │  │  Image] │ │  Image] │ │  Image] │             │     │
│  │  │         │ │         │ │         │             │     │
│  │  │ Title.. │ │ Title.. │ │ Title.. │             │     │
│  │  │ Hook... │ │ Hook... │ │ Hook... │             │     │
│  │  │         │ │         │ │         │             │     │
│  │  │[Edit][📋]│ │[Edit][📋]│ │[Edit][📋]│             │     │
│  │  └─────────┘ └─────────┘ └─────────┘             │     │
│  │                                                    │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐             │     │
│  │  │Carousel │ │Carousel │ │ Tweet   │             │     │
│  │  │   #1    │ │   #2    │ │   #1    │             │     │
│  │  │  ...    │ │  ...    │ │  ...    │             │     │
│  │  └─────────┘ └─────────┘ └─────────┘             │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Section: Success Header

```
Background: --success-subtle
Border: 1px solid --success/20
Border-radius: --radius-lg
Padding: 24px
Margin: 32px

Layout: Flex, space-between, align-center

Left:
  Icon: Checkmark circle (--success, 32px)
  Text: "Content Generated Successfully!" (h2, 30px, --success)
  
Right:
  "Process Another Video" button (secondary)
  Navigates to /video-input
  
Mobile: Stack vertically, center-align
```

---

## Section: Video Summary

```
Card:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-lg
  Padding: 24px
  Margin: 32px

Layout: Flex, gap: 20px

Thumbnail:
  Width: 160px (desktop), 120px (mobile)
  Aspect: 16:9
  Border-radius: --radius-md
  
Info:
  Video Title (h3, 24px, line-clamp 2)
  Video ID: ... (caption, monospace, --muted-foreground)
  Generated: X content pieces (body-sm, --muted-foreground)
  Date: Just now (body-sm, --muted-foreground)
  
  Icons for metadata (subtle)
  
Mobile: Stack vertically
```

---

## Section: Filters & Actions Bar

```
Background: --card
Border: 1px solid --border
Border-radius: --radius-lg
Padding: 16px 24px
Margin: 32px
Display: Flex
Gap: 12px
Align: center
Justify: space-between

Left - Filter Dropdown:
  Label: "Show:"
  Select: 
    Options:
      - All Content (8)
      - Reels (3)
      - Carousels (3)
      - Tweets (2)
    Icon per type
    Count badge
  
Right - Action Buttons:
  [Export All] - Secondary button
    Click → Dropdown menu:
      - Export as JSON
      - Export as CSV
      - Export as Text Files
      
  [Copy All] - Ghost button
    Click → Copy all content to clipboard
    Toast: "All content copied!"
    
Mobile:
  Stack if needed
  Full width buttons
```

---

## Section: Content Grid

```
Display: Grid
Columns: 3 (desktop xl), 2 (desktop/tablet), 1 (mobile)
Gap: 24px
Padding: 32px
```

### Content Card (Base)

```
Background: --card
Border: 2px solid --border
Border-radius: --radius-lg
Padding: 0
Overflow: hidden
Transition: 200ms ease

Hover:
  Border: --border-strong
  Shadow: --shadow-md
  Transform: translateY(-4px)
  
Structure:
  ┌─────────────────────────────┐
  │ [Header: Type Badge]        │ ← Colored bg
  ├─────────────────────────────┤
  │ [Preview Area]              │ ← Type-specific
  │                             │
  ├─────────────────────────────┤
  │ [Content Preview]           │ ← Title, caption, etc.
  │                             │
  ├─────────────────────────────┤
  │ [Actions]                   │ ← Edit, Copy, etc.
  └─────────────────────────────┘
```

---

### Reel Content Card

```
Header:
  Background: --reel-accent/10
  Border-bottom: 1px solid --reel-accent/20
  Padding: 12px 16px
  
  Badge: "Instagram Reel" 
  Font: caption, semibold, uppercase
  Color: --reel-accent
  Icon: Video icon
  
Preview Area:
  Aspect: 9:16 (portrait)
  Max-height: 300px
  Background: Gradient or placeholder
  Position: relative
  
  Overlay (center):
    Play icon (large, semi-transparent)
    Duration badge (if applicable)
    
Content Preview:
  Padding: 16px
  
  Title: (h6, 16px, semibold, line-clamp 2)
  Hook: (body-sm, --muted-foreground, line-clamp 2)
  Caption: (caption, --muted-foreground, line-clamp 3)
  
  Divider between sections (subtle)
  
Actions Bar:
  Padding: 12px 16px
  Border-top: 1px solid --border
  Display: Flex
  Gap: 8px
  
  [Edit] button (secondary, small)
  [Copy] button (ghost, small, icon)
  [Preview] button (ghost, small, icon)
  
  Hover states for each
```

---

### Carousel Content Card

```
Header:
  Background: --carousel-accent/10
  Badge: "Image Carousel"
  Color: --carousel-accent
  Icon: Layers
  
Preview Area:
  Display: Horizontal scroll of slides
  Or: Show first slide with "1/8" indicator
  Aspect: 1:1 (square)
  Max-height: 250px
  
  Slide indicator dots at bottom
  Navigation arrows (< >)
  
Content Preview:
  Title: (h6)
  Caption: (body-sm, line-clamp 2)
  Slides: X slides (caption, --muted-foreground)
  
  Expandable: "View All Slides >"
    Click → Show all slide headings
    
Actions: Same as Reel
```

---

### Tweet Content Card

```
Header:
  Background: --tweet-accent/10
  Badge: "Twitter Thread"
  Color: --tweet-accent
  Icon: Twitter logo
  
Preview Area:
  Background: --background
  Border: 1px solid --border
  Padding: 16px
  Border-radius: --radius
  
  Mock tweet layout:
    [Avatar] Username • @handle • 2m
    Tweet text... (body, 280 char max)
    
    If thread:
      Thread indicator: "1/3" badge
      "Show thread..." link
      
Content Preview:
  Title: (h6, line-clamp 2)
  Text preview: (body-sm, line-clamp 3)
  Thread count: "3 tweets" (caption)
  
Actions: Same as Reel
```

---

## Content Card Interactions

### Hover (Desktop)
- Lift shadow
- Slight scale up
- Show action buttons more prominently

### Click Card
- Navigate to content detail view OR
- Open preview modal

### Click Edit
- Navigate to content editor
- Pass content ID

### Click Copy
- Copy content to clipboard
- Show success toast
- Green checkmark animation on button

### Click Preview
- Open full preview modal
- Show formatted content
- Allow copy from preview

---

## Preview Modal

```
Backdrop: Semi-transparent dark
Max-width: 900px (depends on type)
Max-height: 90vh
Border-radius: --radius-lg
Background: --popover
Shadow: --shadow-lg

Header:
  Padding: 20px 24px
  Border-bottom: 1px solid --border
  
  [Type Badge] Content Title
  [Close X]
  
Body:
  Padding: 24px
  Overflow: auto
  
  For Reel:
    9:16 preview (phone mockup)
    Show title, hook, script, caption
    Formatted nicely
    
  For Carousel:
    Slide-by-slide view
    Navigation between slides
    Pagination dots
    
  For Tweet:
    Thread view (stacked tweets)
    Twitter-like formatting
    
Footer:
  Padding: 16px 24px
  Border-top: 1px solid --border
  
  [Copy Content] [Edit] [Close]
  
Animations:
  Enter: Scale + fade (200ms)
  Exit: Scale + fade (150ms)
```

---

## Export Functionality

### Export Modal

```
When "Export All" clicked:

Modal:
  Title: "Export Content"
  
  Format selection:
    ⚪ JSON (All data)
    ⚪ CSV (Spreadsheet)
    ⚪ Text Files (Individual files)
    ⚪ Markdown (Formatted)
    
  Options:
    ☑ Include metadata
    ☑ Include video info
    ☐ Compress as ZIP
    
  Filename:
    [video_id_content] .ext
    
  [Cancel] [Export]
  
On Export:
  Generate file
  Trigger download
  Success toast
  Close modal
```

---

## Empty State

**If no content generated (error recovery scenario):**

```
Text-align: center
Padding: 64px
Icon: Sad face or alert (64px)
Title: "No Content Generated"
Description: "Something went wrong during generation."
Actions:
  [Try Again] → Re-run generation
  [Go Back] → Return to input
```

---

## Loading State

**While fetching content details:**

```
Show skeleton cards
Maintain grid layout
Pulsing animation
Preserve spacing
```

---

## Responsive Behavior

### Desktop (≥1280px)
- 3-column grid
- Hover interactions prominent
- Side-by-side preview in modal

### Tablet (768px - 1279px)
- 2-column grid
- Maintain all features
- Smaller cards

### Mobile (<768px)
- Single column
- Full width cards
- Bottom sheet instead of modal
- Swipe between slides in carousel
- Tap interactions instead of hover

---

## User Flow Summary

### After Generation Complete
1. Land on this screen
2. See success message
3. Scroll through generated content
4. Preview interesting pieces
5. Edit if needed
6. Copy favorites to clipboard
7. Export all or go to library

### Typical Actions
1. **Quick Copy**: Copy best 2-3 pieces immediately
2. **Review All**: Browse all generated content
3. **Edit & Refine**: Open editor for specific pieces
4. **Export**: Download all for later use
5. **Process More**: Go back to input another video

---

## Data Requirements

```javascript
// On page load (from process result or route param)
GET /content/by-video/{video_id}
Response: {
  video: {
    id: string
    title: string
    thumbnail: string
    generated_at: timestamp
  }
  content_pieces: ContentPiece[]
}

// For edit action
Navigate to /content/edit/{content_id}

// For export
POST /content/export
Body: {
  video_id: string
  format: "json" | "csv" | "txt" | "md"
  options: {...}
}
Response: File download
```

---

## Success Criteria

- User can immediately see all generated content
- Easy to identify content types
- Quick copy functionality
- Smooth navigation to editor
- Clear visual feedback on actions
- Mobile-friendly interactions
- Export options available
- Can process another video easily

---

## Accessibility

- Keyboard navigation through cards
- Focus trap in modals
- Screen reader labels for actions
- Alt text for type icons
- Announce copy success
- ARIA labels for expandable content
- Color + text + icon for content types
