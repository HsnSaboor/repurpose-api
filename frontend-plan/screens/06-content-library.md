# Content Library Screen

## Overview
Central repository for all generated content. Advanced filtering, search, sorting, and bulk actions. Power-user features with clean interface.

---

## Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│ [Top Nav]                                                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Content Library                    [+ New Video] │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  [🔍 Search]  [Filters ▼]  [Sort ▼]  [View: Grid] │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Active Filters: × Reels  × This Week  [Clear]    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  234 content pieces                                │     │
│  │                                                     │     │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐          │     │
│  │  │Card 1│  │Card 2│  │Card 3│  │Card 4│          │     │
│  │  └──────┘  └──────┘  └──────┘  └──────┘          │     │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐          │     │
│  │  │Card 5│  │Card 6│  │Card 7│  │Card 8│          │     │
│  │  └──────┘  └──────┘  └──────┘  └──────┘          │     │
│  │                                                     │     │
│  │  [Load More] or [Pagination]                       │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Section: Page Header

```
Padding: 32px
Border-bottom: 1px solid --border

Layout: Flex, space-between, align-center

Left:
  "Content Library" (h1, 36px)
  Subtitle: "All your generated content" 
  (body, --muted-foreground)
  
Right:
  [+ New Video] button (primary, large)
  Icon: Plus
  Click → Navigate to /video-input
  
Mobile:
  Stack vertically
  Center align
```

---

## Section: Toolbar

```
Background: --card
Border: 1px solid --border
Border-radius: --radius-lg
Padding: 16px 20px
Margin: 32px
Display: Flex
Gap: 12px
Align: center
Flex-wrap: wrap

Components (left to right):

1. Search Input
   Width: 320px (flex-grow on mobile)
   Placeholder: "Search content..."
   Icon: Search (left)
   Clear icon (right, when has value)
   
   Searches:
   - Content titles
   - Captions
   - Video titles
   - Content IDs
   
   Debounced input (300ms)

2. Filters Dropdown
   Button: Secondary
   Text: "Filters"
   Icon: Filter
   Badge: Active filter count (if any)
   
   Click → Open filter panel

3. Sort Dropdown
   Button: Secondary  
   Text: "Sort: Recent" (shows current)
   Icon: Arrow up/down
   
   Options:
   - Recent (default)
   - Oldest
   - Title A-Z
   - Title Z-A
   - Content Type
   - Video

4. View Toggle
   Button group: [Grid] [List]
   Icons: Grid / List
   Active state highlighted
   
5. Bulk Actions (when items selected)
   Appears dynamically
   [X selected] [Export] [Delete] [Deselect All]

Mobile: Stack or horizontal scroll
```

---

## Filter Panel (Dropdown/Sidebar)

```
Opens below toolbar or as sidebar (desktop)
Background: --popover
Border: 1px solid --border
Border-radius: --radius-lg
Shadow: --shadow-lg
Padding: 20px
Width: 320px (desktop)

Structure:
┌─────────────────────────────────┐
│ Filters            [Clear All]  │
├─────────────────────────────────┤
│                                 │
│ Content Type                    │
│ ☑ Reels (45)                    │
│ ☑ Carousels (32)                │
│ ☑ Tweets (18)                   │
│                                 │
│ ──────────                      │
│                                 │
│ Date Range                      │
│ ⚪ All Time                     │
│ ⚪ Today                        │
│ ⚪ This Week                    │
│ ⚪ This Month                   │
│ ⚪ Custom Range                 │
│                                 │
│ ──────────                      │
│                                 │
│ Video                           │
│ [Search videos...  ▼]           │
│                                 │
│ ──────────                      │
│                                 │
│ Status                          │
│ ☑ Published                     │
│ ☑ Draft                         │
│ ☐ Archived                      │
│                                 │
│ ──────────                      │
│                                 │
│ [Apply Filters]                 │
│                                 │
└─────────────────────────────────┘

Sections:
  Each section collapsible
  Checkbox groups
  Radio button groups
  Counts next to options
  
Actions:
  "Clear All" - Reset all filters
  "Apply Filters" - Primary button
  Auto-apply (optional, no button needed)
```

---

## Active Filters Bar

**Only visible when filters active**

