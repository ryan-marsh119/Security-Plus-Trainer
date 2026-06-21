import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useSessionStore from '../store/sessionStore'
import QuestionWrapper from '../components/questions/QuestionWrapper'
import StatusScreen from '../components/StatusScreen'

const EXAM_MINUTES = 90

export default function PracticeExam() {
  const { session, currentQuestion, error, questionsServed, startSession, completeSession, clearError } =
    useSessionStore()
  const navigate = useNavigate()
  const [secondsLeft, setSecondsLeft] = useState(EXAM_MINUTES * 60)
  // Guards against double-completion (timer expiry AND a manual "Submit Exam"
  // click both calling handleComplete). A ref, not state, so it's read
  // synchronously without a re-render race.
  const completingRef = useRef(false)

  const handleComplete = useCallback(async () => {
    if (completingRef.current) return
    completingRef.current = true
    const results = await completeSession()
    if (results) {
      navigate('/results', { state: { results, sessionId: results.sessionId } })
    } else {
      // Completion failed — allow another attempt and surface the store error.
      completingRef.current = false
    }
  }, [completeSession, navigate])

  // Start the exam once on mount. Mount-only by design (guarded actions are
  // stable Zustand refs); re-running on session changes would restart the exam.
  useEffect(() => {
    if (!session) startSession('exam')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Tick the clock down. The interval ONLY mutates secondsLeft — completion is
  // triggered by the separate effect below so we never call a side effect from
  // inside a setState updater (which double-fires under StrictMode).
  useEffect(() => {
    if (!session) return
    const interval = setInterval(() => {
      setSecondsLeft((s) => (s <= 1 ? 0 : s - 1))
    }, 1000)
    return () => clearInterval(interval)
  }, [session])

  // Fire completion once when the clock hits zero.
  useEffect(() => {
    if (secondsLeft === 0 && session) handleComplete()
  }, [secondsLeft, session, handleComplete])

  const mins = Math.floor(secondsLeft / 60).toString().padStart(2, '0')
  const secs = (secondsLeft % 60).toString().padStart(2, '0')

  if (error) {
    return (
      <StatusScreen
        message={error}
        onRetry={() => {
          clearError()
          if (!session) startSession('exam')
        }}
        tone="error"
      />
    )
  }

  if (!currentQuestion) {
    return <StatusScreen message="Loading exam…" />
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-semibold">Practice Exam</h2>
            <p className="text-sm text-gray-500">Question {questionsServed}</p>
          </div>
          <div className="flex items-center gap-4">
            <span className={`font-mono text-lg ${secondsLeft < 300 ? 'text-red-600' : 'text-gray-700'}`}>
              {mins}:{secs}
            </span>
            <button
              type="button"
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
