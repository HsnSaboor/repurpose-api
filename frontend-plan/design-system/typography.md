# Typography System

## Philosophy
Clean, readable type system optimized for content-heavy interfaces. Balance between modern aesthetics and functional clarity.

## Font Families

### Primary Font (UI & Body)
```
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```
- Weight range: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- Use for: UI elements, body text, buttons, labels
- Excellent readability at all sizes
- Wide language support

### Monospace Font (Code & IDs)
```
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace
```
- Weight: 400 (Regular), 600 (Semibold)
- Use for: Video IDs, content IDs, code snippets, API responses
- Clear character distinction

### Optional Display Font (Marketing/Landing)
```
font-family: 'Cal Sans', 'Inter', sans-serif
```
- Weight: 600 (Semibold)
- Use sparingly for: Hero headings, marketing pages
- NOT for application UI

## Type Scale

### Display/Hero
```
display-lg: 
  font-size: 3.75rem (60px)
  line-height: 1.1
  letter-spacing: -0.02em
  font-weight: 700
  Usage: Landing page hero

display-md:
  font-size: 3rem (48px)
  line-height: 1.2
  letter-spacing: -0.02em
  font-weight: 700
  Usage: Major section headers
```

### Headings
```
h1:
  font-size: 2.25rem (36px)
  line-height: 1.25
  letter-spacing: -0.01em
  font-weight: 700
  Usage: Page titles

h2:
  font-size: 1.875rem (30px)
  line-height: 1.3
  letter-spacing: -0.01em
  font-weight: 600
  Usage: Major sections

h3:
  font-size: 1.5rem (24px)
  line-height: 1.4
  letter-spacing: -0.01em
  font-weight: 600
  Usage: Card titles, subsections

h4:
  font-size: 1.25rem (20px)
  line-height: 1.4
  letter-spacing: 0
  font-weight: 600
  Usage: Component headers

h5:
  font-size: 1.125rem (18px)
  line-height: 1.5
  letter-spacing: 0
  font-weight: 600
  Usage: Small sections

h6:
  font-size: 1rem (16px)
  line-height: 1.5
  letter-spacing: 0
  font-weight: 600
  Usage: Labels, emphasized text
```

### Body Text
```
body-lg:
  font-size: 1.125rem (18px)
  line-height: 1.6
  font-weight: 400
  Usage: Featured content, introductory text

body:
  font-size: 1rem (16px)
  line-height: 1.6
  font-weight: 400
  Usage: Default body text, content

body-sm:
  font-size: 0.875rem (14px)
  line-height: 1.5
  font-weight: 400
  Usage: Secondary information, metadata
```

### Small & Utility
```
caption:
  font-size: 0.75rem (12px)
  line-height: 1.5
  font-weight: 500
  letter-spacing: 0.02em
  Usage: Image captions, timestamps, footnotes

label:
  font-size: 0.875rem (14px)
  line-height: 1.4
  font-weight: 500
  Usage: Form labels, button text

overline:
  font-size: 0.75rem (12px)
  line-height: 1.5
  font-weight: 600
  letter-spacing: 0.08em
  text-transform: uppercase
  Usage: Section tags, categories
```

### Code/Monospace
```
code-inline:
  font-size: 0.875em (relative)
  font-family: monospace
  padding: 0.125rem 0.25rem
  background: --muted
  border-radius: 0.25rem

code-block:
  font-size: 0.875rem (14px)
  line-height: 1.6
  font-family: monospace
  padding: 1rem
  background: --muted
```

## Text Colors

```
--text-primary: --foreground           # Main text (near black)
--text-secondary: --muted-foreground   # Secondary text (gray)
--text-tertiary: --muted-foreground    # Least prominent text
--text-disabled: opacity 0.4           # Disabled state
--text-link: --primary                 # Interactive links
--text-on-primary: --primary-foreground # Text on colored backgrounds
```

## Usage Guidelines

### Hierarchy
1. One H1 per page (page title)
2. H2 for major sections
3. H3 for card/component titles
4. H4-H6 for nested content
5. Body text follows naturally

### Line Length
- Optimal: 50-75 characters per line
- Max: 90 characters for readability
- Use max-width on text containers

### Text Spacing
```
Paragraph spacing: 1em margin-bottom
Section spacing: 2-3rem margin-bottom
List items: 0.5rem margin-bottom
```

### Weight Application
- **700 (Bold)**: Page titles, important callouts
- **600 (Semibold)**: Section headers, button text
- **500 (Medium)**: Labels, emphasis, navigation
- **400 (Regular)**: Body text, descriptions

### Do's
✓ Use consistent scale throughout application
✓ Maintain 1.5-1.6 line-height for body text
✓ Use negative letter-spacing for large headings
✓ Use relative font sizes (rem) for accessibility
✓ Ensure 4.5:1 contrast for body text
✓ Use 3:1 contrast for large text (18px+)

### Don'ts
✗ Don't use more than 2 font families
✗ Don't use font sizes outside the scale
✗ Don't use all-caps for long text
✗ Don't use italic for emphasis (use weight)
✗ Don't justify body text
✗ Don't use line-height < 1.4 for body text

## Component-Specific Typography

### Buttons
```
Primary: body-sm, font-weight: 500
Large: body, font-weight: 500
Small: caption, font-weight: 500
```

### Form Fields
```
Label: label
Input text: body
Helper text: body-sm (--text-secondary)
Error text: body-sm (--destructive)
```

### Cards
```
Title: h3 or h4
Description: body
Metadata: body-sm (--text-secondary)
```

### Tables
```
Header: label (--text-secondary)
Cell: body-sm
Numeric: code-inline (right-aligned)
```

### Badges & Tags
```
Text: caption or label (uppercase)
Weight: 600 (semibold)
Letter-spacing: 0.05em
```

## Responsive Adjustments

### Mobile (< 640px)
- Reduce heading sizes by 20-25%
- Keep body text at 16px minimum
- Increase line-height slightly (1.65)

### Tablet (640px - 1024px)
- Use standard scale
- Optimize line-length (60-70 chars)

### Desktop (> 1024px)
- Full scale
- Consider slightly larger body (18px) for wide layouts
- Max content width: 1200px
