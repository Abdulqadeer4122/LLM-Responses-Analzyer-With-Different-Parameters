# LLM Lab Architecture

## System Overview

LLM Lab is a full-stack application designed for experimenting with LLM parameters and analyzing response quality. The system is built with a clear separation between frontend (Next.js) and backend (FastAPI), communicating via REST APIs.

## Backend Architecture

### Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: LLM abstraction layer for OpenAI integration
- **SQLAlchemy**: ORM for database operations
- **SQLite/PostgreSQL**: Database for experiment persistence

### Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization and CORS setup
│   ├── models/              # Pydantic schemas for API validation
│   │   └── schemas.py       # Request/response models
│   ├── services/            # Business logic layer
│   │   ├── llm_service.py   # LangChain + OpenAI integration
│   │   ├── metrics.py       # Quality metrics computation
│   │   └── experiment.py    # Parameter combination generation
│   ├── api/                 # API route handlers
│   │   └── experiments.py   # CRUD operations for experiments
│   └── db/                  # Database layer
│       ├── database.py      # Database connection and session management
│       └── models.py        # SQLAlchemy ORM models
```

### Key Design Decisions

#### Why LangChain?

1. **Standardization**: Provides a consistent interface across LLM providers
2. **Token Tracking**: Built-in callbacks for automatic token counting
3. **Error Handling**: Retry logic and better error handling for API issues
4. **Extensibility**: Easy to add chains, prompt templates, or agent workflows
5. **Future-proofing**: Clear path for adding streaming, function calling, etc.

#### API Design

**Endpoints:**
- `POST /api/experiments/` - Create and run new experiment
- `GET /api/experiments/` - List all experiments (summary)
- `GET /api/experiments/{id}` - Get experiment with all responses
- `DELETE /api/experiments/{id}` - Delete experiment
- `GET /api/experiments/{id}/export?format=json|csv` - Export experiment data

**Request Validation:**
- Pydantic models ensure type safety and validation
- Parameter range validation prevents excessive API calls (max 50 combinations)
- Clear error messages for invalid inputs

**Error Handling:**
- Rate limit handling via LangChain retries
- Invalid parameter ranges return 400 with descriptive messages
- LLM API errors are caught and returned as 500 with details
- Database errors are handled gracefully

### Quality Metrics

All metrics are computed purely via code (no LLM evaluation):

1. **Coherence Score** (0-1)
   - Measures sentence flow and punctuation quality
   - Factors: proper sentence endings, transition words, sentence length variance
   - Formula: Weighted combination (40% punctuation, 30% transitions, 30% variance)

2. **Completeness Score** (0-1)
   - Measures prompt coverage
   - Factors: question word coverage, keyword overlap, response length adequacy
   - Formula: Weighted combination (40% questions, 40% keywords, 20% length)

3. **Length Appropriateness** (0-1)
   - Measures if response length matches prompt complexity
   - Factors: response length vs prompt length, token efficiency
   - Formula: Ratio-based with ideal range (1.5x to 8x prompt length)

4. **Repetition Penalty** (0-1, inverted)
   - Detects repetition (lower score = more repetition)
   - Factors: N-gram repetition, sentence repetition
   - Formula: Inverse of repetition ratio

5. **Structural Richness** (0-1)
   - Measures formatting and structure diversity
   - Factors: paragraph breaks, lists, formatting markers, sentence variety
   - Formula: Weighted combination of structural elements

**Overall Score**: Weighted average of all metrics (coherence 25%, completeness 30%, length 15%, repetition 15%, structure 15%)

### Database Schema

**Experiments Table:**
- `id` (PK)
- `name` (optional)
- `prompt` (text)
- `created_at`, `updated_at` (timestamps)

**Responses Table:**
- `id` (PK)
- `experiment_id` (FK)
- Parameters: `temperature`, `top_p`, `max_tokens`, `presence_penalty`, `frequency_penalty`
- `response_text` (text)
- `tokens_used` (integer, nullable)
- `metrics` (JSON)
- `created_at` (timestamp)

## Frontend Architecture

### Technology Stack
- **Next.js 14+**: App Router with Server-Side Rendering
- **React 18**: Component library
- **TanStack Query**: Data fetching, caching, and synchronization
- **Recharts**: Data visualization
- **Tailwind CSS**: Utility-first styling
- **TypeScript**: Type safety

### Component Hierarchy

```
app/
├── layout.tsx              # Root layout with providers
├── page.tsx                # Main page (client component)
└── providers.tsx           # TanStack Query provider

