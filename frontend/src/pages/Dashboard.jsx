import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import useUserStore from '../store/userStore'
import client from '../api/client'

export default function Dashboard() {
  const { user, logout } = useUserStore()
  const navigate = useNavigate()
  const [overview, setOverview] = useState(null)

  useEffect(() => {
    let cancelled = false
    client
      .get('/progress/')
      .then(({ data }) => {
        if (!cancelled) setOverview(data)
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  const handleLogout = async () => {
    try {
      await logout()
    } finally {
      navigate('/login')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Security+ Dashboard</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">{user?.username}</span>
            <button onClick={handleLogout} className="text-sm text-gray-500 hover:text-gray-800">
              Logout
            </button>
          </div>
        </div>

        {overview && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Questions Seen', value: overview.total_seen },
              { label: 'Total Questions', value: overview.total_questions },
              { label: 'Mastered', value: overview.total_mastered },
              { label: 'Due for Review', value: overview.due_count },
            ].map(({ label, value }) => (
              <div key={label} className="bg-white rounded-xl p-4 shadow-sm text-center">
                <p className="text-3xl font-bold text-blue-600">{value}</p>
                <p className="text-sm text-gray-500 mt-1">{label}</p>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <Link to="/study" className="bg-blue-600 text-white rounded-xl p-6 text-center hover:bg-blue-700">
            <p className="text-xl font-bold">Study Mode</p>
            <p className="text-sm mt-1 opacity-80">SM-2 spaced repetition</p>
          </Link>
          <Link to="/exam" className="bg-purple-600 text-white rounded-xl p-6 text-center hover:bg-purple-700">
            <p className="text-xl font-bold">Practice Exam</p>
            <p className="text-sm mt-1 opacity-80">90 questions, 90 minutes</p>
          </Link>
          <Link to="/pbq" className="bg-orange-500 text-white rounded-xl p-6 text-center hover:bg-orange-600">
            <p className="text-xl font-bold">PBQ Practice</p>
            <p className="text-sm mt-1 opacity-80">Performance-based questions</p>
          </Link>
          <Link to="/domains" className="bg-white rounded-xl p-6 text-center shadow-sm hover:shadow-md">
            <p className="text-xl font-bold text-gray-800">Domains</p>
            <p className="text-sm mt-1 text-gray-500">Browse by domain</p>
          </Link>
        </div>
      </div>
    </div>
  )
}
