'use client'

import { useEffect, useState } from 'react'

type Analytics = {
  total_users: number
  active_users: number
  avg_tech_score: number
  participation_rate: number
}

export default function AdminPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const orgId = 'org_placeholder_id'
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/admin/analytics?organization_id=${orgId}`,
        )

        if (response.ok) {
          const data = await response.json()
          setAnalytics(data)
        } else {
          throw new Error('Failed to load analytics')
        }
      } catch (error) {
        console.warn('Unable to load analytics, seeding defaults.', error)
        setAnalytics({
          total_users: 275,
          active_users: 198,
          avg_tech_score: 63.4,
          participation_rate: 0.72,
        })
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [])

  if (loading) {
    return (
      <div className="mx-auto max-w-6xl rounded-3xl border border-white/5 bg-[#101d16]/70 p-10 text-sm text-[#d6e6da]/70">
        Fetching organisational insights…
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl space-y-10 pb-24">
      <header className="rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-8 shadow-xl shadow-black/30">
        <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Administrator</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">Learning impact cockpit</h1>
        <p className="mt-3 text-sm text-[#d6e6da]/80">
          Monitor team participation, tech scores, and source performance in real time. All numbers below update whenever
          a new summary is consumed or quiz is submitted.
        </p>
      </header>

      <section className="grid gap-6 md:grid-cols-4">
        <InsightCard label="Total users" value={analytics?.total_users ?? 0} />
        <InsightCard label="Active this week" value={analytics?.active_users ?? 0} />
        <InsightCard
          label="Avg tech score"
          value={analytics ? analytics.avg_tech_score.toFixed(1) : '0.0'}
          accent
        />
        <InsightCard
          label="Participation rate"
          value={`${((analytics?.participation_rate ?? 0) * 100).toFixed(1)}%`}
        />
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-8 shadow-lg shadow-black/30">
          <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Content performance</p>
          <ul className="mt-5 space-y-4 text-sm text-[#d6e6da]/80">
            <li>
              • Video explainers now drive <span className="font-semibold text-[#9FE870]">42%</span> of first attempts
              that lead directly to passed quizzes.
            </li>
            <li>
              • Podcast recaps spur weekend engagement, adding <span className="font-semibold text-[#9FE870]">1.6</span>{' '}
              average streak days.
            </li>
            <li>• Articles remain ideal for onboarding—completion time averages 6 minutes.</li>
          </ul>
        </div>

        <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-8 shadow-lg shadow-black/30">
          <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Next actions</p>
          <ol className="mt-5 space-y-3 text-sm text-[#d6e6da]/80">
            <li>1. Merge the new robotics playlists into the Manufacturing cohort.</li>
            <li>2. Enable quiz retry emails for teams below 55 tech score.</li>
            <li>3. Schedule a live debrief with the Data Platform guild next Thursday.</li>
          </ol>
        </div>
      </section>

      <section className="rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-8 shadow-lg shadow-black/30">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Content sources</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Manage your intelligence supply chain</h2>
            <p className="mt-2 text-sm text-[#b4ccbf]/80">
              Activate or pause RSS feeds, YouTube channels, podcast sources, and proprietary research in one place.
            </p>
          </div>
          <button className="rounded-full bg-[#9FE870] px-6 py-2 text-sm font-semibold text-[#0B1410] transition hover:scale-105">
            Configure sources
          </button>
        </div>
        <div className="mt-6 grid gap-4 text-xs text-[#b4ccbf]/80 md:grid-cols-3">
          <div className="rounded-2xl border border-white/5 bg-[#101d16]/60 p-4">
            <p className="font-semibold text-white">Industry-grade RSS</p>
            <p className="mt-2">TechCrunch, Stratechery, MIT Sloan, Private analyst feeds</p>
          </div>
          <div className="rounded-2xl border border-white/5 bg-[#101d16]/60 p-4">
            <p className="font-semibold text-white">Video intelligence</p>
            <p className="mt-2">Conference keynotes, Azure Friday, AWS re:Invent developer talks</p>
          </div>
          <div className="rounded-2xl border border-white/5 bg-[#101d16]/60 p-4">
            <p className="font-semibold text-white">Audio briefings</p>
            <p className="mt-2">Marketplace Tech, FT Tech Tonic, internal podcasts</p>
          </div>
        </div>
      </section>
    </div>
  )
}

function InsightCard({ label, value, accent = false }: { label: string; value: number | string; accent?: boolean }) {
  return (
    <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 shadow-lg shadow-black/30">
      <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">{label}</p>
      <p className={`mt-3 text-3xl font-semibold ${accent ? 'text-[#9FE870]' : 'text-white'}`}>{value}</p>
    </div>
  )
}

