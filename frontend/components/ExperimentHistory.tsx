'use client'

import { ExperimentSummary } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

interface ExperimentHistoryProps {
  experiments: ExperimentSummary[]
  currentExperimentId: number | null
  onSelectExperiment: (id: number) => void
}

export function ExperimentHistory({
  experiments,
  currentExperimentId,
  onSelectExperiment,
}: ExperimentHistoryProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Experiment History
      </h2>

      {experiments.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-8">
          No experiments yet. Create your first experiment to get started.
        </p>
      ) : (
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {experiments.map((exp) => (
            <button
              key={exp.id}
              onClick={() => onSelectExperiment(exp.id)}
              className={`w-full text-left p-3 rounded-md border transition-colors ${
                currentExperimentId === exp.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {exp.name || `Experiment ${exp.id}`}
                  </p>
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    {exp.prompt}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs text-gray-400">
                      {exp.response_count} response{exp.response_count !== 1 ? 's' : ''}
                    </span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-400">
                      {formatDistanceToNow(new Date(exp.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
