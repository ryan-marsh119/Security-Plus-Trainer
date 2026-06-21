/**
 * App.jsx
 *
 * Root component. Sets up React Router and calls fetchMe() on mount so the
 * app can restore auth state from an existing session cookie without forcing
 * the user to log in again after a page refresh.
 *
 * Route structure:
 *   /login          -- public
 *   /register       -- public
 *   /dashboard      -- requires auth
 *   /study          -- requires auth; starts a study-mode session
 *   /exam           -- requires auth; starts a timed exam-mode session
 *   /pbq            -- requires auth; PBQ domain selector hub
 *   /pbq/:domainId  -- requires auth; PBQ practice for a specific domain
 *                      (domainId can be 'all' for cross-domain)
 *   /results        -- requires auth; displays score after session completion
 *   *               -- redirects to /dashboard (authenticated) or /login (not)
 */

import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import useUserStore from './store/userStore'
import client from './api/client'
import ErrorBoundary from './components/ErrorBoundary'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Domains from './pages/Domains'
import StudySession from './pages/StudySession'
import PracticeExam from './pages/PracticeExam'
import PBQHub from './pages/PBQHub'
import PBQSession from './pages/PBQSession'
import Results from './pages/Results'

/**
 * Route guard — redirects unauthenticated users to /login.
 * Waits for the initial fetchMe() to settle (authChecked) so a page refresh
 * doesn't bounce a logged-in user to /login before the session is restored.
 *
 * @param {object} props
 * @param {ReactNode} props.children -- the protected page component
 */
function RequireAuth({ children }) {
  const user = useUserStore((s) => s.user)
  const authChecked = useUserStore((s) => s.authChecked)
  if (!authChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading…</p>
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const { user, fetchMe } = useUserStore()

  // On every full page load: seed the CSRF cookie, then restore session from
  // cookie. Mount-only; fetchMe is a stable Zustand action.
  useEffect(() => {
    client.get('/auth/csrf/').finally(fetchMe)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <ErrorBoundary>
      <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/domains" element={<RequireAuth><Domains /></RequireAuth>} />
        <Route path="/study" element={<RequireAuth><StudySession /></RequireAuth>} />
        <Route path="/exam" element={<RequireAuth><PracticeExam /></RequireAuth>} />
        <Route path="/pbq" element={<RequireAuth><PBQHub /></RequireAuth>} />
        <Route path="/pbq/:domainId" element={<RequireAuth><PBQSession /></RequireAuth>} />
        <Route path="/results" element={<RequireAuth><Results /></RequireAuth>} />
        <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} replace />} />
      </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
