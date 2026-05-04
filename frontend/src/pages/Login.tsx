import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../services/auth'
import { showError } from '../utils/toast'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [serverError, setServerError] = useState('')

  const handleChange = (field: keyof typeof credentials) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials((prev) => ({ ...prev, [field]: event.target.value }))
    setServerError('')
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    try {
      await login(credentials)
      navigate('/products')
    } catch (error: unknown) {
      if ((error as { response?: { status: number; data?: { detail?: string } } }).response?.status === 401) {
        setServerError('Invalid credentials provided.')
      } else {
        showError('Unable to log in. Please try again later.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold">Log in</h1>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg bg-white p-6 shadow-sm">
        <div>
          <label className="block text-sm font-medium text-slate-700">Username or email</label>
          <input
            value={credentials.username}
            onChange={handleChange('username')}
            className="mt-1 w-full rounded-md border border-slate-200 p-2 focus:border-slate-400 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            value={credentials.password}
            onChange={handleChange('password')}
            className="mt-1 w-full rounded-md border border-slate-200 p-2 focus:border-slate-400 focus:outline-none"
          />
        </div>
        {serverError && <p className="text-xs text-rose-600">{serverError}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-slate-900 px-4 py-2 text-white disabled:opacity-60"
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </section>
  )
}

export default Login
