import React, { useEffect, useState } from 'react'
import { getDashboardSummary } from '../services/api'
import { showError } from '../utils/toast'

interface DashboardSummary {
  name: string
  email: string
  recent_orders: number
}

const Profile: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadSummary = async () => {
      setLoading(true)
      try {
        const data = await getDashboardSummary()
        setSummary(data)
      } catch (error) {
        showError('Unable to load profile summary.')
      } finally {
        setLoading(false)
      }
    }

    loadSummary()
  }, [])

  if (loading) {
    return <p className="text-sm text-slate-500">Loading profile...</p>
  }

  return (
    <section className="space-y-4 rounded-lg bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold text-slate-900">Profile</h1>
      {summary ? (
        <div className="space-y-2 text-slate-700">
          <p className="text-sm text-slate-500">Name</p>
          <p>{summary.name}</p>
          <p className="text-sm text-slate-500">Email</p>
          <p>{summary.email}</p>
          <p className="text-sm text-slate-500">Orders this quarter</p>
          <p>{summary.recent_orders}</p>
        </div>
      ) : (
        <p className="text-sm text-slate-500">No profile data available yet.</p>
      )}
    </section>
  )
}

export default Profile
