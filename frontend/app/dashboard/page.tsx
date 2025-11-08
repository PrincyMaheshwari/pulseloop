'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

interface ContentItem {
  id: string
  title: string
  type: 'article' | 'video' | 'podcast'
  url: string
  description?: string
  published_at: string
}

interface DashboardData {
  user: {
    tech_score: number
    current_streak: number
    longest_streak: number
  }
  feed: ContentItem[]
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Replace with actual user_id from auth
    const user_id = 'user_placeholder_id'
    
    // Fetch feed
    axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/feed`, {
      headers: {
        'Authorization': 'Bearer placeholder_token'
      }
    })
    .then(response => {
      setDashboard({
        user: {
          tech_score: 0,
          current_streak: 0,
          longest_streak: 0
        },
        feed: response.data.feed || []
      })
      setLoading(false)
    })
    .catch(error => {
      console.error('Error fetching dashboard:', error)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
        
        {/* User Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">Tech Score</h3>
            <p className="text-3xl font-bold text-primary-600">{dashboard?.user.tech_score || 0}</p>
          </div>
          
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">Current Streak</h3>
            <p className="text-3xl font-bold text-primary-600">{dashboard?.user.current_streak || 0} days</p>
          </div>
          
          <div className="p-6 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">Longest Streak</h3>
            <p className="text-3xl font-bold text-primary-600">{dashboard?.user.longest_streak || 0} days</p>
          </div>
        </div>

        {/* Feed */}
        <div className="space-y-4">
          <h2 className="text-2xl font-semibold mb-4">Today's Feed</h2>
          
          {dashboard?.feed.map((item) => (
            <div key={item.id} className="p-6 bg-white rounded-lg shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded text-sm">
                      {item.type}
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(item.published_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  {item.description && (
                    <p className="text-gray-600 mb-4">{item.description.substring(0, 200)}...</p>
                  )}
                  <a
                    href={`/content/${item.id}`}
                    className="text-primary-600 hover:underline"
                  >
                    View Content →
                  </a>
                </div>
              </div>
            </div>
          ))}
          
          {!dashboard?.feed.length && (
            <p className="text-gray-500">No content available. Check back later!</p>
          )}
        </div>
      </div>
    </main>
  )
}


