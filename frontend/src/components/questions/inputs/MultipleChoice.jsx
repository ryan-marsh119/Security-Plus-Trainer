/**
 * components/questions/inputs/MultipleChoice.jsx
 *
 * Radio-style single-select answer choices (multiple_choice / true_false).
 *
 * Props:
 *   choices    {object[]} -- AnswerChoiceSerializer array [{id, text, order}]
 *   selected   {number|null} -- id of the currently selected choice
 *   onChange   {function} -- called with the choice id when user selects one
 *   disabled   {boolean}  -- true after submission; prevents re-selection
 *   correctIds {number[]|undefined} -- when present (question resolved), the
 *               correct choice id(s); those choices render green.
 */
export default function MultipleChoice({ choices, selected, onChange, disabled, correctIds }) {
  const revealing = Array.isArray(correctIds)
  const list = Array.isArray(choices) ? choices : []
  return (
    <div className="space-y-3" role="radiogroup">
      {list.map((choice) => {
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
            type="button"
            role="radio"
            aria-checked={isSelected}
            onClick={() => onChange(choice.id)}
            disabled={disabled}
            className={`w-full flex items-center justify-between gap-3 text-left rounded-xl border px-4 py-3 transition-colors
              ${stateClass}
              ${disabled ? 'cursor-default' : 'cursor-pointer'}
            `}
          >
            <span>{choice.text}</span>
            {/* Non-color cue so the correct answer is conveyed without relying
                on green alone (accessibility). */}
            {isCorrect && (
              <span className="flex-shrink-0 text-green-700 text-sm font-semibold" aria-label="correct answer">
                ✓ correct
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
