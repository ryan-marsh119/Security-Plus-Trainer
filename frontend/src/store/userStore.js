/**
 * store/userStore.js
 *
 * Zustand store for authentication state.
 *
 * State:
 *   user      {object|null} -- UserSerializer data {id, username, email, date_joined}
 *                              null means the user is not authenticated.
 *   isLoading {boolean}     -- true while a login/register request is in flight.
 *
 * Actions:
 *   fetchMe()                        -- Called on app mount to rehydrate auth state
 *                                       from an existing session cookie. Silently
 *                                       sets user to null on 403 (no session).
 *   login(username, password)        -- Authenticates and populates user state.
 *   logout()                         -- Destroys the server session and clears user.
 *   register(username, email, pass)  -- Creates account and logs the user in.
 */

import { create } from 'zustand'
import client from '../api/client'

const useUserStore = create((set) => ({
  user: null,
  isLoading: false,
  // false until the initial fetchMe() settles; route guards wait on this so a
  // page refresh doesn't redirect to /login before the session is restored.
  authChecked: false,

  /**
   * Rehydrates auth state on page load by hitting GET /auth/me/.
   * If no session cookie exists, the 403 is caught and user stays null.
   * Always sets authChecked so route guards can render once this resolves.
   */
  fetchMe: async () => {
    try {
      const { data } = await client.get('/auth/me/')
      set({ user: data })
    } catch {
      set({ user: null })
    } finally {
      set({ authChecked: true })
    }
  },

  /**
   * POSTs credentials to /auth/login/ and stores the returned user object.
   *
   * @param {string} username
   * @param {string} password
   * @throws Axios error on 401 — caller is responsible for catching and
   *         displaying an error message.
   */
  login: async (username, password) => {
    set({ isLoading: true })
    try {
      const { data } = await client.post('/auth/login/', { username, password })
      set({ user: data })
    } finally {
      // Always clear the loading flag, even on a 401 — otherwise the Login
      // button stays disabled and stuck on "Signing in…" after a failed attempt.
      set({ isLoading: false })
    }
  },

  /**
   * POSTs to /auth/logout/, which destroys the Django session, then clears
   * the local user state.
   */
  logout: async () => {
    try {
      await client.post('/auth/logout/')
    } finally {
      // Always clear local user state, even if the logout request fails —
      // otherwise a network hiccup leaves the UI in a logged-in state with a
      // dead session. Clearing locally is the safe default.
      set({ user: null })
    }
  },

  /**
   * Creates a new account via /auth/register/ and logs the user in immediately.
   *
   * @param {string} username
   * @param {string} email     -- optional; pass empty string if not provided
   * @param {string} password  -- minimum 8 characters
   * @throws Axios error on 400 (validation errors) — caller should display them.
   */
  register: async (username, email, password) => {
    set({ isLoading: true })
    try {
      const { data } = await client.post('/auth/register/', { username, email, password })
      set({ user: data })
    } finally {
      // Clear loading on validation errors (400) too, so the button recovers.
      set({ isLoading: false })
    }
  },
}))

export default useUserStore
