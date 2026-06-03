/**
 * utils/shuffle.js
 *
 * Pure array-shuffle helper used to randomize the display order of answer
 * choices so correct answers don't cluster in a fixed position (e.g. always
 * the first N options). Used by QuestionWrapper for multiple_choice,
 * multi_select, and ordering questions (not true_false).
 */

/**
 * Returns a NEW array with the elements of `arr` randomly reordered using the
 * Fisher–Yates algorithm. Does not mutate the input.
 *
 * @param {Array} arr -- the array to shuffle
 * @returns {Array} a new, shuffled array
 */
export function shuffle(arr) {
  const result = [...arr]
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}
