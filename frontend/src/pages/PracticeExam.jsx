import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useSessionStore from '../store/sessionStore'
import QuestionWrapper from '../components/questions/QuestionWrapper'

const EXAM_MINUTES = 90

export default function PracticeExam() {
  const { session, currentQuestion, startSession, completeSession } = useSessionStore()
  const navigate = useNavigate()
  const [secondsLeft, setSecondsLeft] = useState(EXAM_MINUTES * 60)

  useEffect(() => {
    if (!session) startSession('exam')
  }, [])

  useEffect(() => {
    if (!session) return
    const interval = setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          clearInterval(interval)
          handleComplete()
          return 0
        }
        return s - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [session])

  const handleComplete = async () => {
    const results = await completeSession()
    navigate('/results', { state: { results } })
  }

  const mins = Math.floor(secondsLeft / 60).toString().padStart(2, '0')
  const secs = (secondsLeft % 60).toString().padStart(2, '0')

  if (!currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading exam…</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Practice Exam</h2>
          <div className="flex items-center gap-4">
            <span className={`font-mono text-lg ${secondsLeft < 300 ? 'text-red-600' : 'text-gray-700'}`}>
              {mins}:{secs}
            </span>
            <button
              onClick={handleComplete}
              className="text-sm bg-red-100 text-red-700 px-3 py-1 rounded-lg hover:bg-red-200"
            >
              Submit Exam
            </button>
          </div>
        </div>
        <QuestionWrapper question={currentQuestion} examMode />
      </div>
    </div>
  )
}
