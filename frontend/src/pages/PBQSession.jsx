import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import useSessionStore from '../store/sessionStore'
import QuestionWrapper from '../components/questions/QuestionWrapper'
import StatusScreen from '../components/StatusScreen'

export default function PBQSession() {
  const { domainId } = useParams()
  const { currentQuestion, error, startSession, clearError } = useSessionStore()
  const navigate = useNavigate()

  // Restart the session whenever the domain changes. startSession is a stable
  // Zustand action, intentionally omitted from deps.
  useEffect(() => {
    const id = domainId === 'all' ? null : Number(domainId)
    startSession('pbq', id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainId])

  const retry = () => {
    clearError()
    const id = domainId === 'all' ? null : Number(domainId)
    startSession('pbq', id)
  }

  if (error) {
    return <StatusScreen message={error} onRetry={retry} tone="error" />
  }

  if (!currentQuestion) {
    return <StatusScreen message="Loading PBQ…" />
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <p className="text-sm text-orange-600 font-semibold">PBQ Practice</p>
            <h2 className="text-xl font-semibold">
              {domainId === 'all' ? 'All Domains' : `Domain ${domainId}`}
            </h2>
          </div>
          <button
            onClick={() => navigate('/pbq')}
            className="text-sm text-gray-500 hover:text-gray-800"
          >
            ← PBQ Hub
          </button>
        </div>
        <QuestionWrapper question={currentQuestion} />
      </div>
    </div>
  )
}
