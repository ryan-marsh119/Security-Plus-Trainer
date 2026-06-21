/**
 * components/questions/QuestionFeedback.jsx
 *
 * The post-submission feedback panel: correct/incorrect banner, the two-strike
 * hint/explanation, and the Try Again / Next Question buttons. Pure presentation
 * — all state lives in QuestionWrapper, which passes the answer result here.
 *
 * Props:
 *   result    {object}   -- SessionAnswerView response {correct, attempt_number,
 *                           hint, explanation, ...}
 *   examMode  {boolean}  -- when true, hints/explanations are hidden
 *   onRetry   {function} -- called when the user clicks "Try Again"
 *   onNext    {function} -- called when the user clicks "Next Question"
 */
export default function QuestionFeedback({ result, examMode, onRetry, onNext }) {
  if (!result) return null
  const resolved = result.correct || result.attempt_number >= 2 || examMode
  const canRetry = !result.correct && result.attempt_number < 2 && !examMode

  return (
    <div
      role="status"
      aria-live="polite"
      className={`mt-4 rounded-xl p-4 ${
        result.correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
      }`}
    >
      <p className={`font-semibold ${result.correct ? 'text-green-700' : 'text-red-700'}`}>
        {result.correct ? 'Correct!' : 'Incorrect'}
      </p>
      {/* Hint: shown only on first wrong attempt, hidden in exam mode */}
      {result.hint && !examMode && (
        <p className="text-sm text-gray-600 mt-2">
          <span className="font-medium">Hint:</span> {result.hint}
        </p>
      )}
      {/* Explanation: shown after correct answer or second wrong attempt */}
      {result.explanation && !examMode && (
        <p className="text-sm text-gray-600 mt-2">{result.explanation}</p>
      )}
      {/* "Try Again" on the first wrong attempt (study/PBQ mode only) */}
      {canRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 w-full bg-blue-600 text-white rounded-xl py-2 font-semibold hover:bg-blue-700"
        >
          Try Again
        </button>
      )}
      {/* "Next Question" appears once the question is resolved */}
      {resolved && (
        <button
          type="button"
          onClick={onNext}
          className="mt-4 w-full bg-gray-800 text-white rounded-xl py-2 font-semibold hover:bg-gray-900"
        >
          Next Question
        </button>
      )}
    </div>
  )
}