components/
├── Header.tsx              # App header/navigation
├── PromptEditor.tsx        # Prompt input and experiment name
├── ParameterPanel.tsx      # Parameter range controls
├── ExperimentExecution.tsx # Run experiment button and model selection
├── ExperimentHistory.tsx   # Sidebar with experiment list
└── ResponseComparison.tsx  # Results grid, charts, and detail modal
```

### Client vs Server Component Decisions

**Client Components** (`'use client'`):
- All interactive components (forms, buttons, modals)
- Components using hooks (useState, useQuery, etc.)
- Components with event handlers

**Server Components** (default):
- None in this implementation (all components are interactive)

**Rationale**: Since the app is highly interactive with real-time data fetching, all components are client-side. This allows for:
- Immediate UI updates
- Optimistic updates
- Client-side caching via TanStack Query
- Better user experience with loading states

### UX Design Rationale

1. **Three-Column Layout**:
   - Left: Input controls (prompt, parameters, execution)
   - Right: Experiment history (quick access to past experiments)
   - Bottom: Results (only shown after experiment runs)
   - Rationale: Clear separation of input vs output, reduces cognitive load

2. **Parameter Controls**:
   - Sliders for single values, range inputs for experiments
   - Toggle to switch between single value and range mode
   - Real-time preview of parameter values
   - Rationale: Intuitive for both beginners and advanced users

3. **Response Comparison Grid**:
   - Card-based layout with key metrics visible
   - Sortable by different criteria
   - Click to view full details in modal
   - Rationale: Easy to scan multiple responses, drill down when needed

4. **Visual Metrics**:
   - Color-coded scores (green/yellow/red)
   - Charts for comparison (bar charts, scatter plots)
   - Badge-style metric display
   - Rationale: Visual comparison is faster than reading numbers

5. **Export Functionality**:
   - JSON for programmatic access
   - CSV for spreadsheet analysis
   - Rationale: Supports different use cases (developers vs analysts)

### State Management

- **TanStack Query**: Handles server state (experiments, responses)
  - Automatic caching
  - Background refetching
  - Optimistic updates
  - Error handling

- **React State**: Handles UI state (form inputs, selected items, modals)
  - Local component state for inputs
  - Lifted state in page.tsx for shared form data

### API Integration

- Centralized API client (`lib/api.ts`)
- Type-safe request/response types
- Error handling with user-friendly messages
- Automatic retries via TanStack Query

## Data Flow

1. **Experiment Creation**:
   ```
   User Input → PromptEditor/ParameterPanel → ExperimentExecution
   → API Request → Backend validates → Generate combinations
   → LangChain batch calls → Compute metrics → Save to DB
   → Return results → Frontend displays in ResponseComparison
   ```

2. **Experiment Viewing**:
   ```
   User clicks experiment → API request → Backend queries DB
   → Returns experiment + responses → Frontend displays
   → User can sort, filter, export
   ```

3. **Export**:
   ```
   User clicks export → API request → Backend formats data
   → Returns blob → Frontend downloads file
   ```

## Security Considerations

1. **API Key**: Stored in backend environment variables, never exposed to frontend
2. **CORS**: Configured to only allow requests from frontend origin
3. **Input Validation**: All inputs validated on backend (Pydantic)
4. **Rate Limiting**: Parameter combination limit prevents excessive API calls
5. **Error Messages**: Generic errors to users, detailed logs on server

## Performance Optimizations

1. **Concurrent LLM Calls**: Batch requests run in parallel via asyncio
2. **Database Indexing**: Primary keys and foreign keys indexed
3. **Frontend Caching**: TanStack Query caches responses
4. **Lazy Loading**: Results only loaded when experiment selected
5. **Pagination**: Experiment list could be paginated (currently limited to 50)

## Future Enhancements

1. **Streaming Responses**: Show responses as they're generated
2. **Comparison Tools**: Side-by-side diff view
3. **Custom Metrics**: Allow users to define custom metrics
4. **Experiment Templates**: Save parameter presets
5. **Collaboration**: Share experiments with team members
6. **Analytics Dashboard**: Aggregate statistics across experiments
