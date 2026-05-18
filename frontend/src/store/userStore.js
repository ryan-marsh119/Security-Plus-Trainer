import { create } from 'zustand'
import client from '../api/client'

const useUserStore = create((set) => ({
  user: null,
  isLoading: false,

  fetchMe: async () => {
    try {
      const { data } = await client.get('/auth/me/')
      set({ user: data })
    } catch {
      set({ user: null })
    }
  },

  login: async (username, password) => {
    set({ isLoading: true })
    const { data } = await client.post('/auth/login/', { username, password })
    set({ user: data, isLoading: false })
  },

  logout: async () => {
    await client.post('/auth/logout/')
    set({ user: null })
  },

  register: async (username, email, password) => {
    set({ isLoading: true })
    const { data } = await client.post('/auth/register/', { username, email, password })
    set({ user: data, isLoading: false })
  },
}))

export default useUserStore
