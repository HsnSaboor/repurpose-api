# Component Specifications

## Overview
Detailed specifications for all reusable UI components. Each component follows the design system principles and maintains visual consistency.

---

## Buttons

### Variants

#### Primary Button
```
Background: --primary
Text: --primary-foreground
Padding: 10px 16px (default)
Border-radius: --radius
Font: label (14px, semibold)
Height: 40px

Hover: 
  Background: --primary (lighter 5%)
  Transform: scale(1.02)
  
Active:
  Transform: scale(0.98)
  
Focus:
  Ring: 2px --ring, offset 2px
  
Disabled:
  Opacity: 0.5
  Cursor: not-allowed
```

#### Secondary Button
```
Background: transparent
Text: --foreground
Border: 1px solid --border
Padding: 10px 16px
Border-radius: --radius

Hover:
  Background: --muted
  
States: Same as primary
```

#### Ghost Button
```
Background: transparent
Text: --foreground
No border
Padding: 10px 16px

Hover:
  Background: --muted
```

#### Destructive Button
```
Background: --destructive
Text: --destructive-foreground
Same structure as primary
```

### Sizes
- **Small**: 8px 12px padding, 32px height, 12px text
- **Default**: 10px 16px padding, 40px height, 14px text
- **Large**: 12px 24px padding, 48px height, 16px text

### With Icons
- Icon size: 16px (default), 14px (small), 20px (large)
- Gap between icon and text: 8px
- Icon-only: Square dimensions, centered icon

---

## Input Fields

### Text Input
```
Border: 1px solid --input
Background: --background
Padding: 10px 16px
Border-radius: --radius
Height: 40px
Font: body (16px)

Hover:
  Border: --border-strong
  
Focus:
  Border: --primary
  Ring: 2px --ring, offset 0
  
Error:
  Border: --destructive
  
Disabled:
  Background: --muted
  Cursor: not-allowed
  Opacity: 0.7
```

### Label
```
Font: label (14px, medium)
Color: --foreground
Margin-bottom: 8px
Display required indicator if needed
```

### Helper Text
```
Font: body-sm (14px)
Color: --muted-foreground
Margin-top: 6px
```

### Error Message
```
Font: body-sm (14px)
Color: --destructive
Margin-top: 6px
Icon: Alert circle before text
```

### Textarea
Same as input but:
- Min-height: 120px
- Resize: vertical
- Padding: 12px 16px

### Select Dropdown
```
Same as input
Plus chevron-down icon (right side)
Padding-right: 40px (for icon)

Dropdown panel:
  Background: --popover
  Border: 1px solid --border
  Border-radius: --radius-md
  Shadow: --shadow-lg
  Max-height: 300px
  Overflow: auto
  
Option:
  Padding: 10px 12px
  Hover: --muted background
  Selected: --primary/10 background
  Font: body-sm
```

---

## Cards

### Base Card
```
Background: --card
Border: 1px solid --border
Border-radius: --radius-md
Padding: 24px
Shadow: none (or --shadow-sm on hover)

Hover (if clickable):
  Border: --border-strong
  Shadow: --shadow-md
  Transform: translateY(-2px)
  
Transition: 200ms ease
```

### Content Card
```
Structure:
┌─────────────────────────────┐
│ [Thumbnail]                 │ ← 16:9 aspect, rounded-top
├─────────────────────────────┤
│ [Type Badge]  [Status]      │ ← 12px padding
│                             │
│ Title (h3)                  │ ← 24px padding
│ Description (body-sm)       │ ← Line clamp 2-3
│                             │
│ Metadata row                │ ← Flex, gray text
├─────────────────────────────┤
│ [Action buttons]            │ ← 16px padding, border-top
└─────────────────────────────┘

Type Badge:
  Background: content-type color (10% opacity)
  Text: content-type color
  Padding: 4px 8px
  Border-radius: --radius-sm
  Font: caption (12px, semibold, uppercase)
  
Status Badge:
  Background: semantic color subtle
  Text: semantic color
  Same structure as type badge
```

### Stat Card
```
Centered content
Large number (display-md)
Label below (body-sm, muted)
Optional icon at top
Padding: 32px
Min-width: 200px
```

---

## Modals & Dialogs

