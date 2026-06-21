/**
 * components/questions/answerLogic.js
 *
 * Pure, side-effect-free helpers for the question/answer flow, extracted from
 * QuestionWrapper so they can be unit-tested in isolation (see
 * answerLogic.test.js). None of these touch React state or the network.
 *
 * The answer-payload shapes returned by buildAnswer() are a CROSS-STACK
 * CONTRACT with the backend (Question.check_answer in questions/models.py).
 * Keep them in lockstep — see answerLogic.test.js, which guards the shapes.
 */

import { shuffle } from '../../utils/shuffle'

/** Question types that have a real input renderer in QuestionWrapper. */
export const SUPPORTED_TYPES = new Set([
  'multiple_choice',
  'true_false',
  'multi_select',
  'ordering',
])

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
export function computeDisplayChoices(question) {
  // Defensive: a question without choices (e.g. an unsupported type) must not
  // crash the render. Fall back to an empty list.
  const choices = question.answer_choices ?? []
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
export function sameOrder(a, b) {
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
export function initialSelection(question, displayChoices) {
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
export function hasSelection(question, selected) {
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
 * Question.check_answer() on the server. CROSS-STACK CONTRACT — see module docs.
 *
 * @param {object} question  -- question object with question_type field
 * @param {*}      selected  -- selected value (varies by type)
 * @returns {object} answer dict ready to POST to /sessions/<id>/answers/
 */
export function buildAnswer(question, selected) {
  if (question.question_type === 'multiple_choice' || question.question_type === 'true_false') {
    return { selected_id: selected }
  }
  if (question.question_type === 'multi_select') {
    return { selected_ids: selected }
  }
  if (question.question_type === 'ordering') {
    return { ordered_ids: selected }
  }
  // Unsupported type — there is no valid server payload. The UI never reaches
  // here (unsupported types render a Skip panel, not a Submit button), so this
  // signals a programming error rather than silently POSTing a bad shape that
  // would be scored wrong invisibly (Contract Decision A2).
  throw new Error(`buildAnswer: unsupported question_type "${question.question_type}"`)
}
