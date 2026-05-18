import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import useUserStore from '../store/userStore'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, isLoading } = useUserStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch {
      setError('Invalid username or password.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm p-8 bg-white rounded-2xl shadow">
        <h1 className="text-2xl font-bold mb-6 text-center">Security+ Trainer</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            className="w-full border rounded-lg px-4 py-2"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            className="w-full border rounded-lg px-4 py-2"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white rounded-lg py-2 font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          No account? <Link to="/register" className="text-blue-600">Register</Link>
        </p>
      </div>
    </div>
  )
}
