# Frontend Design Plan - YouTube Repurposer

## Overview
Modern, beautiful SaaS application for transforming YouTube videos into social media content. Design inspired by shadcn/ui aesthetics with emphasis on clarity, efficiency, and delightful user experience.

## Organization

```
frontend-plan/
├── README.md                          # This file
├── design-system/                     # Core design specifications
│   ├── colors.md                      # Color palette & usage
│   ├── typography.md                  # Font system & hierarchy
│   ├── spacing.md                     # Spacing scale & grid
│   ├── components-spec.md             # Component design specs
│   └── design-principles.md           # Core design philosophy
├── screens/                           # Screen-by-screen layouts
│   ├── 01-authentication.md           # Login/signup screens
│   ├── 02-dashboard.md                # Main dashboard
│   ├── 03-video-input.md              # Video URL input & processing
│   ├── 04-content-generation.md       # Content generation interface
│   ├── 05-content-editor.md           # Edit generated content
│   ├── 06-content-library.md          # View all generated content
│   ├── 07-settings.md                 # Configuration & preferences
│   └── 08-bulk-processing.md          # Bulk video processing
├── flows/                             # User journey flowcharts
│   ├── user-journeys.md               # All user journey diagrams
│   ├── video-processing-flow.md       # Video processing flow
│   └── content-editing-flow.md        # Content editing flow
└── components/                        # Reusable component patterns
    ├── content-card.md                # Content piece display cards
    ├── video-input-widget.md          # Video URL input component
    └── style-selector.md              # Style preset selector
```

## Design Goals

1. **Minimal Friction**: Users should accomplish tasks with minimal clicks
2. **Visual Clarity**: Information hierarchy should be immediately obvious
3. **Responsive Beauty**: Looks stunning on all screen sizes
4. **Speed Perception**: UI should feel instant and responsive
5. **Progressive Disclosure**: Show complexity only when needed

## Key Features to Support

- Single video processing with style customization
- Bulk video processing
- Content editing with natural language
- Content library with filtering
- Style preset management
- Configuration customization
- Real-time processing status

## Screen Hierarchy

### Primary Screens (Full Layout)
1. Dashboard - Main landing after login
2. Video Input - Process new videos
3. Content Library - Browse all generated content
4. Bulk Processing - Process multiple videos
5. Settings - User preferences & API config

### Secondary Screens (Modal/Overlay Context)
1. Content Editor - Edit individual content pieces
2. Style Preset Creator - Create custom styles
3. Video Details - View video metadata & transcript

### Subscreens (Tabs/Sections within screens)
1. Dashboard tabs: Overview, Recent Activity, Quick Stats
2. Content Library filters: By Type, By Video, By Date
3. Settings sections: Account, Content Config, API Keys, Style Presets
