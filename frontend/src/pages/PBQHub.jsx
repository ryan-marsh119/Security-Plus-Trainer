import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import client from '../api/client'

export default function PBQHub() {
  const [domains, setDomains] = useState([])

  useEffect(() => {
    client.get('/domains/').then(({ data }) => setDomains(data)).catch(() => {})
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">PBQ Practice Hub</h1>
            <p className="text-gray-500 mt-1">Performance-based questions by domain</p>
          </div>
          <Link to="/dashboard" className="text-sm text-gray-500 hover:text-gray-800">
            ← Dashboard
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {domains.map((domain) => (
            <Link
              key={domain.id}
              to={`/pbq/${domain.id}`}
              className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm text-orange-600 font-semibold">Domain {domain.number}</p>
                  <p className="font-bold text-gray-800 mt-1">{domain.name}</p>
                  <p className="text-sm text-gray-500 mt-1">{domain.weight_pct}% of exam</p>
                </div>
                <span className="text-2xl">→</span>
              </div>
            </Link>
          ))}
        </div>

        <div className="mt-6">
          <Link
            to="/pbq/all"
            className="block w-full bg-orange-500 text-white rounded-xl p-4 text-center font-semibold hover:bg-orange-600"
          >
            Start All PBQs (Cross-Domain)
          </Link>
        </div>
      </div>
    </div>
  )
}
