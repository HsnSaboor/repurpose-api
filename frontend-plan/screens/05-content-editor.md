# Content Editor Screen

## Overview
Dedicated editing interface for individual content pieces. Supports natural language editing prompts and manual field editing. Real-time preview and AI-assisted refinement.

---

## Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│ [Top Nav]                                                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Edit Content               [Save] [Cancel]        │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌──────────────┬───────────────────────────────────────┐   │
│  │              │                                       │   │
│  │   PREVIEW    │         EDITING PANEL                 │   │
│  │   (Left)     │         (Right)                       │   │
│  │              │                                       │   │
│  │  [Visual     │  Tabs: [AI Edit] [Manual Edit]       │   │
│  │   Preview    │                                       │   │
│  │   of         │  ┌─────────────────────────────────┐ │   │
│  │   Content]   │  │ AI Editing Panel                │ │   │
│  │              │  │                                 │ │   │
│  │              │  │ "Make it more engaging..."      │ │   │
│  │              │  │ [___________________________]   │ │   │
│  │              │  │                                 │ │   │
│  │              │  │ [Apply Edit]                    │ │   │
│  │              │  │                                 │ │   │
│  │              │  │ Quick Prompts:                  │ │   │
│  │              │  │ • Make it more professional     │ │   │
│  │              │  │ • Add emojis                    │ │   │
│  │              │  │ • Shorten text                  │ │   │
│  │              │  └─────────────────────────────────┘ │   │
│  │              │                                       │   │
│  │  [Status]    │  OR                                   │   │
│  │              │                                       │   │
│  │              │  ┌─────────────────────────────────┐ │   │
│  │              │  │ Manual Editing Panel            │ │   │
│  │              │  │                                 │ │   │
│  │              │  │ Title                           │ │   │
│  │              │  │ [___________________________]   │ │   │
│  │              │  │                                 │ │   │
│  │              │  │ Hook                            │ │   │
│  │              │  │ [___________________________]   │ │   │
│  │              │  │                                 │ │   │
│  │              │  │ Caption                         │ │   │
│  │              │  │ [___________________________    │ │   │
│  │              │  │  ___________________________]   │ │   │
│  │              │  │                                 │ │   │
│  │              │  └─────────────────────────────────┘ │   │
│  └──────────────┴───────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Section: Header Bar

```
Height: 64px
Background: --card
Border-bottom: 1px solid --border
Padding: 0 32px
Position: sticky, top: 0
Z-index: 20

Layout: Flex, space-between, align-center

Left:
  "Edit Content" (h2, 24px)
  Content type badge (small)
  Content ID (caption, muted, monospace)
  
Right:
  [Revert] button (ghost, small)
    Tooltip: "Undo all changes"
    Click → Confirm modal → Reset to original
    
  [Cancel] button (secondary)
    Navigates back
    If unsaved: Confirm modal
    
  [Save] button (primary)
    Saves changes
    Disabled if no changes
    Loading state while saving
```

### Mobile
```
Two-line header:
Line 1: [< Back] Title [Save]
Line 2: Badge • ID
```

---

## Layout: Split View (Desktop)

### Left Panel: Preview (40%)

```
Width: 40%
Background: --muted/30
Border-right: 1px solid --border
Padding: 32px
Position: sticky, top: 64px
Height: calc(100vh - 64px)
Overflow: auto

Content varies by type:

For Reel:
  ┌─────────────┐
  │  [Phone     │
  │   Mockup]   │
  │             │
  │  Title      │
  │  Hook text  │
  │  ...        │
  │             │
  │  [Preview   │
  │   Script]   │
  │             │
  │  Caption    │
  └─────────────┘
  
  9:16 aspect ratio container
  Phone frame design (optional)
  Formatted text preview
  Real-time updates as user edits
  
For Carousel:
  ┌─────────────┐
  │  [Slide 1/8]│
  │             │
  │  ┌───────┐  │
  │  │ Image │  │
  │  │ Area  │  │
  │  └───────┘  │
  │             │
  │  Heading    │
  │  Text...    │
  │             │
  │  [< 1/8 >]  │
  └─────────────┘
  
  Square aspect (1:1)
  Navigation between slides
  Pagination dots
  Preview current slide
  
For Tweet:
  ┌─────────────┐
  │ [@user]     │
  │             │
  │ Tweet text  │
  │ ...         │
  │             │
  │ [If thread:]│
  │             │
  │ Tweet 2...  │
  │             │
  │ 1/3 Thread  │
  └─────────────┘
  
  Twitter-like UI
  Character count
  Thread indicator
  
Status Section (bottom):
  • Original vs Current indicator
  • Changes made list
  • Character counts
  • Validation warnings
```

