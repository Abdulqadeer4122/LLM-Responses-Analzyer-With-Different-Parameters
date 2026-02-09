'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, ExperimentRequest, ParameterRange } from '@/lib/api'
import { PromptEditor } from '@/components/PromptEditor'
import { ParameterPanel } from '@/components/ParameterPanel'
import { ExperimentExecution } from '@/components/ExperimentExecution'
import { ResponseComparison } from '@/components/ResponseComparison'
import { ExperimentHistory } from '@/components/ExperimentHistory'
import { Header } from '@/components/Header'

export default function Home() {
  const [currentExperiment, setCurrentExperiment] = useState<number | null>(null)
  const [prompt, setPrompt] = useState('')
  const [name, setName] = useState('')
  const [parameters, setParameters] = useState<Record<string, ParameterRange | undefined>>({
    temperature: { min: 0.7, max: 0.7 },
    top_p: { min: 1.0, max: 1.0 },
    max_tokens: { min: 1000, max: 1000 },
    presence_penalty: { min: 0.0, max: 0.0 },
    frequency_penalty: { min: 0.0, max: 0.0 },
  })
  const queryClient = useQueryClient()

  // Fetch current experiment if selected
  const { data: experiment, isLoading: isLoadingExperiment } = useQuery({
    queryKey: ['experiment', currentExperiment],
    queryFn: () => api.getExperiment(currentExperiment!),
    enabled: currentExperiment !== null,
  })

  // Fetch experiment list
  const { data: experiments } = useQuery({
    queryKey: ['experiments'],
    queryFn: () => api.listExperiments(),
  })

  // Create experiment mutation
  const createMutation = useMutation({
    mutationFn: (request: ExperimentRequest) => api.createExperiment(request),
    onSuccess: (data) => {
      setCurrentExperiment(data.id)
      queryClient.invalidateQueries({ queryKey: ['experiments'] })
    },
  })

  const handleRunExperiment = (model: string) => {
    if (!prompt.trim()) {
      alert('Please enter a prompt')
      return
    }

    const request: ExperimentRequest = {
      prompt: prompt.trim(),
      name: name.trim() || undefined,
      model,
      ...Object.fromEntries(
        Object.entries(parameters).map(([key, value]) => [
          key,
          value && value.min === value.max ? undefined : value,
        ])
      ),
    }

    createMutation.mutate(request)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            LLM Lab
          </h1>
          <p className="text-gray-600">
            Experiment with LLM parameters, generate multiple responses, and analyze quality through custom metrics.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Left Column: Input Controls */}
          <div className="lg:col-span-2 space-y-6">
            <PromptEditor
              prompt={prompt}
              name={name}
              onPromptChange={setPrompt}
              onNameChange={setName}
            />

            <ParameterPanel
              parameters={parameters}
              onParametersChange={setParameters}
            />

            <ExperimentExecution
              onRunExperiment={handleRunExperiment}
              isLoading={createMutation.isPending}
            />
          </div>

          {/* Right Column: History */}
          <div className="lg:col-span-1">
            <ExperimentHistory
              experiments={experiments || []}
              currentExperimentId={currentExperiment}
              onSelectExperiment={setCurrentExperiment}
            />
          </div>
        </div>

        {/* Results Section */}
        {isLoadingExperiment && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <p className="mt-2 text-gray-600">Loading experiment...</p>
          </div>
        )}

        {experiment && !isLoadingExperiment && (
          <div className="mt-8">
            <ResponseComparison experiment={experiment} />
          </div>
        )}
      </main>
    </div>
  )
}
