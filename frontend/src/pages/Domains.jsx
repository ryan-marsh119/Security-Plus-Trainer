import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import client from '../api/client'
import useSessionStore from '../store/sessionStore'

export default function Domains() {
  const [domains, setDomains] = useState([])
  const [progress, setProgress] = useState({})
  const [loading, setLoading] = useState(true)
  const { startSession } = useSessionStore()
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      client.get('/domains/'),
      client.get('/progress/domains/').catch(() => ({ data: [] })),
    ])
      .then(([domainsRes, progressRes]) => {
        setDomains(domainsRes.data)
        // Index per-domain progress by domain id for quick lookup.
        const byId = {}
        for (const row of progressRes.data) byId[row.domain] = row
        setProgress(byId)
      })
      .finally(() => setLoading(false))
  }, [])

  const accuracy = (domainId) => {
    const row = progress[domainId]
    if (!row || !row.total_seen) return null
    return Math.round((row.total_correct / row.total_seen) * 100)
  }

  const startInDomain = async (sessionType, domainId) => {
    await startSession(sessionType, domainId)
    navigate(sessionType === 'exam' ? '/exam' : '/study')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading domains…</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Domains</h1>
            <p className="text-gray-500 mt-1">Browse and drill into the five SY0-701 domains</p>
          </div>
          <Link to="/dashboard" className="text-sm text-gray-500 hover:text-gray-800">
            ← Dashboard
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {domains.map((domain) => {
            const acc = accuracy(domain.id)
            const seen = progress[domain.id]?.total_seen ?? 0
            return (
              <div key={domain.id} className="bg-white rounded-xl p-6 shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-blue-600 font-semibold">Domain {domain.number}</p>
                    <p className="font-bold text-gray-800 mt-1">{domain.name}</p>
                    <p className="text-sm text-gray-500 mt-1">{domain.weight_pct}% of exam</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-800">
                      {acc === null ? '—' : `${acc}%`}
                    </p>
                    <p className="text-xs text-gray-400">{seen} seen</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => startInDomain('study', domain.id)}
                    className="flex-1 bg-blue-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-blue-700"
                  >
                    Study
                  </button>
                  <button
                    onClick={() => startInDomain('exam', domain.id)}
                    className="flex-1 bg-purple-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-purple-700"
                  >
                    Practice
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
