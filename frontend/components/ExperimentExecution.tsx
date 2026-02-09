'use client'

import { useState } from 'react'

interface ExperimentExecutionProps {
  onRunExperiment: (model: string) => void
  isLoading: boolean
}

export function ExperimentExecution({ onRunExperiment, isLoading }: ExperimentExecutionProps) {
  const [model, setModel] = useState('gpt-3.5-turbo')

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Run Experiment
      </h2>

      <div className="space-y-4">
        <div>
          <label htmlFor="model-select" className="block text-sm font-medium text-gray-700 mb-2">
            Model
          </label>
          <select
            id="model-select"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500"
          >
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
          </select>
        </div>

        <button
          onClick={() => onRunExperiment(model)}
          disabled={isLoading}
          className="w-full bg-primary-600 text-white px-6 py-3 rounded-md font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Running Experiment...
            </span>
          ) : (
            'Run Experiment'
          )}
        </button>
      </div>
    </div>
  )
}
