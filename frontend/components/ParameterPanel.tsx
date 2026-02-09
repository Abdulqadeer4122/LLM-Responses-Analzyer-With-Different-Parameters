'use client'

import { useState } from 'react'
import { ParameterRange } from '@/lib/api'

interface ParameterPanelProps {
  parameters: Record<string, ParameterRange | undefined>
  onParametersChange: (params: Record<string, ParameterRange | undefined>) => void
}

export function ParameterPanel({ parameters, onParametersChange }: ParameterPanelProps) {
  const [useRange, setUseRange] = useState<Record<string, boolean>>({
    temperature: false,
    top_p: false,
    max_tokens: false,
    presence_penalty: false,
    frequency_penalty: false,
  })

  const updateParameter = (key: string, field: 'min' | 'max' | 'step', value: number) => {
    const newParams = { ...parameters }
    if (!newParams[key]) {
      newParams[key] = { min: 0, max: 0 }
    }
    newParams[key] = {
      ...newParams[key]!,
      [field]: value,
    }
    onParametersChange(newParams)
  }

  const toggleRange = (key: string) => {
    const newUseRange = { ...useRange }
    newUseRange[key] = !newUseRange[key]
    setUseRange(newUseRange)
  }

  const paramConfigs = [
    {
      key: 'temperature',
      label: 'Temperature',
      min: 0,
      max: 2,
      step: 0.1,
      description: 'Controls randomness. Higher = more creative, lower = more focused.',
    },
    {
      key: 'top_p',
      label: 'Top P',
      min: 0,
      max: 1,
      step: 0.1,
      description: 'Nucleus sampling. Controls diversity via probability mass.',
    },
    {
      key: 'max_tokens',
      label: 'Max Tokens',
      min: 1,
      max: 4000,
      step: 100,
      description: 'Maximum number of tokens to generate.',
    },
    {
      key: 'presence_penalty',
      label: 'Presence Penalty',
      min: -2,
      max: 2,
      step: 0.1,
      description: 'Penalizes new topics. Positive = less repetition of topics.',
    },
    {
      key: 'frequency_penalty',
      label: 'Frequency Penalty',
      min: -2,
      max: 2,
      step: 0.1,
      description: 'Penalizes repetition. Positive = less repetition of tokens.',
    },
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Parameter Controls
      </h2>
      
      <div className="space-y-6">
        {paramConfigs.map((config) => {
          const param = parameters[config.key]
          const isRange = useRange[config.key]

          return (
            <div key={config.key} className="border-b border-gray-100 last:border-0 pb-4 last:pb-0">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <label className="text-sm font-medium text-gray-700">
                    {config.label}
                  </label>
                  <p className="text-xs text-gray-500 mt-1">{config.description}</p>
                </div>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isRange}
                    onChange={() => toggleRange(config.key)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-600">Range</span>
                </label>
              </div>

              {isRange ? (
                <div className="grid grid-cols-3 gap-3 mt-3">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Min</label>
                    <input
                      type="number"
                      min={config.min}
                      max={config.max}
                      step={config.step}
                      value={param?.min ?? config.min}
                      onChange={(e) =>
                        updateParameter(config.key, 'min', parseFloat(e.target.value) || 0)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Max</label>
                    <input
                      type="number"
                      min={config.min}
                      max={config.max}
                      step={config.step}
                      value={param?.max ?? config.max}
                      onChange={(e) =>
                        updateParameter(config.key, 'max', parseFloat(e.target.value) || 0)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Step</label>
                    <input
                      type="number"
                      min={config.step}
                      step={config.step}
                      value={param?.step ?? config.step}
                      onChange={(e) =>
                        updateParameter(config.key, 'step', parseFloat(e.target.value) || config.step)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
              ) : (
                <div className="mt-3">
                  <input
                    type="range"
                    min={config.min}
                    max={config.max}
                    step={config.step}
                    value={param?.min ?? config.min}
                    onChange={(e) => {
                      const value = parseFloat(e.target.value)
                      updateParameter(config.key, 'min', value)
                      updateParameter(config.key, 'max', value)
                    }}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{config.min}</span>
                    <span className="font-medium">{param?.min ?? config.min}</span>
                    <span>{config.max}</span>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
