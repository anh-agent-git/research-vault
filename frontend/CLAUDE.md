# Frontend Context

## Overview

Next.js frontend for Research Vault. Provides UI for paper upload, pattern review, library browsing, and query interface.

## Tech Stack

- **Framework:** Next.js 16.1.x (App Router)
- **React:** 19.x
- **Styling:** Tailwind CSS v4
- **Dark Mode:** next-themes
- **Icons:** Lucide React
- **TypeScript:** 5.x

## Directory Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout with ThemeProvider
│   │   ├── page.tsx         # Home page (health dashboard)
│   │   └── globals.css      # Tailwind imports + CSS variables
│   ├── components/
│   │   └── theme-provider.tsx  # next-themes wrapper
│   └── lib/
│       ├── api.ts           # Backend API client
│       └── utils.ts         # cn() utility
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts           # Standalone output for Docker
├── postcss.config.mjs
├── eslint.config.mjs        # Flat config with Prettier
├── .prettierrc
├── Dockerfile               # Multi-stage build
└── .dockerignore
```

## Key Patterns

### API Client

```typescript
import { api } from '@/lib/api';

// Health check
const health = await api.health();
// { status: 'ok', database: 'ok', qdrant: 'ok', sessions: 0, tracing: 'disabled' }
```

### Theme Support

Dark mode via `next-themes`:

```tsx
import { useTheme } from 'next-themes';

const { theme, setTheme } = useTheme();
setTheme('dark'); // or 'light', 'system'
```

### CSS Variables

Theme colors defined in `globals.css`:

```css
:root {
  --background: oklch(100% 0 0);
  --foreground: oklch(14.5% 0 0);
  /* ... */
}
.dark {
  --background: oklch(14.5% 0 0);
  --foreground: oklch(98.5% 0 0);
  /* ... */
}
```

### Utility Classes

```typescript
import { cn } from '@/lib/utils';

<div className={cn('base-class', condition && 'conditional-class')} />
```

## Common Commands

```bash
# Install dependencies
npm install

# Dev server
npm run dev

# Production build
npm run build

# Lint
npm run lint

# Format (if configured)
npx prettier --write .
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NEXT_PUBLIC_API_URL | No | http://localhost:8000 | Backend API URL |

## Docker Build

Multi-stage build with standalone output:

```bash
docker build -t research-vault-frontend .
```

Build args:
- `NEXT_PUBLIC_API_URL` - API URL baked into client bundle

## Conventions

- Use App Router (not Pages Router)
- Server Components by default, `'use client'` only when needed
- Tailwind for all styling (no CSS modules)
- Path alias `@/` maps to `src/`
