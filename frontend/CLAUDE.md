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
- **Testing:** Vitest + Testing Library

## Directory Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout with MainNav
│   │   ├── page.tsx             # Redirects to /library
│   │   ├── globals.css          # Tailwind imports + CSS variables
│   │   ├── upload/page.tsx      # Paper upload (PDF/text)
│   │   ├── review/[paperId]/page.tsx  # Pattern review
│   │   ├── library/page.tsx     # Paper list with filters
│   │   └── query/page.tsx       # Query interface
│   ├── components/
│   │   ├── ui/                  # Base UI components
│   │   │   ├── badge.tsx
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── loading.tsx
│   │   │   ├── select.tsx
│   │   │   ├── textarea.tsx
│   │   │   └── index.ts
│   │   ├── nav/                 # Navigation
│   │   │   ├── main-nav.tsx
│   │   │   └── index.ts
│   │   ├── upload/              # Upload page components
│   │   │   ├── file-upload.tsx
│   │   │   ├── text-input.tsx
│   │   │   ├── metadata-form.tsx
│   │   │   └── index.ts
│   │   ├── review/              # Review page components
│   │   │   ├── pattern-card.tsx
│   │   │   ├── review-summary.tsx
│   │   │   └── index.ts
│   │   ├── library/             # Library page components
│   │   │   ├── filter-bar.tsx
│   │   │   ├── paper-card.tsx
│   │   │   ├── pattern-detail.tsx
│   │   │   └── index.ts
│   │   ├── query/               # Query page components
│   │   │   ├── search-input.tsx
│   │   │   ├── response-display.tsx
│   │   │   ├── pattern-detail-modal.tsx  # Modal for viewing pattern details
│   │   │   ├── conversation-history.tsx
│   │   │   └── index.ts
│   │   └── theme-provider.tsx   # next-themes wrapper
│   ├── lib/
│   │   ├── api.ts               # Backend API client
│   │   ├── api.test.ts          # API client tests
│   │   ├── utils.ts             # cn() utility
│   │   └── utils.test.ts        # Utility tests
│   ├── test/
│   │   └── setup.ts             # Vitest setup
│   └── types/
│       └── index.ts             # TypeScript types
├── vitest.config.ts             # Vitest configuration
├── package.json
├── tsconfig.json
├── next.config.ts
├── Dockerfile
└── .dockerignore
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Redirects to `/library` |
| `/upload` | Upload PDF or paste text, extract patterns |
| `/review/[paperId]` | Review and approve/reject extracted patterns |
| `/library` | Browse papers with filters, manage patterns |
| `/query` | Ask questions about your research library |

## Key Patterns

### API Client

```typescript
import { uploadPaper, listPapers, submitQuery, getPattern } from '@/lib/api';

// Upload paper
const result = await uploadPaper(formData);

// List papers with filters
const papers = await listPapers({ status: 'active', limit: 20 });

// Get pattern details (includes paper_title)
const pattern = await getPattern('pattern-uuid');

// Query the library
const response = await submitQuery('What patterns relate to X?', sessionId);
```

### UI Components

All components in `@/components/ui/` follow the shadcn-style pattern:
- No external component library dependencies
- Use `cn()` for conditional classes
- Support light/dark mode via CSS variables
- Props extend HTML element attributes

```tsx
import { Button, Card, Badge, LoadingSpinner } from '@/components/ui';

<Button variant="destructive" size="sm">Delete</Button>
<Badge variant="success">Active</Badge>
<LoadingSpinner size="lg" />
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

# Run tests
npm test

# Format (if configured)
npx prettier --write .
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NEXT_PUBLIC_API_URL | No | http://localhost:8000 | Backend API URL |

## Testing

Uses Vitest with jsdom environment and Testing Library:

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch
```

Test files: `*.test.ts` or `*.test.tsx` alongside source files.

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
- Wrap `useSearchParams()` in Suspense boundary
- Tailwind for all styling (no CSS modules)
- Path alias `@/` maps to `src/`
- Desktop-first responsive design
