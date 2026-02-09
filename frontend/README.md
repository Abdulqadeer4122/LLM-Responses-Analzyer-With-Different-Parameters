# LLM Lab Frontend

Next.js frontend for LLM Lab application.

## Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Configure environment** (optional):
Create `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Run development server**:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
npm start
```

## Project Structure

- `app/`: Next.js App Router pages and layouts
- `components/`: React components
- `lib/`: Utilities and API client
  - `api.ts`: API client with type-safe requests
  - `utils.ts`: Helper functions

## Key Features

- **Prompt Editor**: Input prompt and experiment name
- **Parameter Panel**: Configure LLM parameters (temperature, top_p, etc.)
- **Experiment Execution**: Run experiments with selected model
- **Response Comparison**: View and compare all responses with metrics
- **Experiment History**: Browse and select past experiments
- **Export**: Download results as JSON or CSV

## Component Architecture

All components are client components (`'use client'`) for interactivity:
- Form inputs use React state
- Data fetching uses TanStack Query
- Charts use Recharts library
- Styling uses Tailwind CSS

## API Integration

The frontend communicates with the backend via REST API:
- Base URL: `http://localhost:8000` (configurable via `NEXT_PUBLIC_API_URL`)
- All API calls are type-safe using TypeScript interfaces
- Error handling is centralized in the API client
