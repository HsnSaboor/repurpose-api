# Design Principles

## Core Philosophy

**Beautiful by Default, Powerful When Needed**

The YouTube Repurposer interface prioritizes clarity and speed while maintaining visual elegance. Every design decision serves the user's goal: transforming videos into social media content efficiently.

## Principles

### 1. Progressive Disclosure
**Hide complexity until needed**

- Default interfaces show only essential options
- Advanced features appear in expandable sections
- Configuration lives in settings, not main flows
- Expert users can access power features quickly

**Examples:**
- Video input starts with just URL field
- Style presets shown as simple dropdown
- Advanced customization behind "Customize" button
- Bulk processing is separate flow

### 2. Immediate Feedback
**User should always know what's happening**

- Show processing status in real-time
- Provide estimated completion times
- Display error messages inline, near source
- Confirm successful actions with subtle indicators

**Examples:**
- Progress bar during video processing
- "Generating..." animation for content creation
- Green checkmark on successful edit
- Toast notification for bulk operations

### 3. Minimal Friction
**Reduce steps, remove obstacles**

- Single-click defaults for common actions
- Smart defaults based on context
- Batch operations where sensible
- Keyboard shortcuts for power users

**Examples:**
- "Process with Default Style" primary button
- Remember last-used style preset
- Quick edit without opening modal
- Cmd/Ctrl+K for quick actions

### 4. Visual Hierarchy
**Important things stand out naturally**

- Size and weight indicate importance
- Color draws attention purposefully
- Spacing creates clear groups
- Layout guides the eye naturally

**Examples:**
- Primary CTA is larger, colored
- Content titles are bold and prominent
- Sections clearly separated
- Action buttons positioned predictably

### 5. Consistency & Familiarity
**Build on learned patterns**

- Common patterns across all screens
- Predictable component behavior
- Familiar UI conventions
- Consistent terminology

**Examples:**
- All cards have same structure
- Buttons behave uniformly
- Icons match industry standards
- Same layout patterns throughout

### 6. Content-First
**Content is the hero, UI supports it**

- Generated content prominently displayed
- UI chrome minimal and subtle
- Whitespace frames content nicely
- Actions contextual to content

**Examples:**
- Large content preview cards
- Subtle toolbar/navigation
- Generous padding around content
- Edit button appears on hover

### 7. Responsive Grace
**Adapt elegantly to any size**

- Mobile-first thinking
- Touch-friendly targets
- Graceful layout transformations
- No loss of functionality

**Examples:**
- Bottom sheet modals on mobile
- Hamburger menu on small screens
- Stackable grid layouts
- Swipe gestures on mobile

### 8. Performance Perception
**Feel fast, even when slow**

- Optimistic UI updates
- Skeleton loading states
- Instant local feedback
- Background processing indicators

**Examples:**
- Show content card immediately with skeleton
- Edit appears to save instantly
- Pagination loads immediately
- Processing happens in background

## Design System Adherence

### Color Usage
- **Primary**: Main CTAs, links, focus states
- **Semantic**: Success, warning, error, info only for those states
- **Neutral**: Everything else (80% of UI)
- **Accent**: Subtle differentiation (content types)

### Typography
- **Hierarchy**: Clear, predictable, no more than 4 levels on screen
- **Readability**: Body text 16px minimum, 1.6 line-height
- **Weight**: Use weight changes for emphasis, not size alone
- **Scale**: Stick to defined scale, no custom sizes

### Spacing
- **Rhythm**: Use 8px base system exclusively
- **Consistency**: Same spacing for same relationships
- **Breathing Room**: Generous whitespace around content
- **Grouping**: Proximity indicates relationships

### Components
- **Reusability**: Build once, use everywhere
- **Variants**: Limited, purposeful variants only
- **Composition**: Combine simple components into complex UIs
- **State**: Clear visual feedback for all states

## Accessibility Standards

### WCAG 2.1 Level AA Compliance
- **Contrast**: 4.5:1 for text, 3:1 for large text
- **Focus**: Visible focus indicators on all interactive elements
- **Labels**: All form fields properly labeled
- **Keyboard**: Full keyboard navigation support
- **Screen Readers**: Semantic HTML, ARIA labels where needed
- **Touch Targets**: Minimum 44x44px on mobile

### Inclusive Design
- Support prefers-reduced-motion
- Provide text alternatives for icons
- Allow zoom up to 200%
- Don't rely on color alone
- Support dark mode

## Interaction Patterns

### Buttons
- Primary action = filled primary button
- Secondary action = outlined or ghost button
- Destructive = red destructive button
- Icon-only = show tooltip on hover

### Forms
- Single column on mobile
- Labels above inputs
- Inline validation
- Clear error messages
- Submit button at bottom

### Modals
- Backdrop darkens page
- ESC key closes
- Click outside closes
- Max width 600px
- Centered on desktop, bottom sheet on mobile

### Cards
- Clickable cards have hover state
- Actions appear on hover (desktop)
- Actions always visible (mobile)
- Status indicators in corner
- Thumbnail at top or left

### Navigation
- Persistent top bar
- Sidebar on desktop (optional)
- Tab bar on mobile
- Breadcrumbs for deep hierarchies
- Clear active state

## Motion & Animation

### Principles
- Purposeful, not decorative
- Fast (150-300ms)
- Easing functions feel natural
- Respects prefers-reduced-motion

### Standard Timings
```
Micro-interactions: 100-150ms (hover, press)
Element transitions: 200-250ms (expand, move)
Page transitions: 300-400ms (route change)
Loading animations: continuous, smooth
```

### Use Cases
- Button hover/press feedback
- Dropdown/modal open/close
- Content expand/collapse
- Loading spinners
- Toast notifications slide in
- Success checkmark animation

## Error Handling

### User-Friendly Errors
- Explain what went wrong
- Suggest how to fix it
- Provide recovery actions
- Don't blame the user

### Error Patterns
- **Validation**: Inline, near field, as user types
- **Form submission**: Summary at top, inline details
- **API errors**: Toast notification + retry button
- **Critical errors**: Full-screen with support contact

### Examples
- "Video ID not found. Please check the URL and try again."
- "Processing failed. [Retry] [Contact Support]"
- "This field is required."
- "API rate limit reached. Try again in 60 seconds."

## Empty States

### Informative & Actionable
- Explain why empty
- Show next action clearly
- Use friendly illustration/icon
- Provide contextual help

### Examples
- "No videos processed yet. Enter a YouTube URL to get started."
- "No content generated. Process a video first."
- "No style presets. Create your first custom style."
- Empty state with large upload icon + CTA button

## Loading States

### Types
1. **Skeleton screens**: Card/content placeholders
2. **Spinners**: Small inline operations
3. **Progress bars**: Long operations with % complete
4. **Pulsing indicators**: Background sync

### Rules
- Show skeleton if content layout known
- Show spinner for unpredictable time
- Show progress bar for >3 second operations
- Never block entire UI unless critical

## Success States

### Celebration, Not Disruption
- Brief, positive confirmation
- Don't interrupt workflow
- Use green checkmarks subtly
- Toast for async confirmations

### Examples
- "✓ Content generated successfully"
- "✓ Changes saved"
- Green border flash on saved card
- Confetti animation (sparingly) for major completions
