'use client'

import { useState } from 'react'
import { Experiment, ResponseResult } from '@/lib/api'
import { formatScore, getScoreColor, downloadBlob } from '@/lib/utils'
import { api } from '@/lib/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, Cell } from 'recharts'

interface ResponseComparisonProps {
  experiment: Experiment
}

export function ResponseComparison({ experiment }: ResponseComparisonProps) {
  const [selectedResponse, setSelectedResponse] = useState<ResponseResult | null>(null)
  const [sortBy, setSortBy] = useState<'overall' | 'temperature' | 'tokens'>('overall')

  const sortedResponses = [...experiment.responses].sort((a, b) => {
    if (sortBy === 'overall') {
      return b.metrics.overall_score - a.metrics.overall_score
    } else if (sortBy === 'temperature') {
      return a.temperature - b.temperature
    } else {
      return (b.tokens_used || 0) - (a.tokens_used || 0)
    }
  })

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const blob = await api.exportExperiment(experiment.id, format)
      downloadBlob(blob, `experiment_${experiment.id}.${format}`)
    } catch (error) {
      alert(`Export failed: ${error}`)
    }
  }

  // Prepare data for charts
  const metricsData = sortedResponses.map((resp, idx) => ({
    index: idx + 1,
    coherence: resp.metrics.coherence_score,
    completeness: resp.metrics.completeness_score,
    length: resp.metrics.length_appropriateness,
    repetition: resp.metrics.repetition_penalty,
    structure: resp.metrics.structural_richness,
    overall: resp.metrics.overall_score,
    temperature: resp.temperature,
  }))

  const scatterData = sortedResponses.map((resp) => ({
    x: resp.temperature,
    y: resp.metrics.overall_score,
    tokens: resp.tokens_used || 0,
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {experiment.name || `Experiment ${experiment.id}`}
            </h2>
            <p className="text-sm text-gray-600 mt-1">{experiment.responses.length} responses</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleExport('json')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Export JSON
            </button>
            <button
              onClick={() => handleExport('csv')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Export CSV
            </button>
          </div>
        </div>

        <div className="bg-gray-50 rounded-md p-4 border border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-1">Prompt:</p>
          <p className="text-sm text-gray-900 whitespace-pre-wrap">{experiment.prompt}</p>
        </div>
      </div>

      {/* Metrics Overview Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Metrics Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metricsData.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="coherence" fill="#3b82f6" name="Coherence" />
              <Bar dataKey="completeness" fill="#10b981" name="Completeness" />
              <Bar dataKey="overall" fill="#f59e0b" name="Overall" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Temperature vs Quality</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" dataKey="x" name="Temperature" />
              <YAxis type="number" dataKey="y" name="Overall Score" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter name="Responses" data={scatterData} fill="#3b82f6">
                {scatterData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill="#3b82f6" />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Response Grid */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Responses</h3>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500"
          >
            <option value="overall">Sort by Overall Score</option>
            <option value="temperature">Sort by Temperature</option>
            <option value="tokens">Sort by Tokens</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedResponses.map((response) => (
            <div
              key={response.id}
              onClick={() => setSelectedResponse(response)}
              className={`border rounded-lg p-4 cursor-pointer transition-all bg-white text-gray-900 ${
                selectedResponse?.id === response.id
                  ? 'border-primary-500 bg-primary-50 shadow-md'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-500">
                  Temp: {response.temperature} | Top-P: {response.top_p}
                </span>
                <span
                  className={`text-sm font-semibold ${getScoreColor(
                    response.metrics.overall_score
                  )}`}
                >
                  {formatScore(response.metrics.overall_score)}%
                </span>
              </div>

              <div className="space-y-1 mb-3">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Coherence</span>
                  <span className={getScoreColor(response.metrics.coherence_score)}>
                    {formatScore(response.metrics.coherence_score)}%
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Completeness</span>
                  <span className={getScoreColor(response.metrics.completeness_score)}>
                    {formatScore(response.metrics.completeness_score)}%
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600">Structure</span>
                  <span className={getScoreColor(response.metrics.structural_richness)}>
                    {formatScore(response.metrics.structural_richness)}%
                  </span>
                </div>
              </div>

              <p className="text-sm text-gray-700 line-clamp-4">
                {response.response_text}
              </p>

              {response.tokens_used && (
                <p className="text-xs text-gray-400 mt-2">
                  {response.tokens_used} tokens
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Selected Response Detail Modal */}
      {selectedResponse && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedResponse(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto text-gray-900"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-900">Response Details</h3>
                <button
                  onClick={() => setSelectedResponse(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Parameters */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Parameters</h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Temperature</p>
                    <p className="text-sm font-medium text-gray-900">{selectedResponse.temperature}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Top P</p>
                    <p className="text-sm font-medium text-gray-900">{selectedResponse.top_p}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Max Tokens</p>
                    <p className="text-sm font-medium text-gray-900">{selectedResponse.max_tokens}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Presence Penalty</p>
                    <p className="text-sm font-medium text-gray-900">{selectedResponse.presence_penalty}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Frequency Penalty</p>
                    <p className="text-sm font-medium text-gray-900">{selectedResponse.frequency_penalty}</p>
                  </div>
                </div>
              </div>

              {/* Metrics */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Quality Metrics</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(selectedResponse.metrics).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 rounded-md p-3 text-gray-900">
                      <p className="text-xs text-gray-500 capitalize mb-1">
                        {key.replace(/_/g, ' ')}
                      </p>
                      <p className={`text-lg font-semibold ${getScoreColor(value)}`}>
                        {formatScore(value)}%
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Response Text */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Response</h4>
                <div className="bg-gray-50 rounded-md p-4 border border-gray-200">
                  <p className="text-sm text-gray-900 whitespace-pre-wrap">
                    {selectedResponse.response_text}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
