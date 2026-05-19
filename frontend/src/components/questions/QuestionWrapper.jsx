/**
 * components/questions/QuestionWrapper.jsx
 *
 * Renders a question card and manages the full answer → feedback loop for
 * a single question. Supports the two-strike hint system:
 *   - First wrong attempt  → shows hint, allows retry
 *   - Second wrong attempt → shows explanation, shows "Next Question"
 *   - Correct answer       → shows explanation, shows "Next Question"
 *   - Exam mode            → suppresses all hints and explanations
 *
 * Currently only renders multiple_choice. Other question_type values
 * (multi_select, ordering, drag_drop, fill_blank, pbq_simulation) will
 * need their own sub-components wired into the type switch below.
 *
 * Props:
 *   question  {object}  -- QuestionSerializer output from the API
 *   examMode  {boolean} -- when true, hints/explanations are hidden (default: false)
 */

import { useState } from 'react'
import useSessionStore from '../../store/sessionStore'

export default function QuestionWrapper({ question, examMode = false }) {
  // selected: the value the user has chosen but not yet submitted
  const [selected, setSelected] = useState(null)
  // submitted: true after the user clicks Submit; locks the choice UI
  const [submitted, setSubmitted] = useState(false)
  // result: the response from SessionAnswerView {correct, attempt_number, hint, explanation}
  const [result, setResult] = useState(null)
  const { submitAnswer, fetchNextQuestion } = useSessionStore()

  /**
   * Submits the selected answer to the server and stores the feedback response.
   * No-op if nothing is selected yet.
   */
  const handleSubmit = async () => {
    if (selected === null) return
    const answer = buildAnswer(question, selected)
    const res = await submitAnswer(answer)
    setResult(res)
    setSubmitted(true)
  }

  /**
   * Resets local state and asks the store to load the next question.
   * Called when the user clicks "Next Question".
   */
  const handleNext = () => {
    setSelected(null)
    setSubmitted(false)
    setResult(null)
    fetchNextQuestion()
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      {/* Question metadata badge */}
      <div className="mb-2 flex gap-2 text-xs text-gray-400">
        <span>{question.question_type.replace('_', ' ')}</span>
        <span>·</span>
        <span>{question.difficulty}</span>
      </div>

      <p className="text-lg font-medium text-gray-800 mb-6">{question.question_text}</p>

      {/* Render the appropriate input component for the question type */}
      {question.question_type === 'multiple_choice' && (
        <MultipleChoice
          choices={question.answer_choices}
          selected={selected}
          onChange={setSelected}
          disabled={submitted}
        />
      )}

      {/* Submit button — hidden after submission */}
      {!submitted && (
        <button
          onClick={handleSubmit}
          disabled={selected === null}
          className="mt-6 w-full bg-blue-600 text-white rounded-xl py-3 font-semibold hover:bg-blue-700 disabled:opacity-40"
        >
          Submit Answer
        </button>
      )}

      {/* Feedback panel — shown after submission */}
      {submitted && result && (
        <div className={`mt-4 rounded-xl p-4 ${result.correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <p className={`font-semibold ${result.correct ? 'text-green-700' : 'text-red-700'}`}>
            {result.correct ? 'Correct!' : 'Incorrect'}
          </p>
          {/* Hint: shown only on first wrong attempt, hidden in exam mode */}
          {result.hint && !examMode && (
            <p className="text-sm text-gray-600 mt-2"><span className="font-medium">Hint:</span> {result.hint}</p>
          )}
          {/* Explanation: shown after correct answer or second wrong attempt */}
          {result.explanation && !examMode && (
            <p className="text-sm text-gray-600 mt-2">{result.explanation}</p>
          )}
          {/* "Next Question" appears once the question is resolved */}
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

/**
 * Renders a list of radio-style answer choice buttons.
 *
 * Props:
 *   choices  {object[]} -- AnswerChoiceSerializer array [{id, text, order}]
 *   selected {number|null} -- id of the currently selected choice
 *   onChange {function}  -- called with the choice id when user selects one
 *   disabled {boolean}   -- true after submission; prevents re-selection
 */
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

/**
 * Converts the UI selection value into the answer dict shape expected by
 * Question.check_answer() on the server.
 *
 * @param {object} question  -- question object with question_type field
 * @param {*}      selected  -- selected value (varies by type)
 * @returns {object} answer dict ready to POST to /sessions/<id>/answers/
 */
function buildAnswer(question, selected) {
  if (question.question_type === 'multiple_choice' || question.question_type === 'true_false') {
    return { selected_id: selected }
  }
  if (question.question_type === 'multi_select') {
    return { selected_ids: selected }
  }
  return { answer: selected }
}
