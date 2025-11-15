# Content Repurposer Frontend

Modern React + TypeScript frontend for the YouTube Content Repurposer API, built with Vite and TailwindCSS.

## Features

- 🎨 Clean, modern UI based on shadcn/ui design system
- 📱 Fully responsive (mobile, tablet, desktop)
- ⚡ Fast performance with Vite
- 🎬 Process YouTube videos into social media content
- 📚 Browse and manage content library
- 🎯 Multiple content style presets
- 📋 One-click copy to clipboard
- 🚫 **No authentication required** - direct access to all features

## Tech Stack

- **React 19** with TypeScript
- **Vite** for blazing fast development
- **TailwindCSS** for styling
- **React Router** for navigation
- **Axios** for API calls
- **Bun** as package manager

## Getting Started

### Prerequisites

- Bun installed (https://bun.sh)
- Backend API running on http://localhost:8002

### Installation

```bash
# Install dependencies
bun install

# Start development server
bun run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
# Build
bun run build

# Preview production build
bun run preview
```

## Project Structure

```
src/
├── components/
│   ├── ui/              # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   └── Badge.tsx
│   └── features/        # Feature-specific components
├── pages/
│   ├── Dashboard.tsx    # Main dashboard
│   ├── VideoInput.tsx   # Video processing form
│   └── ContentLibrary.tsx # Content browser
├── lib/
│   └── api.ts          # API client
└── App.tsx             # Main app component
```

## Pages

### Dashboard (/)
- Overview statistics (videos processed, content generated)
- Recent content grid
- Quick action cards for common tasks

### Process Video (/process-video)
- Enter YouTube URL
- Fetch video information
- Select content style preset
- Generate content

### Content Library (/library)
- Browse all generated content
- Search and filter by type
- Copy content to clipboard
- Grid and list view modes

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8002
```

## API Integration

The frontend connects to the FastAPI backend. Make sure:

1. Backend is running on port 8002
2. CORS is configured to allow localhost:3000
3. All API endpoints are accessible

## Design System

Following the frontend-plan specifications:

- **Colors**: HSL-based with semantic colors (primary, success, warning, destructive)
- **Typography**: Inter for UI, JetBrains Mono for code/IDs
- **Spacing**: Base-8 system (4px, 8px, 16px, 24px, 32px...)
- **Components**: Shadcn-inspired with custom Tailwind styling

### Content Type Colors
- **Reels** (purple): `hsl(280 65% 60%)`
- **Carousels** (pink): `hsl(340 75% 55%)`
- **Tweets** (blue): `hsl(203 89% 53%)`

## Features

### No Authentication
As per requirements, there is no authentication or login system. All features are immediately accessible.

### Content Types
- **Reels**: Instagram/TikTok style video content (title, hook, script, caption)
- **Carousels**: Multi-slide image posts with headings and content
- **Tweets**: Twitter thread content with multiple tweets

### Style Presets
- Professional Business
- Social Media Casual
- E-commerce Entrepreneur
- Educational Content
- Fitness & Wellness

## Development

### Code Style
- TypeScript strict mode
- Functional components with hooks
- Tailwind for all styling
- ESLint for code quality

### Hot Module Replacement
Vite provides instant HMR - changes reflect immediately without page refresh.

## Troubleshooting

### API Connection Issues
- Verify backend is running: `curl http://localhost:8002`
- Check CORS configuration in backend (main.py)
- Verify .env file exists with correct VITE_API_URL

### Build Issues
- Clear dependencies: `rm -rf node_modules && bun install`
- Clear Vite cache: `rm -rf .vite`

## Roadmap

Future enhancements (not in current MVP):
- Content editing with AI prompts
- Bulk video processing
- Export functionality
- Advanced filtering
- Content preview modals

## License

Same as parent project.
