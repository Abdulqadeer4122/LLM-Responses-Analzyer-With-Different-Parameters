'use client'

interface PromptEditorProps {
  prompt: string
  name: string
  onPromptChange: (prompt: string) => void
  onNameChange: (name: string) => void
}

export function PromptEditor({ prompt, name, onPromptChange, onNameChange }: PromptEditorProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Prompt Editor
      </h2>
      
      <div className="space-y-4">
        <div>
          <label htmlFor="experiment-name" className="block text-sm font-medium text-gray-700 mb-2">
            Experiment Name (Optional)
          </label>
          <input
            id="experiment-name"
            type="text"
            value={name}
            onChange={(e) => onNameChange(e.target.value)}
            placeholder="e.g., 'Temperature Comparison'"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
            Prompt
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            rows={6}
            placeholder="Enter your prompt here..."
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
          />
          <p className="mt-1 text-sm text-gray-500">
            {prompt.length} characters
          </p>
        </div>
      </div>
    </div>
  )
}
