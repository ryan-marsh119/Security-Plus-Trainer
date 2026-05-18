import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import useUserStore from '../store/userStore'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const { register, isLoading } = useUserStore()
  const navigate = useNavigate()

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await register(form.username, form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registration failed.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-sm p-8 bg-white rounded-2xl shadow">
        <h1 className="text-2xl font-bold mb-6 text-center">Create Account</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {['username', 'email', 'password'].map((field) => (
            <input
              key={field}
              className="w-full border rounded-lg px-4 py-2"
              name={field}
              type={field === 'password' ? 'password' : 'text'}
              placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
              value={form[field]}
              onChange={handleChange}
              required
            />
          ))}
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white rounded-lg py-2 font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Creating…' : 'Create Account'}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-500">
          Already have an account? <Link to="/login" className="text-blue-600">Sign In</Link>
        </p>
      </div>
    </div>
  )
}
