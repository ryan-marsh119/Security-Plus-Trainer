/**
 * components/questions/QuestionWrapper.jsx
 *
 * Container for a single question: owns the answer→feedback state and dispatches
 * to the right input component per question_type. The input renderers
 * (MultipleChoice / MultiSelect / Ordering), the feedback panel, and the pure
 * answer helpers were extracted into sibling modules so each is independently
 * testable; this file is the orchestration layer only.
 *
 * Two-strike hint system:
 *   - First wrong attempt  → shows hint, allows retry
 *   - Second wrong attempt → shows explanation, shows "Next Question"
 *   - Correct answer       → shows explanation, shows "Next Question"
 *   - Exam mode            → suppresses all hints and explanations
 *
 * Choice order is SHUFFLED (see computeDisplayChoices) for every type except
 * true_false. Correct-answer reveal: when the server includes correct_ids /
 * correct_order in the answer response (gated server-side so it can't leak
 * before the second attempt in study/pbq), the correct option(s) render green.
 *
 * Props:
 *   question  {object}  -- QuestionSerializer output from the API
 *   examMode  {boolean} -- when true, hints/explanations are hidden (default: false)
 */

import { useState } from 'react'
import useSessionStore from '../../store/sessionStore'
import {
  SUPPORTED_TYPES,
  computeDisplayChoices,
  initialSelection,
  hasSelection,
  buildAnswer,
} from './answerLogic'
import MultipleChoice from './inputs/MultipleChoice'
import MultiSelect from './inputs/MultiSelect'
import Ordering from './inputs/Ordering'
import QuestionFeedback from './QuestionFeedback'

export default function QuestionWrapper({ question, examMode = false }) {
  // displayChoices: answer choices in the (possibly shuffled) order shown to the
  // user. Held in state — not useMemo — so the shuffle is stable across
  // re-renders within the same question (no jumping on each keystroke).
  const [displayChoices, setDisplayChoices] = useState(() => computeDisplayChoices(question))
  // selected: the value the user has chosen but not yet submitted (shape varies
  // by question_type — see initialSelection).
  const [selected, setSelected] = useState(() => initialSelection(question, displayChoices))
  // submitted: true after the user clicks Submit; locks the choice UI.
  const [submitted, setSubmitted] = useState(false)
  // result: the SessionAnswerView response, or null before submission.
  const [result, setResult] = useState(null)
  // Tracks which question the local state currently belongs to.
  const [activeId, setActiveId] = useState(question.id)
  const { submitAnswer, fetchNextQuestion } = useSessionStore()

  // Reset local state DURING render whenever the question changes. This must
  // happen in render, not a useEffect: an effect runs after children render, so
  // the first render of a new ordering/multi_select question would pass the
  // PREVIOUS question's `selected` (often null) into a child and crash on
  // .map()/.includes(). Resetting here keeps `selected` in sync with the
  // current question_type before any child renders.
  if (activeId !== question.id) {
    const dc = computeDisplayChoices(question)
    setActiveId(question.id)
    setDisplayChoices(dc)
    setSelected(initialSelection(question, dc))
    setSubmitted(false)
    setResult(null)
  }

  /**
   * Submits the selected answer and stores the feedback response. No-op if
   * nothing is selected or the submit fails (the store records the error and
   * the UI stays interactive rather than locking).
   */
  const handleSubmit = async () => {
    if (!hasSelection(question, selected)) return
    try {
      const res = await submitAnswer(buildAnswer(question, selected))
      if (!res) return // store recorded an error; stay on the question
      setResult(res)
      setSubmitted(true)
    } catch {
      // submitAnswer already set the store error; nothing else to do here.
    }
  }

  /** Loads the next question (state resets in render when question.id changes). */
  const handleNext = () => {
    fetchNextQuestion()
  }

  /** Clears feedback and re-enables choices for a second attempt (two-strike). */
  const handleRetry = () => {
    setSelected(initialSelection(question, displayChoices))
    setSubmitted(false)
    setResult(null)
  }

  const isSupported = SUPPORTED_TYPES.has(question.question_type)
  const type = question.question_type

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      {/* Question metadata badge */}
      <div className="mb-2 flex gap-2 text-xs text-gray-400">
        <span>{type.replaceAll('_', ' ')}</span>
        <span>·</span>
        <span>{question.difficulty}</span>
      </div>

      <p className="text-lg font-medium text-gray-800 mb-6">{question.question_text}</p>

      {/* Type-specific input */}
      {(type === 'multiple_choice' || type === 'true_false') && (
        <MultipleChoice
          choices={displayChoices}
          selected={selected}
          onChange={setSelected}
          disabled={submitted}
          correctIds={result?.correct_ids}
        />
      )}

      {type === 'multi_select' && (
        <MultiSelect
          choices={displayChoices}
          selected={selected}
          onChange={setSelected}
          disabled={submitted}
          correctIds={result?.correct_ids}
        />
      )}

      {type === 'ordering' && (
        <Ordering
          choices={displayChoices}
          order={selected}
          onChange={setSelected}
          disabled={submitted}
          correctOrder={result?.correct_order}
        />
      )}

      {/* Unsupported type (drag_drop / fill_blank / pbq_simulation): no input is
          wired yet, so offer a Skip so the session can't dead-end. */}
      {!isSupported && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
          <p className="text-sm text-amber-800">
            This question type ({type.replaceAll('_', ' ')}) isn’t supported yet.
          </p>
          <button
            type="button"
            onClick={handleNext}
            className="mt-3 w-full bg-gray-800 text-white rounded-xl py-2 font-semibold hover:bg-gray-900"
          >
            Skip Question
          </button>
        </div>
      )}

      {/* Submit button — only for supported types, hidden after submission */}
      {isSupported && !submitted && (
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!hasSelection(question, selected)}
          className="mt-6 w-full bg-blue-600 text-white rounded-xl py-3 font-semibold hover:bg-blue-700 disabled:opacity-40"
        >
          Submit Answer
        </button>
      )}

      {/* Feedback panel — shown after submission */}
      {submitted && (
        <QuestionFeedback
          result={result}
          examMode={examMode}
          onRetry={handleRetry}
          onNext={handleNext}
        />
      )}
    </div>
  )
}
