import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import useSessionStore from '../store/sessionStore'
import QuestionWrapper from '../components/questions/QuestionWrapper'

export default function PBQSession() {
  const { domainId } = useParams()
  const { session, currentQuestion, startSession } = useSessionStore()
  const navigate = useNavigate()

  useEffect(() => {
    const id = domainId === 'all' ? null : Number(domainId)
    startSession('pbq', id)
  }, [domainId])

  if (!currentQuestion) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading PBQ…</p>
      </div>
    )
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
