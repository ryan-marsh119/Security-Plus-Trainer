/**
 * store/sessionStore.js
 *
 * Zustand store that manages the lifecycle of a single study/exam/PBQ session.
 * Wraps the session API endpoints so pages only need to call store actions.
 *
 * State:
 *   session         {object|null} -- ExamSession data {id, session_type, ...}
 *   currentQuestion {object|null} -- QuestionSerializer data for the active question
 *   attemptNumber   {number}      -- 0 before first submit, 1 after first, 2 after second
 *   lastResult      {object|null} -- Last answer response {correct, attempt_number,
 *                                    hint, explanation}
 *
 * Typical session flow:
 *   startSession() → fetchNextQuestion() [auto] → submitAnswer() → fetchNextQuestion()
 *   → ... → completeSession()
 */

import { create } from 'zustand'
import client from '../api/client'

const useSessionStore = create((set, get) => ({
  session: null,
  currentQuestion: null,
  attemptNumber: 0,
  lastResult: null,

  /**
   * Creates a new session on the server and immediately fetches the first question.
   *
   * @param {string} sessionType  -- 'study' | 'exam' | 'pbq'
   * @param {number|null} domainId -- Domain pk to filter questions, or null for all domains
   */
  startSession: async (sessionType, domainId = null) => {
    const payload = { session_type: sessionType }
    if (domainId) payload.domain_filter = domainId
    const { data } = await client.post('/sessions/', payload)
    set({ session: data, currentQuestion: null, attemptNumber: 0, lastResult: null })
    await get().fetchNextQuestion()
  },

  /**
   * Fetches the next question from the server (SM-2 ordered for study mode,
   * random for exam mode). Resets attempt and result state.
   * No-op if there is no active session.
   */
  fetchNextQuestion: async () => {
    const { session } = get()
    if (!session) return
    const { data } = await client.get(`/sessions/${session.id}/next/`)
    set({ currentQuestion: data, attemptNumber: 0, lastResult: null })
  },

  /**
   * Submits an answer for the current question.
   *
   * @param {object} answer -- Shape depends on question_type:
   *                           multiple_choice/true_false: {selected_id: number}
   *                           multi_select:               {selected_ids: number[]}
   *                           ordering:                   {ordered_ids: number[]}
   *                           drag_drop:                  {matches: {item: zone}}
   *                           fill_blank:                 {answers: string[]}
   *
   * @returns {object} result -- {correct, attempt_number, hint, explanation}
   *                             hint is non-null only on the first wrong attempt.
   *                             explanation is non-null after correct or second wrong.
   */
  submitAnswer: async (answer) => {
    const { session, currentQuestion } = get()
    const { data } = await client.post(`/sessions/${session.id}/answers/`, {
      question_id: currentQuestion.id,
      answer,
    })
    set({ lastResult: data, attemptNumber: data.attempt_number })
    return data
  },

  /**
   * Marks the session complete on the server, fetches the final score,
   * then clears session state.
   *
   * @returns {object|null} results -- calculate_score() output
   *                                   {correct, total, percent, by_domain}
   *                                   or null if no session is active.
   */
  completeSession: async () => {
    const { session } = get()
    if (!session) return null
    await client.post(`/sessions/${session.id}/complete/`)
    const { data } = await client.get(`/sessions/${session.id}/results/`)
    set({ session: null, currentQuestion: null })
    return data
  },
}))

export default useSessionStore
