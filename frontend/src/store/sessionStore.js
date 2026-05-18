import { create } from 'zustand'
import client from '../api/client'

const useSessionStore = create((set, get) => ({
  session: null,
  currentQuestion: null,
  attemptNumber: 0,
  lastResult: null,

  startSession: async (sessionType, domainId = null) => {
    const payload = { session_type: sessionType }
    if (domainId) payload.domain_filter = domainId
    const { data } = await client.post('/sessions/', payload)
    set({ session: data, currentQuestion: null, attemptNumber: 0, lastResult: null })
    await get().fetchNextQuestion()
  },

  fetchNextQuestion: async () => {
    const { session } = get()
    if (!session) return
    const { data } = await client.get(`/sessions/${session.id}/next/`)
    set({ currentQuestion: data, attemptNumber: 0, lastResult: null })
  },

  submitAnswer: async (answer) => {
    const { session, currentQuestion } = get()
    const { data } = await client.post(`/sessions/${session.id}/answers/`, {
      question_id: currentQuestion.id,
      answer,
    })
    set({ lastResult: data, attemptNumber: data.attempt_number })
    return data
  },

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