### Right Panel: Editing (60%)

```
Width: 60%
Padding: 32px
Overflow: auto
```

---

## Tabs: AI Edit vs Manual Edit

```
Tab Bar:
  Border-bottom: 2px solid --border
  Padding: 0 32px
  
  [AI Edit] [Manual Edit]
  
  Active tab:
    Color: --primary
    Border-bottom: 2px solid --primary
    Font: medium weight
    
  Inactive:
    Color: --muted-foreground
    Hover: --foreground
```

---

## Tab 1: AI Edit Panel

```
Padding: 32px

Section: Edit Prompt Input
  ┌─────────────────────────────────────────────┐
  │ Tell AI how to improve this content         │
  │                                             │
  │ [Textarea - 3 rows]                         │
  │ "E.g., Make it more engaging, add emojis,   │
  │  make it shorter, change tone to casual..."  │
  │                                             │
  └─────────────────────────────────────────────┘
  
  Textarea:
    Large size
    Border: --input
    Placeholder: Examples shown
    Auto-resize
    Min-height: 80px
    Max-height: 200px
    
  [Apply Edit] button (primary, large)
    Full width or prominent
    Disabled if empty
    Loading: "Applying edit..."
    
  Character counter: Optional

Section: Quick Edit Prompts
  Title: "Quick Edits" (h6, 18px)
  Description: "Click to apply common improvements"
  
  Grid of prompt chips:
    ┌──────────────────┐ ┌──────────────────┐
    │ Make Professional│ │ Add Emojis       │
    └──────────────────┘ └──────────────────┘
    ┌──────────────────┐ ┌──────────────────┐
    │ Shorten Text     │ │ Expand Details   │
    └──────────────────┘ └──────────────────┘
    ┌──────────────────┐ ┌──────────────────┐
    │ More Engaging    │ │ Add Call-to-Act. │
    └──────────────────┘ └──────────────────┘
    
  Chip style:
    Background: --muted
    Border: 1px solid --border
    Border-radius: --radius-full
    Padding: 10px 16px
    Font: body-sm, medium
    
    Hover: --border-strong border
    Active: --primary/10 background, --primary border
    
    Click → Fill prompt textarea with text
    Double-click → Apply immediately

Section: Edit History (collapsible)
  Title: "Edit History" (h6)
  [> Show History] button (ghost)
  
  When expanded:
    List of previous edits:
      • "Made more professional" - 2 min ago [Undo]
      • "Added emojis" - 5 min ago [Undo]
      
    Each item:
      Body-sm text
      Timestamp
      Undo button (ghost, small)
      
    Max 5 items shown, "View all" link

Section: AI Suggestions (optional)
  Card:
    Background: --info-subtle
    Border: --info/20
    Border-radius: --radius-md
    Padding: 16px
    
    Icon: Lightbulb
    "AI Suggestion: Try making the hook more captivating"
    [Apply] button (secondary, small)
```

---

## Tab 2: Manual Edit Panel

```
Padding: 32px

Form layout varies by content type:

For Reel:
  ┌─────────────────────────────────────────────┐
  │ Title                                       │
  │ [_______________________________] 45/100    │
  │                                             │
  │ Hook                                        │
  │ [_______________________________] 78/200    │
  │                                             │
  │ Caption                                     │
  │ [_______________________________            │
  │  _______________________________] 156/300   │
  │                                             │
  │ Script (collapsible)                        │
  │ [> Expand to edit]                          │
  │                                             │
  │ ── Metadata ──                              │
  │ Video ID: abc123                            │
  │ Content ID: abc123_001                      │
  │ Type: Instagram Reel                        │
  │                                             │
  └─────────────────────────────────────────────┘
  
For Carousel:
  ┌─────────────────────────────────────────────┐
  │ Carousel Title                              │
  │ [_______________________________] 45/100    │
  │                                             │
  │ Caption                                     │
  │ [_______________________________] 156/300   │
  │                                             │
  │ ── Slides ──                                │
  │                                             │
  │ Slide 1                          [+ Add]    │
  │   Heading                                   │
  │   [_______________________________]         │
  │   Text                                      │
  │   [_______________________________          │
  │    _______________________________] 345/800 │
  │   [Remove Slide]                            │
  │                                             │
  │ Slide 2                                     │
  │   ...                                       │
  │                                             │
  └─────────────────────────────────────────────┘
  
  Slides:
    Accordion or expandable panels
    Drag-to-reorder handles
    Add/remove slide buttons
    Validation per slide
    
For Tweet:
  ┌─────────────────────────────────────────────┐
  │ Title                                       │
  │ [_______________________________]           │
  │                                             │
  │ Tweet 1                                     │
  │ [_______________________________            │
  │  _______________________________] 245/280   │
  │                                             │
  │ Thread Continuation 1                       │
  │ [_______________________________] 156/280   │
  │                                             │
  │ [+ Add Tweet to Thread]                     │
  │                                             │
  └─────────────────────────────────────────────┘

All inputs:
  Label: label style (14px, medium)
  Input/Textarea: Large size
  Character counter (right side)
  Real-time validation
  Error messages inline
  Helper text where needed
```