```
Background: --primary/5
Border: 1px solid --primary/20
Border-radius: --radius
Padding: 12px 20px
Margin: 0 32px 16px
Display: Flex
Gap: 8px
Align: center
Flex-wrap: wrap

Text: "Active Filters:" (body-sm, semibold)

Filter chips:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-full
  Padding: 6px 12px
  Font: caption
  
  Structure: [Text] [× Icon]
  
  Hover:
    Border: --destructive
    × icon: --destructive
    
  Click × → Remove filter
  
[Clear All] button (ghost, small)
  Click → Remove all filters
```

---

## Content Grid View

```
Display: Grid
Columns: 4 (xl), 3 (lg), 2 (md), 1 (sm)
Gap: 20px
Padding: 32px

Content card structure:
┌─────────────────────────────┐
│ [☐]    [Type Badge] [Menu]  │ ← Selection + actions
├─────────────────────────────┤
│                             │
│    [Thumbnail/Preview]      │ ← Visual preview
│                             │
├─────────────────────────────┤
│ Title (h6, line-clamp 2)    │
│                             │
│ Video: Title (body-sm)      │ ← Linked to video
│ ID: abc_001 (caption)       │
│ Date: 2 days ago            │
│                             │
├─────────────────────────────┤
│ [Copy] [Edit] [Preview]     │ ← Quick actions
└─────────────────────────────┘

Card:
  Background: --card
  Border: 1px solid --border
  Border-radius: --radius-lg
  Padding: 0
  Overflow: hidden
  Transition: 200ms
  
  Hover:
    Border: --border-strong
    Shadow: --shadow-md
    Transform: translateY(-4px)
    
  Selected:
    Border: 2px solid --primary
    Background: --primary/5
```

### Card Components

**Selection Checkbox**
```
Position: Absolute, top-left
Padding: 12px
Size: 20px
Z-index: 1
Background: Semi-transparent on hover
```

**Type Badge**
```
Position: Absolute, top
Center or left (after checkbox)
Same as before (Reel/Carousel/Tweet)
```

**Menu Button**
```
Position: Absolute, top-right
Icon: Three dots vertical
Size: 32px
Ghost button

Click → Dropdown:
  - Edit
  - Copy
  - Preview  
  - Export
  - Delete
  - Archive
```

**Thumbnail Area**
```
Aspect depends on type:
  Reel: 9:16 (vertical)
  Carousel: 1:1 (square)
  Tweet: 16:9 or text preview
  
Max-height: 240px
Object-fit: cover
Background: Gradient placeholder if no image
Cursor: pointer (opens preview)
```

**Metadata Section**
```
Padding: 16px

Title:
  Font: h6 (16px, semibold)
  Line-clamp: 2
  Margin-bottom: 8px
  
Video link:
  Font: body-sm
  Color: --muted-foreground
  Hover: --primary (underline)
  Click → Filter by this video
  
Content ID:
  Font: caption, monospace
  Color: --muted-foreground
  Copy on click
  
Date:
  Font: caption
  Color: --muted-foreground
  Relative time (2 days ago)
```

**Actions Bar**
```
Padding: 12px 16px
Border-top: 1px solid --border
Display: Flex
Gap: 8px

Buttons: Small, ghost
Icons + text (desktop) or icons only (mobile)

[Copy] - Copy icon
[Edit] - Pencil icon
[Preview] - Eye icon

All have hover states and tooltips
```

---

## Content List View

**Alternative to grid**

```
Table or list layout:
┌─────────────────────────────────────────────────────────┐
│ ☐  [Thumb] Title          Video    Type    Date  [...]  │
│ ☐  [Thumb] Title          Video    Type    Date  [...]  │
│ ☐  [Thumb] Title          Video    Type    Date  [...]  │
└─────────────────────────────────────────────────────────┘

Columns:
- [☐] Selection (40px)
- [Thumbnail] Small (60px)
- Title (flex-grow)
- Video (200px)
- Type (100px, badge)
- Date (120px)
- [Actions] Menu (40px)

Rows:
  Padding: 12px 16px
  Border-bottom: 1px solid --border
  Hover: --muted background
  
  Click row → Navigate to content detail
  Click checkbox → Toggle selection
  Click actions → Open menu

More compact than grid
Better for scanning large lists
Shows more info at glance
```

---

## Bulk Selection Mode

**When one or more items selected:**

