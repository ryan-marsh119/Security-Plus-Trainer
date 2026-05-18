import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import useUserStore from './store/userStore'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import StudySession from './pages/StudySession'
import PracticeExam from './pages/PracticeExam'
import PBQHub from './pages/PBQHub'
import PBQSession from './pages/PBQSession'
import Results from './pages/Results'

function RequireAuth({ children }) {
  const user = useUserStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  const { user, fetchMe } = useUserStore()

  useEffect(() => {
    fetchMe()
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="/study" element={<RequireAuth><StudySession /></RequireAuth>} />
        <Route path="/exam" element={<RequireAuth><PracticeExam /></RequireAuth>} />
        <Route path="/pbq" element={<RequireAuth><PBQHub /></RequireAuth>} />
        <Route path="/pbq/:domainId" element={<RequireAuth><PBQSession /></RequireAuth>} />
        <Route path="/results" element={<RequireAuth><Results /></RequireAuth>} />
        <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  )
}
