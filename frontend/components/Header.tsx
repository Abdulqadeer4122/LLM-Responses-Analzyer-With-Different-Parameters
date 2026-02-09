'use client'

export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">L</span>
            </div>
            <h1 className="text-xl font-semibold text-gray-900">LLM Lab</h1>
          </div>
          <nav className="flex items-center space-x-6">
            <a href="#" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
              Experiments
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
              Documentation
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}