```
Toolbar changes:
┌────────────────────────────────────────┐
│ ✓ 5 selected  [Export] [Delete] [×]   │
└────────────────────────────────────────┘

Appears at top (sticky)
Background: --primary/10
Border: --primary

Actions:
  [Export] → Export selected items
  [Delete] → Delete with confirmation
  [×] Deselect all

Selected cards:
  Highlighted border (--primary)
  Slightly different background
  
Select all checkbox:
  Appears in toolbar
  "Select all X items"
```

---

## Pagination / Infinite Scroll

### Option 1: Pagination
```
Bottom of grid:
Display: Flex, justify-center
Gap: 8px
Margin: 32px

[< Previous] [1] [2] [3] ... [10] [Next >]

Buttons: 40x40px
Numbers: Current highlighted (--primary bg)
Disabled: Previous/Next if at boundary

Page size selector:
  "Show: [24▼] per page"
  Options: 12, 24, 48, 96
```

### Option 2: Infinite Scroll
```
Load more automatically as user scrolls
Show loading spinner at bottom
"Loading more content..."
Smooth, no page jumps

When all loaded:
  "You've reached the end"
  "Showing all X items"
```

---

## Empty State

```
Center of content area
Padding: 64px

Icon: Empty box or video (64px, --muted-foreground)
Title: "No content found" (h3)
Description: Varies by context:
  - "No content generated yet. Process a video to get started."
  - "No results match your filters. Try adjusting your search."
  
Actions:
  [Process Video] button (primary) - if truly empty
  [Clear Filters] button (secondary) - if filtered
  
Illustration: Optional friendly graphic
```

---

## Loading State

```
Show skeleton grid
Match grid column count
Pulsing animation
Preserve layout
Maintain spacing

Skeleton card:
  Gray boxes for thumbnail, text, buttons
  No borders or shadows
  Subtle pulse animation
```

---

## Responsive Behavior

### Desktop (≥1280px)
- 4-column grid
- Full toolbar
- Sidebar filters

### Tablet (768px - 1279px)
- 2-3 column grid
- Toolbar stacks if needed
- Drawer filters

### Mobile (<768px)
- Single column or 2 columns
- Compact cards
- Bottom sheet filters
- Floating action button for new video
- Swipe actions on cards (optional)

---

## User Interactions

### Search
1. Type in search input (debounced)
2. API call with query
3. Update results
4. Highlight matching text (optional)
5. Show "No results" if empty

### Filter
1. Click "Filters"
2. Select filter options
3. Click "Apply" or auto-apply
4. Update results
5. Show active filter chips
6. Update count

### Sort
1. Click sort dropdown
2. Select option
3. Re-fetch with sort param
4. Update display
5. Remember preference

### Card Actions
1. **Click card** → Navigate to detail/preview
2. **Click Copy** → Copy to clipboard + toast
3. **Click Edit** → Navigate to editor
4. **Click Preview** → Open preview modal
5. **Click checkbox** → Toggle selection
6. **Click video link** → Filter by video

### Bulk Actions
1. Select multiple items
2. Click "Export" → Export modal → Download
3. Click "Delete" → Confirm modal → Delete

---

## Data Requirements

```javascript
// Get content list
GET /content/list
Query params:
  ?page=1
  &per_page=24
  &search=query
  &content_type=reel,carousel
  &date_from=YYYY-MM-DD
  &date_to=YYYY-MM-DD
  &video_id=abc123
  &sort_by=created_at
  &sort_order=desc
  
Response: {
  content_pieces: ContentPiece[]
  total_count: number
  page: number
  per_page: number
  total_pages: number
}

// Bulk delete
DELETE /content/bulk
Body: {
  content_ids: string[]
}

// Bulk export
POST /content/export/bulk
Body: {
  content_ids: string[]
  format: "json" | "csv"
}
```

---

## Performance Optimizations

- Virtual scrolling for large lists
- Image lazy loading
- Debounced search
- Cached filter counts
- Pagination/infinite scroll
- Skeleton loading
- Optimistic UI updates

---

## Accessibility

- Keyboard navigation
- Focus management
- ARIA labels for actions
- Screen reader announcements
- High contrast mode support
- Skip to content
- Bulk action keyboard shortcuts
  - Cmd/Ctrl+A: Select all
  - Delete key: Delete selected
  - Cmd/Ctrl+E: Export selected