### Modal Structure
```
Backdrop: rgba(0, 0, 0, 0.5)
Container: --popover background
Border-radius: --radius-lg
Max-width: 600px (default)
Max-height: 90vh
Position: Centered
Shadow: --shadow-lg

Structure:
┌─────────────────────────────┐
│ Title (h3)        [X Close] │ ← 24px padding, border-bottom
├─────────────────────────────┤
│                             │
│ Content                     │ ← 24px padding, scrollable
│                             │
│                             │
├─────────────────────────────┤
│            [Cancel] [Save]  │ ← 24px padding, border-top
└─────────────────────────────┘

Animations:
  Enter: scale(0.95) → scale(1), opacity 0 → 1 (200ms)
  Exit: scale(1) → scale(0.95), opacity 1 → 0 (150ms)
```

### Bottom Sheet (Mobile)
```
Slides up from bottom
Border-radius: --radius-lg (top only)
Max-height: 90vh
Drag handle at top (optional)
Swipe down to close
```

---

## Navigation

### Top Navigation Bar
```
Height: 64px
Background: --card
Border-bottom: 1px solid --border
Padding: 0 24px (desktop), 0 16px (mobile)
Position: Sticky top

Layout:
[Logo] ──── [Nav Links] ──────────── [Profile] [Theme Toggle]

Logo: 32px height
Nav links: body, medium weight, --muted-foreground
Active link: --foreground, underline (2px --primary, offset 8px)
```

### Sidebar Navigation
```
Width: 256px
Background: --card
Border-right: 1px solid --border
Padding: 24px 16px

Nav item:
  Padding: 10px 12px
  Border-radius: --radius
  Gap: 12px between icon and text
  
  Hover: --muted background
  Active: --primary/10 background, --primary text
  
Icon: 20px, --muted-foreground (or --primary if active)
Text: body-sm, medium weight
```

### Breadcrumbs
```
Font: body-sm
Color: --muted-foreground
Separator: / or › (8px margins)
Current: --foreground (no link)

Hover (links):
  Color: --primary
  Underline
```

---

## Badges & Tags

### Badge
```
Padding: 4px 10px
Border-radius: --radius-full
Font: caption (12px, semibold)
Display: inline-flex
Align-items: center
Gap: 4px (if icon)

Variants:
  Default: --muted background, --foreground text
  Success: --success-subtle bg, --success text
  Warning: --warning-subtle bg, --warning text
  Error: --destructive-subtle bg, --destructive text
  Info: --info-subtle bg, --info text
```

### Tag (Removable)
```
Same as badge
Plus close icon (×) on right
Hover close: --destructive color
```

---

## Tables

### Table Structure
```
Border: 1px solid --border
Border-radius: --radius-md

Header:
  Background: --muted
  Text: --muted-foreground
  Font: label (12px, semibold, uppercase)
  Padding: 12px 16px
  Border-bottom: 2px solid --border-strong
  
Row:
  Border-bottom: 1px solid --border
  Padding: 12px 16px
  Hover: --muted background
  
Cell:
  Font: body-sm
  Vertical-align: middle
  
Striped (optional):
  Odd rows: slight --muted tint
```

---

## Toast Notifications

```
Position: Fixed, top-right (desktop) or bottom (mobile)
Width: 360px max
Background: --card
Border: 1px solid --border
Border-radius: --radius-lg
Shadow: --shadow-lg
Padding: 16px
Display: flex
Gap: 12px

Structure:
[Icon] Title
       Description (optional)
                                [X Close]

Icon: 20px, semantic color
Title: label (14px, semibold)
Description: body-sm (14px)

Variants:
  Success: Green left border (3px)
  Error: Red left border
  Warning: Amber left border
  Info: Blue left border

Animation:
  Enter: Slide from right + fade (300ms)
  Exit: Slide to right + fade (200ms)
  Auto-dismiss: 5 seconds (or manual)
```

---

## Loading States

### Spinner
```
Size: 16px (small), 24px (default), 32px (large)
Color: --primary
Animation: 1s linear infinite rotate
Border: 2px, transparent with colored top
Border-radius: full
```

### Progress Bar
```
Height: 8px (or 4px for slim)
Background: --muted
Border-radius: --radius-full

Fill:
  Background: --primary
  Border-radius: --radius-full
  Transition: width 300ms ease
  
With percentage text:
  Font: body-sm, --muted-foreground
  Margin-top: 8px
```

