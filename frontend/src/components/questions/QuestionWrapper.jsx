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
 * Renders the appropriate input per question_type:
 *   - multiple_choice / true_false → single-select radio buttons
 *   - multi_select                 → checkbox-style multi-select
 *   - ordering                     → drag-and-drop sortable list (@dnd-kit)
 * The remaining types (drag_drop, fill_blank, pbq_simulation) still need
 * their own sub-components wired into the type switch below.
 *
 * Choice order: displayed choices are SHUFFLED (see computeDisplayChoices) for
 * every type except true_false, so correct answers don't cluster in a fixed
 * position and ordering questions aren't served pre-solved.
 *
 * Correct-answer reveal: once a question is resolved the server includes
 * correct_ids / correct_order in the answer response (gated server-side so it
 * can't leak before the second attempt in study/pbq). When present, the correct
 * option(s) are highlighted green.
 *
 * Props:
 *   question  {object}  -- QuestionSerializer output from the API
 *   examMode  {boolean} -- when true, hints/explanations are hidden (default: false)
 */

import { useState } from 'react'
import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
  arrayMove,
  useSortable,
  sortableKeyboardCoordinates,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import useSessionStore from '../../store/sessionStore'
import { shuffle } from '../../utils/shuffle'

export default function QuestionWrapper({ question, examMode = false }) {
  // displayChoices: the answer choices in the (possibly shuffled) order they're
  // shown to the user. Held in state — not useMemo — so the shuffle is stable
  // across re-renders within the same question (no jumping on each keystroke).
  const [displayChoices, setDisplayChoices] = useState(() => computeDisplayChoices(question))
  // selected: the value the user has chosen but not yet submitted.
  //   multiple_choice / true_false → choice id (number) | null
  //   multi_select                 → array of choice ids
  //   ordering                     → array of choice ids in the user's order
  const [selected, setSelected] = useState(() => initialSelection(question, displayChoices))
  // submitted: true after the user clicks Submit; locks the choice UI
  const [submitted, setSubmitted] = useState(false)
  // result: the response from SessionAnswerView {correct, attempt_number, hint,
  //         explanation, correct_ids?, correct_order?}
  const [result, setResult] = useState(null)
  // Tracks which question the local state currently belongs to.
  const [activeId, setActiveId] = useState(question.id)
  const { submitAnswer, fetchNextQuestion } = useSessionStore()

  // Reset local state DURING render whenever the question changes (e.g. after
  // fetchNextQuestion). This must happen in render, not a useEffect: an effect
  // runs after the children render, so the first render of a new ordering /
  // multi_select question would pass the PREVIOUS question's `selected`
  // (often null from a multiple_choice question) into Ordering/MultiSelect and
  // crash on .map()/.includes(). Resetting here keeps `selected` in sync with
  // the current question_type before any child renders.
  if (activeId !== question.id) {
    const dc = computeDisplayChoices(question)
    setActiveId(question.id)
    setDisplayChoices(dc)
    setSelected(initialSelection(question, dc))
    setSubmitted(false)
    setResult(null)
  }

  /**
   * Submits the selected answer to the server and stores the feedback response.
   * No-op if nothing is selected yet.
   */
  const handleSubmit = async () => {
    if (!hasSelection(question, selected)) return
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
    setSelected(initialSelection(question, displayChoices))
    setSubmitted(false)
    setResult(null)
    fetchNextQuestion()
  }

  /**
   * Clears the feedback and re-enables the choices for a second attempt on the
   * SAME question (two-strike rule: retry allowed after the first wrong answer).
   */
  const handleRetry = () => {
    setSelected(initialSelection(question, displayChoices))
    setSubmitted(false)
    setResult(null)
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
      {(question.question_type === 'multiple_choice' || question.question_type === 'true_false') && (
        <MultipleChoice
          choices={displayChoices}
          selected={selected}
          onChange={setSelected}
          disabled={submitted}
          correctIds={result?.correct_ids}
        />
      )}

      {question.question_type === 'multi_select' && (
        <MultiSelect
          choices={displayChoices}
          selected={selected}
          onChange={setSelected}
          disabled={submitted}
          correctIds={result?.correct_ids}
        />
      )}

      {question.question_type === 'ordering' && (
        <Ordering
          choices={displayChoices}
          order={selected}
          onChange={setSelected}
          disabled={submitted}
          correctOrder={result?.correct_order}
        />
      )}

      {/* Submit button — hidden after submission */}
      {!submitted && (
        <button
          onClick={handleSubmit}
          disabled={!hasSelection(question, selected)}
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
          {/* "Try Again" on the first wrong attempt (study/PBQ mode only) */}
          {!result.correct && result.attempt_number < 2 && !examMode && (
            <button
              onClick={handleRetry}
              className="mt-4 w-full bg-blue-600 text-white rounded-xl py-2 font-semibold hover:bg-blue-700"
            >
              Try Again
            </button>
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
 * Renders a list of radio-style answer choice buttons (single selection).
 *
 * Props:
 *   choices    {object[]} -- AnswerChoiceSerializer array [{id, text, order}]
 *   selected   {number|null} -- id of the currently selected choice
 *   onChange   {function} -- called with the choice id when user selects one
 *   disabled   {boolean}  -- true after submission; prevents re-selection
 *   correctIds {number[]|undefined} -- when present (question resolved), the
 *               correct choice id(s); those choices render green.
 */
function MultipleChoice({ choices, selected, onChange, disabled, correctIds }) {
  const revealing = Array.isArray(correctIds)
  return (
    <div className="space-y-3">
      {choices.map((choice) => {
        const isCorrect = revealing && correctIds.includes(choice.id)
        const isSelected = selected === choice.id
        const stateClass = isCorrect
          ? 'border-green-500 bg-green-50'
          : isSelected
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        return (
          <button
            key={choice.id}
            onClick={() => onChange(choice.id)}
            disabled={disabled}
            className={`w-full text-left rounded-xl border px-4 py-3 transition-colors
              ${stateClass}
              ${disabled ? 'cursor-default' : 'cursor-pointer'}
            `}
          >
            {choice.text}
          </button>
        )
      })}
    </div>
  )
}

/**
 * Renders checkbox-style choices for multi_select questions. Tracks an array
 * of selected choice ids; clicking a choice toggles its membership.
 *
 * Props:
 *   choices    {object[]} -- AnswerChoiceSerializer array [{id, text, order}]
 *   selected   {number[]} -- ids of the currently selected choices
 *   onChange   {function} -- called with the new id array on toggle
 *   disabled   {boolean}  -- true after submission; prevents re-selection
 *   correctIds {number[]|undefined} -- when present (question resolved), the
 *               correct choice ids; those choices render green.
 */
function MultiSelect({ choices, selected, onChange, disabled, correctIds }) {
  // Guard: never assume `selected` is an array (defensive backstop in case a
  // parent ever passes a stale non-array value mid-transition).
  selected = Array.isArray(selected) ? selected : []
  const revealing = Array.isArray(correctIds)
  const toggle = (id) => {
    if (selected.includes(id)) {
      onChange(selected.filter((x) => x !== id))
    } else {
      onChange([...selected, id])
    }
  }

  return (
    <div className="space-y-3">
      {choices.map((choice) => {
        const isChecked = selected.includes(choice.id)
        const isCorrect = revealing && correctIds.includes(choice.id)
        const rowClass = isCorrect
          ? 'border-green-500 bg-green-50'
          : isChecked
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-200 hover:border-gray-300'
        const boxClass = isCorrect
          ? 'bg-green-600 border-green-600 text-white'
          : isChecked
            ? 'bg-blue-600 border-blue-600 text-white'
            : 'border-gray-300'
        return (
          <button
            key={choice.id}
            onClick={() => toggle(choice.id)}
            disabled={disabled}
            className={`w-full flex items-center gap-3 text-left rounded-xl border px-4 py-3 transition-colors
              ${rowClass}
              ${disabled ? 'cursor-default' : 'cursor-pointer'}
            `}
          >
            <span
              className={`flex-shrink-0 w-5 h-5 rounded border flex items-center justify-center text-xs ${boxClass}`}
            >
              {isChecked || isCorrect ? '✓' : ''}
            </span>
            <span>{choice.text}</span>
          </button>
        )
      })}
    </div>
  )
}

/**
 * Renders a drag-and-drop sortable list for ordering questions.
 * The current order is held by the parent as an array of choice ids; dragging
 * a row reorders that array.
 *
 * When `correctOrder` is present (question resolved), the sortable list is
 * replaced by a static list showing the correct sequence in green.
 *
 * Props:
 *   choices      {object[]} -- AnswerChoiceSerializer array [{id, text, order}]
 *   order        {number[]} -- choice ids in the user's current order
 *   onChange     {function} -- called with the reordered id array after a drag
 *   disabled     {boolean}  -- true after submission; disables dragging
 *   correctOrder {number[]|undefined} -- the correct id sequence; when present,
 *                 renders the green correct-order reveal instead of the list.
 */
function Ordering({ choices, order, onChange, disabled, correctOrder }) {
  // useSensors must be called unconditionally (rules of hooks) — before the
  // correctOrder early-return below.
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )
  const byId = Object.fromEntries(choices.map((c) => [c.id, c]))
  // Guard: fall back to the served choice order if `order` is ever null/non-array
  // (defensive backstop against a stale value mid-question-transition).
  const ids = Array.isArray(order) ? order : choices.map((c) => c.id)

  // Reveal: show the canonical correct sequence in green.
  if (Array.isArray(correctOrder)) {
    return (
      <div className="space-y-3">
        <p className="text-xs font-medium text-green-700">Correct order:</p>
        {correctOrder.map((id, index) => (
          <div
            key={id}
            className="flex items-center gap-3 rounded-xl border border-green-500 bg-green-50 px-4 py-3"
          >
            <span className="text-green-600 text-sm w-5 select-none">{index + 1}.</span>
            <span className="text-gray-800">{byId[id]?.text ?? ''}</span>
          </div>
        ))}
      </div>
    )
  }

  const handleDragEnd = (event) => {
    const { active, over } = event
    if (!over || active.id === over.id) return
    const oldIndex = ids.indexOf(active.id)
    const newIndex = ids.indexOf(over.id)
    onChange(arrayMove(ids, oldIndex, newIndex))
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        <div className="space-y-3">
          {ids.map((id, index) => (
            <SortableItem
              key={id}
              id={id}
              index={index}
              text={byId[id]?.text ?? ''}
              disabled={disabled}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  )
}

/**
 * A single draggable row within the Ordering list.
 */
function SortableItem({ id, index, text, disabled }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id, disabled })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.6 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3
        ${disabled ? 'cursor-default' : 'cursor-grab active:cursor-grabbing hover:border-gray-300'}`}
    >
      <span className="text-gray-400 select-none">☰</span>
      <span className="text-gray-400 text-sm w-5 select-none">{index + 1}.</span>
      <span className="text-gray-800">{text}</span>
    </div>
  )
}

/**
 * Returns the display-order choices for a question. Shuffled for every type
 * except true_false (which keeps its natural True/False order). For ordering,
 * the served order IS the answer key, so we reshuffle once if the shuffle
 * happens to reproduce the served order — the user should never be handed the
 * answer pre-solved.
 *
 * @param {object} question -- QuestionSerializer output
 * @returns {object[]} the answer_choices array in display order (new array)
 */
function computeDisplayChoices(question) {
  const choices = question.answer_choices
  if (question.question_type === 'true_false') return choices
  if (question.question_type === 'ordering') {
    let shuffled = shuffle(choices)
    if (choices.length > 1 && sameOrder(shuffled, choices)) {
      shuffled = shuffle(choices)
    }
    return shuffled
  }
  return shuffle(choices)
}

/**
 * True if two choice arrays are in the same id order.
 */
function sameOrder(a, b) {
  return a.length === b.length && a.every((c, i) => c.id === b[i].id)
}

/**
 * Returns the initial `selected` state for a fresh question, by type.
 *   multiple_choice / true_false → null (nothing chosen)
 *   multi_select                 → [] (no boxes checked)
 *   ordering                     → choice ids in their DISPLAY (shuffled) order
 *
 * @param {object}   question       -- QuestionSerializer output
 * @param {object[]} displayChoices -- choices in display order (from computeDisplayChoices)
 */
function initialSelection(question, displayChoices) {
  if (question.question_type === 'multi_select') return []
  if (question.question_type === 'ordering') {
    return displayChoices.map((c) => c.id)
  }
  return null
}

/**
 * Whether the user has made a submittable selection for this question type.
 * Drives the Submit button's disabled state.
 */
function hasSelection(question, selected) {
  if (question.question_type === 'multi_select') {
    return Array.isArray(selected) && selected.length > 0
  }
  if (question.question_type === 'ordering') {
    // The list is always fully populated, so an order is always submittable.
    return Array.isArray(selected) && selected.length > 0
  }
  return selected !== null
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
  if (question.question_type === 'ordering') {
    return { ordered_ids: selected }
  }
  return { answer: selected }
}
