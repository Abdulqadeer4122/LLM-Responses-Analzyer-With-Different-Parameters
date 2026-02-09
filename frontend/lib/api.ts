/**
 * API client for LLM Lab backend.
 * 
 * All API calls are made from the client-side using TanStack Query.
 * This provides caching, error handling, and loading states automatically.
 */

const API_BASE_URL = 'https://llm-responses-analzyer-with-different.onrender.com/'

export interface ParameterRange {
  min: number
  max: number
  step?: number
  values?: number[]
}

export interface ExperimentRequest {
  prompt: string
  name?: string
  temperature?: ParameterRange
  top_p?: ParameterRange
  max_tokens?: ParameterRange
  presence_penalty?: ParameterRange
  frequency_penalty?: ParameterRange
  model?: string
}

export interface QualityMetrics {
  coherence_score: number
  completeness_score: number
  length_appropriateness: number
  repetition_penalty: number
  structural_richness: number
  overall_score: number
}

export interface ResponseResult {
  id: number
  temperature: number
  top_p: number
  max_tokens: number
  presence_penalty: number
  frequency_penalty: number
  response_text: string
  tokens_used?: number
  metrics: QualityMetrics
  created_at: string
}

export interface Experiment {
  id: number
  name?: string
  prompt: string
  created_at: string
  responses: ResponseResult[]
}

export interface ExperimentSummary {
  id: number
  name?: string
  prompt: string
  created_at: string
  response_count: number
}

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Create and run a new experiment
  createExperiment: async (request: ExperimentRequest): Promise<Experiment> => {
    return fetchAPI<Experiment>('/api/experiments/', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // List all experiments
  listExperiments: async (): Promise<ExperimentSummary[]> => {
    return fetchAPI<ExperimentSummary[]>('/api/experiments/')
  },

  // Get a specific experiment
  getExperiment: async (id: number): Promise<Experiment> => {
    return fetchAPI<Experiment>(`/api/experiments/${id}`)
  },

  // Delete an experiment
  deleteExperiment: async (id: number): Promise<void> => {
    await fetchAPI(`/api/experiments/${id}`, {
      method: 'DELETE',
    })
  },

  // Export experiment
  exportExperiment: async (id: number, format: 'json' | 'csv'): Promise<Blob> => {
    const response = await fetch(`${API_BASE_URL}/api/experiments/${id}/export?format=${format}`)
    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`)
    }
    return response.blob()
  },
}
