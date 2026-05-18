import { useState } from 'react'
import useSessionStore from '../../store/sessionStore'

export default function QuestionWrapper({ question, examMode = false }) {
  const [selected, setSelected] = useState(null)
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState(null)
  const { submitAnswer, fetchNextQuestion } = useSessionStore()

  const handleSubmit = async () => {
    if (selected === null) return
    const answer = buildAnswer(question, selected)
    const res = await submitAnswer(answer)
    setResult(res)
    setSubmitted(true)
  }

  const handleNext = () => {
    setSelected(null)
    setSubmitted(false)
    setResult(null)
    fetchNextQuestion()
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="mb-2 flex gap-2 text-xs text-gray-400">
        <span>{question.question_type.replace('_', ' ')}</span>
        <span>·</span>
        <span>{question.difficulty}</span>
      </div>

      <p className="text-lg font-medium text-gray-800 mb-6">{question.question_text}</p>

      {question.question_type === 'multiple_choice' && (
        <MultipleChoice
          choices={question.answer_choices}
          selected={selected}
          onChange={setSelected}
          disabled={submitted}
        />
      )}

      {!submitted && (
        <button
          onClick={handleSubmit}
          disabled={selected === null}
          className="mt-6 w-full bg-blue-600 text-white rounded-xl py-3 font-semibold hover:bg-blue-700 disabled:opacity-40"
        >
          Submit Answer
        </button>
      )}

      {submitted && result && (
        <div className={`mt-4 rounded-xl p-4 ${result.correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <p className={`font-semibold ${result.correct ? 'text-green-700' : 'text-red-700'}`}>
            {result.correct ? 'Correct!' : 'Incorrect'}
          </p>
          {result.hint && !examMode && (
            <p className="text-sm text-gray-600 mt-2"><span className="font-medium">Hint:</span> {result.hint}</p>
          )}
          {result.explanation && !examMode && (
            <p className="text-sm text-gray-600 mt-2">{result.explanation}</p>
          )}
          {(result.correct || result.attempt_number >= 2 || examMode) && (
            <button
              onClick={handleNext}
              className="mt-4 w-full bg-gray-800 text-white rounded-xl py-2 font-semibold hover:bg-gray-900"
            >
              Next Question
            </button>
          )}
        </div>
      )}
    </div>
  )
}

function MultipleChoice({ choices, selected, onChange, disabled }) {
  return (
    <div className="space-y-3">
      {choices.map((choice) => (
        <button
          key={choice.id}
          onClick={() => onChange(choice.id)}
          disabled={disabled}
          className={`w-full text-left rounded-xl border px-4 py-3 transition-colors
            ${selected === choice.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
            ${disabled ? 'cursor-default' : 'cursor-pointer'}
          `}
        >
          {choice.text}
        </button>
      ))}
    </div>
  )
}

function buildAnswer(question, selected) {
  if (question.question_type === 'multiple_choice' || question.question_type === 'true_false') {
    return { selected_id: selected }
  }
  if (question.question_type === 'multi_select') {
    return { selected_ids: selected }
  }
  return { answer: selected }
}
