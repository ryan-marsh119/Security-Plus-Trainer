import { useLocation, Link } from 'react-router-dom'

export default function Results() {
  const { state } = useLocation()
  const results = state?.results

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 mb-4">No results to display.</p>
          <Link to="/dashboard" className="text-blue-600">Back to Dashboard</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">Session Results</h1>

        <div className="bg-white rounded-2xl p-8 shadow-sm text-center mb-6">
          <p className="text-6xl font-bold text-blue-600">{results.percent}%</p>
          <p className="text-gray-500 mt-2">
            {results.correct} / {results.total} correct
          </p>
        </div>

        {Object.keys(results.by_domain).length > 0 && (
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">By Domain</h2>
            {Object.entries(results.by_domain).map(([domainId, stats]) => (
              <div key={domainId} className="flex justify-between items-center py-2 border-b last:border-0">
                <span className="text-gray-700">Domain {domainId}</span>
                <span className="font-semibold">
                  {stats.correct}/{stats.total}{' '}
                  <span className="text-gray-400 font-normal text-sm">
                    ({stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0}%)
                  </span>
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 flex gap-4">
          <Link to="/study" className="flex-1 bg-blue-600 text-white rounded-xl py-3 text-center font-semibold hover:bg-blue-700">
            Study Again
          </Link>
          <Link to="/dashboard" className="flex-1 bg-white rounded-xl py-3 text-center font-semibold shadow-sm hover:shadow-md">
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
