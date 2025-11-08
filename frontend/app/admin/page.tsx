'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

interface Analytics {
  total_users: number
  active_users: number
  avg_tech_score: number
  participation_rate: number
}

export default function AdminPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Replace with actual organization_id
    const organization_id = 'org_placeholder_id'
    
    axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/analytics?organization_id=${organization_id}`)
      .then(response => {
        setAnalytics(response.data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching analytics:', error)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Admin Dashboard</h1>
        
        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">Total Users</h3>
            <p className="text-3xl font-bold text-primary-600">{analytics?.total_users || 0}</p>
          </div>
          
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">Active Users</h3>
            <p className="text-3xl font-bold text-primary-600">{analytics?.active_users || 0}</p>
          </div>
          
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">Avg Tech Score</h3>
            <p className="text-3xl font-bold text-primary-600">{analytics?.avg_tech_score.toFixed(1) || 0}</p>
          </div>
          
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">Participation Rate</h3>
            <p className="text-3xl font-bold text-primary-600">
              {((analytics?.participation_rate || 0) * 100).toFixed(1)}%
            </p>
          </div>
        </div>
        
        {/* Additional admin features would go here */}
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-semibold mb-4">Content Sources</h2>
          <p className="text-gray-600">Manage content sources and organization settings</p>
          {/* TODO: Implement content source management UI */}
        </div>
      </div>
    </main>
  )
}


