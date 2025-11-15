# Color System

## Philosophy
Modern, professional palette with excellent contrast and accessibility. Inspired by shadcn/ui with subtle refinements for content creation context.

## Base Colors

### Neutrals (Primary UI Structure)
```
--background: 0 0% 100%           # Pure white - main canvas
--foreground: 222.2 84% 4.9%      # Near black - primary text

--muted: 210 40% 96.1%            # Light gray - subtle backgrounds
--muted-foreground: 215.4 16.3% 46.9%  # Medium gray - secondary text

--card: 0 0% 100%                 # White - card backgrounds
--card-foreground: 222.2 84% 4.9% # Near black - card text

--popover: 0 0% 100%              # White - dropdown/modal backgrounds
--popover-foreground: 222.2 84% 4.9%  # Near black - popover text
```

### Primary Brand Color (Accent & Actions)
```
--primary: 221.2 83.2% 53.3%      # Vibrant blue - primary actions
--primary-foreground: 210 40% 98% # Almost white - text on primary

Primary Shades:
- Light: 217.2 91.2% 59.8%        # Hover state
- Dark: 224.3 76.3% 48%           # Active/pressed state
- Subtle: 214.3 31.8% 91.4%       # Background tints
```

### Semantic Colors

#### Success (Content Generated)
```
--success: 142.1 76.2% 36.3%      # Forest green
--success-foreground: 355.7 100% 97.3%
--success-light: 142.1 70.6% 45.3%
--success-subtle: 143.8 61.2% 92.9%
```

#### Warning (Processing/Attention)
```
--warning: 38 92% 50%             # Amber
--warning-foreground: 48 96% 89%
--warning-light: 45 93% 58%
--warning-subtle: 48 100% 96%
```

#### Error (Failures)
```
--destructive: 0 84.2% 60.2%      # Red
--destructive-foreground: 210 40% 98%
--destructive-light: 0 72% 67%
--destructive-subtle: 0 85.7% 97.3%
```

#### Info (Tips & Guidance)
```
--info: 199 89% 48%               # Cyan blue
--info-foreground: 210 40% 98%
--info-subtle: 204 94% 94%
```

### Content Type Colors (Subtle Differentiation)

```
--reel-accent: 280 65% 60%        # Purple - Instagram Reels
--carousel-accent: 340 75% 55%    # Pink - Image Carousels
--tweet-accent: 203 89% 53%       # Twitter Blue - Tweets
```

## Border & Dividers

```
--border: 214.3 31.8% 91.4%       # Subtle borders
--border-strong: 215 20.2% 65.1%  # More visible dividers
--input: 214.3 31.8% 91.4%        # Input field borders

--ring: 221.2 83.2% 53.3%         # Focus ring (matches primary)
```

## Special Purpose

```
--radius: 0.5rem                  # Default border radius (8px)
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1)
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1)
```

## Dark Mode (Optional)

```
--background: 222.2 84% 4.9%
--foreground: 210 40% 98%

--muted: 217.2 32.6% 17.5%
--muted-foreground: 215 20.2% 65.1%

--card: 222.2 84% 4.9%
--card-foreground: 210 40% 98%

--primary: 217.2 91.2% 59.8%
--primary-foreground: 222.2 47.4% 11.2%
```

## Usage Guidelines

### Do's
✓ Use `--primary` for main CTAs and important actions
✓ Use semantic colors (`--success`, `--warning`, etc.) for status
✓ Use `--muted` for backgrounds that need subtle differentiation
✓ Use `--border` for most dividers and component boundaries
✓ Maintain minimum 4.5:1 contrast ratio for text
✓ Use content-type accent colors sparingly for quick visual identification

### Don'ts
✗ Don't use more than 3 colors prominently on a single screen
✗ Don't use full saturation colors for large areas
✗ Don't use red/green only to convey information (accessibility)
✗ Don't mix semantic colors with non-semantic purposes
✗ Don't override focus ring colors (keep consistent)

## Color Application Examples

### Buttons
- Primary action: `bg-primary text-primary-foreground`
- Secondary action: `bg-muted text-foreground`
- Destructive: `bg-destructive text-destructive-foreground`
- Ghost: `text-foreground hover:bg-muted`

### Cards
- Default: `bg-card border-border`
- Hover: `bg-card border-border-strong`
- Selected: `bg-primary/5 border-primary`

### Status Badges
- Success: `bg-success-subtle text-success border-success/20`
- Processing: `bg-warning-subtle text-warning border-warning/20`
- Error: `bg-destructive-subtle text-destructive border-destructive/20`

### Content Type Tags
- Reel: `bg-reel-accent/10 text-reel-accent border-reel-accent/20`
- Carousel: `bg-carousel-accent/10 text-carousel-accent`
- Tweet: `bg-tweet-accent/10 text-tweet-accent`
