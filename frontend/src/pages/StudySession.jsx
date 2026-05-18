import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useSessionStore from '../store/sessionStore'
import QuestionWrapper from '../components/questions/QuestionWrapper'

export default function StudySession() {
  const { session, currentQuestion, startSession } = useSessionStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (!session) {
      startSession('study')
    }
  }, [])

  if (!currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading question…</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Study Mode</h2>
          <button
            onClick={() => navigate('/dashboard')}
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
