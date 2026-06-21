/**
 * components/questions/inputs/MultiSelect.jsx
 *
 * Checkbox-style multi-select choices (multi_select). Tracks an array of
 * selected choice ids; clicking a choice toggles its membership.
 *
 * Props:
 *   choices    {object[]} -- AnswerChoiceSerializer array [{id, text, order}]
 *   selected   {number[]} -- ids of the currently selected choices
 *   onChange   {function} -- called with the new id array on toggle
 *   disabled   {boolean}  -- true after submission; prevents re-selection
 *   correctIds {number[]|undefined} -- when present (question resolved), the
 *               correct choice ids; those choices render green.
 */
export default function MultiSelect({ choices, selected, onChange, disabled, correctIds }) {
  // Guard: never assume `selected` is an array (defensive backstop in case a
  // parent ever passes a stale non-array value mid-transition).
  const selectedIds = Array.isArray(selected) ? selected : []
  const list = Array.isArray(choices) ? choices : []
  const revealing = Array.isArray(correctIds)
  const toggle = (id) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((x) => x !== id))
    } else {
      onChange([...selectedIds, id])
    }
  }

  return (
    <div className="space-y-3">
      {list.map((choice) => {
        const isChecked = selectedIds.includes(choice.id)
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
            type="button"
            role="checkbox"
            aria-checked={isChecked}
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
            {isCorrect && (
              <span className="ml-auto flex-shrink-0 text-green-700 text-sm font-semibold" aria-label="correct answer">
                correct
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
