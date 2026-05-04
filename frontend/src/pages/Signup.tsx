import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { signup } from '../services/auth'
import { showSuccess, showError } from '../utils/toast'

const validateEmail = (value: string) => /
  ^[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}$
/.test(value)

const Signup: React.FC = () => {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [errors, setErrors] = useState({ name: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const handleChange = (field: keyof typeof form) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }))
    setErrors((prev) => ({ ...prev, [field]: '' }))
  }

  const runValidation = () => {
    const nextErrors = { name: '', email: '', password: '' }
    if (!form.name.trim()) nextErrors.name = 'Name is required.'
    if (!form.email.trim() || !validateEmail(form.email)) nextErrors.email = 'Valid email required.'
    if (form.password.length < 8) nextErrors.password = 'Password must be at least 8 characters.'
    setErrors(nextErrors)
    return !Object.values(nextErrors).some(Boolean)
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!runValidation()) {
      return
    }
    setLoading(true)
    try {
      await signup(form)
      showSuccess('Account created. Please log in.')
      navigate('/login')
    } catch (error) {
      showError('Failed to create account. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="max-w-lg space-y-6">
      <h1 className="text-2xl font-semibold">Create an account</h1>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg bg-white p-6 shadow-sm">
        <div>
          <label className="block text-sm font-medium text-slate-700">Name</label>
          <input
            value={form.name}
            onChange={handleChange('name')}
            className="mt-1 w-full rounded-md border border-slate-200 p-2 focus:border-slate-400 focus:outline-none"
          />
          {errors.name && <p className="mt-1 text-xs text-rose-600">{errors.name}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            value={form.email}
            onChange={handleChange('email')}
            className="mt-1 w-full rounded-md border border-slate-200 p-2 focus:border-slate-400 focus:outline-none"
          />
          {errors.email && <p className="mt-1 text-xs text-rose-600">{errors.email}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            value={form.password}
            onChange={handleChange('password')}
            className="mt-1 w-full rounded-md border border-slate-200 p-2 focus:border-slate-400 focus:outline-none"
          />
          {errors.password && <p className="mt-1 text-xs text-rose-600">{errors.password}</p>}
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-slate-900 px-4 py-2 text-white disabled:opacity-60"
        >
          {loading ? 'Creating account…' : 'Sign up'}
        </button>
      </form>
    </section>
  )
}

export default Signup
