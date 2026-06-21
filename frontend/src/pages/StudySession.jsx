import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useSessionStore from '../store/sessionStore'
import QuestionWrapper from '../components/questions/QuestionWrapper'
import StatusScreen from '../components/StatusScreen'

export default function StudySession() {
  const { session, currentQuestion, error, startSession, fetchNextQuestion, completeSession, clearError } =
    useSessionStore()
  const navigate = useNavigate()

  // Start a study session once on mount. Guarded actions are stable Zustand
  // refs; intentionally mount-only so it doesn't restart on every state change.
  useEffect(() => {
    if (!session) {
      startSession('study')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const retry = () => {
    clearError()
    if (!session) startSession('study')
    else fetchNextQuestion()
  }

  const handleEnd = async () => {
    const results = await completeSession()
    if (results) navigate('/results', { state: { results, sessionId: results.sessionId } })
    else navigate('/dashboard')
  }

  if (error) {
    return <StatusScreen message={error} onRetry={retry} tone="error" />
  }

  if (!currentQuestion) {
    return <StatusScreen message="Loading question…" />
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Study Mode</h2>
          <button
            type="button"
            onClick={handleEnd}
            className="text-sm text-gray-500 hover:text-gray-800"
          >
            End Session
          </button>
        </div>
        <QuestionWrapper question={currentQuestion} />
      </div>
    </div>
  )
}
