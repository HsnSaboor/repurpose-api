# Spacing & Layout System

## Philosophy
Consistent, predictable spacing creates visual rhythm and hierarchy. Base-8 system for mathematical harmony and easy implementation.

## Spacing Scale (Base-8)

```
0:    0px      (0rem)      # No space
1:    4px      (0.25rem)   # Hairline
2:    8px      (0.5rem)    # Tight
3:    12px     (0.75rem)   # Compact
4:    16px     (1rem)      # Default
5:    20px     (1.25rem)   # Comfortable
6:    24px     (1.5rem)    # Relaxed
8:    32px     (2rem)      # Loose
10:   40px     (2.5rem)    # Extra loose
12:   48px     (3rem)      # Spacious
16:   64px     (4rem)      # Very spacious
20:   80px     (5rem)      # Section break
24:   96px     (6rem)      # Major section
```

## Component Internal Spacing

### Buttons
```
Small:
  padding: 2 (8px) vertical, 3 (12px) horizontal
  gap: 2 (8px) between icon & text

Default:
  padding: 2.5 (10px) vertical, 4 (16px) horizontal
  gap: 2 (8px) between icon & text

Large:
  padding: 3 (12px) vertical, 6 (24px) horizontal
  gap: 3 (12px) between icon & text
```

### Input Fields
```
Small:
  padding: 2 (8px) vertical, 3 (12px) horizontal
  height: 32px

Default:
  padding: 2.5 (10px) vertical, 4 (16px) horizontal
  height: 40px

Large:
  padding: 3 (12px) vertical, 4 (16px) horizontal
  height: 48px
```

### Cards
```
Compact:
  padding: 4 (16px)
  gap: 3 (12px) between elements

Default:
  padding: 6 (24px)
  gap: 4 (16px) between elements

Spacious:
  padding: 8 (32px)
  gap: 6 (24px) between elements
```

### Modals/Dialogs
```
padding: 6 (24px)
header margin-bottom: 4 (16px)
footer margin-top: 6 (24px)
button gap: 3 (12px)
```

## Layout Spacing

### Page Margins
```
Mobile (< 640px):
  padding: 4 (16px)

Tablet (640px - 1024px):
  padding: 6 (24px)

Desktop (> 1024px):
  padding: 8 (32px) or 10 (40px)
```

### Content Sections
```
Between major sections: 12 (48px) or 16 (64px)
Between subsections: 8 (32px) or 10 (40px)
Between related elements: 6 (24px)
Between list items: 4 (16px)
```

### Grid Gaps
```
Card grids:
  mobile: 4 (16px)
  tablet: 6 (24px)
  desktop: 6 (24px) or 8 (32px)

List items: 3 (12px) or 4 (16px)
Form fields: 4 (16px) or 5 (20px)
```

## Container Widths

```
max-width-sm:   640px   # Forms, narrow content
max-width-md:   768px   # Article content
max-width-lg:   1024px  # Standard content
max-width-xl:   1280px  # Wide layouts
max-width-2xl:  1536px  # Very wide (rare)

Container padding: 4 (16px) mobile, 6 (24px) desktop
```

## Aspect Ratios

```
Video thumbnails: 16:9
Square images: 1:1
Portrait cards: 4:5 or 3:4
Wide cards: 21:9 or 3:1
```

## Border Radius

```
--radius-sm:   4px   (0.25rem)   # Small elements, badges
--radius:      8px   (0.5rem)    # Default, buttons, inputs
--radius-md:   12px  (0.75rem)   # Cards, modals
--radius-lg:   16px  (1rem)      # Large cards, images
--radius-xl:   24px  (1.5rem)    # Hero sections
--radius-full: 9999px            # Pills, avatars
```

### Border Radius Application
- Buttons: `--radius`
- Input fields: `--radius`
- Cards: `--radius-md`
- Badges: `--radius-sm` or `--radius-full`
- Avatars: `--radius-full`
- Images: `--radius-md` or `--radius-lg`
- Modals: `--radius-lg`

## Borders & Outlines

```
Border widths:
  default: 1px
  thick: 2px
  focus: 2px (ring)

Border styles:
  solid: Default for most components
  dashed: For drag-drop zones, placeholders
  none: Borderless variants
```

### Border Application
```
Cards: 1px solid --border
Inputs: 1px solid --input
Dividers: 1px solid --border
Focus ring: 2px solid --ring (with offset)
Selected state: 2px solid --primary
```

## Focus & Interaction States

```
Focus ring:
  width: 2px
  offset: 2px
  color: --ring
  opacity: 1

Hover transform:
  scale: 1.02 (subtle)
  transition: 150ms ease

Active/Press:
  scale: 0.98
  transition: 100ms ease
```

## Z-Index Scale

```
z-0:    0       # Base layer
z-10:   10      # Dropdowns, tooltips
z-20:   20      # Sticky headers
z-30:   30      # Modals, dialogs
z-40:   40      # Popovers over modals
z-50:   50      # Toast notifications
z-max:  9999    # Critical overlays
```

## Responsive Breakpoints

```
sm:  640px    # Mobile landscape, small tablets
md:  768px    # Tablets
lg:  1024px   # Desktop
xl:  1280px   # Large desktop
2xl: 1536px   # Extra large
```

### Responsive Strategy
- Mobile-first approach
- Stack vertically on mobile
- Grid layouts on tablet+
- Increase spacing on larger screens

## Layout Patterns

### Sidebar + Main
```
Sidebar width: 256px (fixed) or 20% (responsive)
Main content: flex-1
Gap: 6 (24px) or 8 (32px)
Mobile: Stack vertically
```

### Dashboard Grid
```
Columns: 1 (mobile) / 2 (tablet) / 3-4 (desktop)
Gap: 4-6 (16-24px)
Min card width: 280px
```

### Form Layout
```
Single column: max-width-sm (640px)
Two column: Only on lg+ screens
Field spacing: 4-5 (16-20px)
Label to input: 2 (8px)
```

### Content Cards
```
Padding: 6 (24px)
Image to content: 4 (16px)
Title to description: 2 (8px)
Content to actions: 4-6 (16-24px)
```

## Spacing Guidelines

### Do's
✓ Use scale values only (avoid arbitrary spacing)
✓ Increase spacing on larger screens
✓ Use larger spacing between unrelated elements
✓ Use consistent spacing for same-level elements
✓ Group related content with smaller gaps

### Don'ts
✗ Don't use spacing outside the scale
✗ Don't use equal spacing everywhere
✗ Don't cram content (breathing room is good)
✗ Don't use too many different spacing values
✗ Don't ignore responsive spacing adjustments

## Touch Targets

```
Minimum touch target: 44x44px (mobile)
Comfortable touch: 48x48px
Desktop clickable: 32x32px minimum
Icon buttons: 40x40px (mobile), 36x36px (desktop)
```

## Whitespace Usage

### Generous Whitespace
- Around hero sections
- Between major sections
- Around featured content
- In empty states

### Moderate Whitespace
- Between cards in grids
- Between form sections
- Around modals

### Compact Whitespace
- Within dense data tables
- In dropdown menus
- Between related list items
- Inside compact cards