### Skeleton
```
Background: --muted
Border-radius: --radius
Animation: pulse (1.5s ease-in-out infinite)

Gradient animation (optional):
  Linear gradient shimmer effect
  --muted to lighter, sliding
```

---

## Tooltips

```
Background: --foreground (dark)
Text: --background (light)
Padding: 6px 12px
Border-radius: --radius
Font: caption (12px)
Max-width: 200px
Shadow: --shadow-md

Arrow: 6px triangle, same color

Position: Top, bottom, left, or right (auto-adjust)
Delay: 500ms on hover
Animation: Fade + slight movement (150ms)
```

---

## Avatars

```
Border-radius: --radius-full
Sizes: 24px, 32px, 40px, 48px, 64px

With image:
  Object-fit: cover
  
Without image (initials):
  Background: --primary
  Text: --primary-foreground
  Font: label (semibold)
  Centered text
  
Status indicator (optional):
  Small dot at bottom-right
  Green (online), gray (offline), amber (away)
  Border: 2px --card
```

---

## Dividers

### Horizontal
```
Border-top: 1px solid --border
Margin: 24px 0 (default)
Width: 100%

With text:
  Position: relative
  Text centered, body-sm, --muted-foreground
  Background: --background (for overlap)
  Padding: 0 12px
```

### Vertical
```
Border-left: 1px solid --border
Height: 100% (or specific)
Margin: 0 16px
```

---

## Accordions

```
Border: 1px solid --border
Border-radius: --radius-md

Item:
  Border-bottom: 1px solid --border (except last)
  
Trigger:
  Padding: 16px
  Display: flex
  Justify: space-between
  Align: center
  Cursor: pointer
  
  Hover: --muted background
  
Icon: Chevron-down, rotates 180° when open
Title: h6 or label

Content:
  Padding: 0 16px 16px
  Animation: Expand height (200ms ease)
```

---

## Tabs

```
Border-bottom: 2px solid --border

Tab button:
  Padding: 12px 16px
  Font: body, medium weight
  Color: --muted-foreground
  Border-bottom: 2px solid transparent
  Margin-bottom: -2px
  
  Hover: --foreground color
  
  Active:
    Color: --primary
    Border-bottom: 2px solid --primary
    
Tab panel:
  Padding-top: 24px
  Animation: Fade in (200ms)
```

---

## Search Input

```
Same as input base
Plus search icon (left side)
Plus clear icon (right side, when has value)

Padding: 10px 40px 10px 40px
Icon positions: Absolute, 12px from edges

With dropdown results:
  Dropdown: --popover background
  Max-height: 400px
  Border: 1px solid --border
  Border-radius: --radius-md
  Shadow: --shadow-lg
  Margin-top: 4px
  
Result item:
  Padding: 10px 12px
  Hover: --muted background
  Highlight matching text: --primary color, semibold
```

---

## Pagination

```
Display: flex
Gap: 8px
Align: center

Button:
  Width: 40px
  Height: 40px
  Border: 1px solid --border
  Border-radius: --radius
  
  Hover: --muted background
  Active: --primary background, --primary-foreground text
  Disabled: opacity 0.5
  
Ellipsis: --muted-foreground, centered
Previous/Next: Text + icon buttons
```

---

## File Upload

### Drag & Drop Zone
```
Border: 2px dashed --border
Border-radius: --radius-lg
Padding: 48px
Background: --muted/50
Min-height: 200px
Text-align: center

Hover (drag over):
  Border-color: --primary
  Background: --primary/5
  
Icon: Upload, 48px, --muted-foreground
Text: body-sm, --muted-foreground
Button: Secondary button

Structure:
  [Icon]
  Drop files here or [Browse]
  Supported formats: ...
```

---

## Empty State

```
Text-align: center
Padding: 64px 24px
Max-width: 400px
Margin: auto

Icon: 64px, --muted-foreground
Title: h3
Description: body, --muted-foreground
CTA Button: Primary

Optional illustration in place of icon
```

---

## Form Validation

### Success
```
Border: --success
Icon: Checkmark circle, --success
Message: --success color
```

### Error
```
Border: --destructive
Icon: Alert circle, --destructive
Message: --destructive color
Shake animation on submit
```

### Warning
```
Border: --warning
Icon: Alert triangle, --warning
Message: --warning color
```