### Field Validation

```
Real-time as user types:

Valid:
  Border: default
  Counter: --muted-foreground
  
Approaching limit (90%):
  Counter: --warning
  
Over limit:
  Border: --destructive
  Counter: --destructive
  Error message: "Exceeds X character limit"
  Save button disabled
  
Empty (required):
  Border: --destructive (on blur)
  Error: "This field is required"
```

---

## Editing Interactions

### AI Edit Flow
1. User types prompt OR clicks quick edit
2. Click "Apply Edit"
3. API call with prompt
4. Show loading state (spinner on button)
5. Preview updates in real-time
6. Success → Show "Edit applied!" toast
7. Add to edit history
8. Enable save button

### Manual Edit Flow
1. User modifies any field
2. Preview updates immediately (debounced)
3. Validate on blur
4. Show character counts
5. Enable save button
6. Can switch tabs without losing changes

### Save Flow
1. Click "Save"
2. Validate all fields
3. If valid → API call
4. Show loading (spinner on button)
5. Success → Toast "Changes saved!"
6. Navigate back or stay (user preference)
7. Error → Show error message, stay on page

### Cancel Flow
1. Click "Cancel" or back
2. If no changes → Navigate immediately
3. If unsaved → Confirm modal:
   ```
   Unsaved Changes
   
   You have unsaved changes. Are you sure?
   
   [Don't Save] [Cancel] [Save & Exit]
   ```

---

## Comparison View (Optional Feature)

```
Toggle button in header: "Compare with Original"

When enabled:
  Split preview:
    [Original] | [Current]
    
  Highlight changes:
    Additions: Green background
    Deletions: Red strikethrough
    Modified: Yellow background
    
  Useful for reviewing AI edits
```

---

## Mobile Layout

```
Stack vertically:
1. Header (fixed top)
2. Tabs
3. Content (scrollable)
4. Actions (fixed bottom)

No split view:
  Show preview at top (collapsible)
  Edit form below
  Toggle between preview/edit with button
  
Bottom action bar:
  [Cancel] ──────── [Save]
  Full width buttons
```

---

## Data Requirements

```javascript
// On page load
GET /content/{content_id}
Response: {
  content_piece: ContentPiece
  original_content: ContentPiece (for comparison)
  video_info: {...}
}

// AI Edit
POST /edit-content/
Body: {
  video_id: string
  content_piece_id: string
  edit_prompt: string
  content_type: "reel" | "carousel" | "tweet"
}
Response: {
  edited_content: ContentPiece
  changes_made: string[]
}

// Manual Save
PUT /content/{content_id}
Body: {
  content_piece: ContentPiece
}
Response: {
  success: boolean
  content_piece: ContentPiece
}

// Get edit history (optional)
GET /content/{content_id}/history
Response: {
  edits: EditHistory[]
}
```

---

## Edge Cases

### Long Processing
- AI edit takes >3s → Show progress indicator
- Keep user informed
- Allow cancel

### API Error
- Show error message clearly
- Allow retry
- Don't lose user's work

### Validation Errors
- Highlight all errors
- Scroll to first error
- Block save until resolved

### Concurrent Edits
- If content modified elsewhere → Show warning
- Offer: Reload latest or continue editing
- Prevent data loss

---

## Success Criteria

- User can easily make quick edits with AI
- Manual editing is straightforward
- Preview updates in real-time
- No data loss on errors
- Clear feedback on all actions
- Fast and responsive
- Works well on mobile

---

## Accessibility

- All form fields labeled
- Error messages associated with fields
- Keyboard shortcuts (Cmd/Ctrl+S to save)
- Focus management
- Screen reader announcements
- Character counts announced
- Undo/redo support
