'use client'

import { useEffect, useMemo, useState } from 'react'

type ContentItem = {
  id: string
  title: string
  type: 'article' | 'video' | 'podcast'
  url: string
  description?: string
  published_at: string
}

export default function Dashboard() {
  const [feed, setFeed] = useState<ContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [techScore, setTechScore] = useState(42)
  const [streak, setStreak] = useState(1)
  const [longestStreak, setLongestStreak] = useState(5)
  const [statusMessage, setStatusMessage] = useState<string | null>(null)

  useEffect(() => {
    const loadFeed = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/feed`, {
          headers: {
            Authorization: 'Bearer placeholder_token',
          },
        })

        if (!response.ok) {
          throw new Error('Failed to load feed')
        }

        const data = await response.json()
        setFeed(Array.isArray(data.feed) ? data.feed : [])
      } catch (error) {
        console.warn('Unable to fetch feed. Using curated samples.', error)
        setFeed([
          {
            id: 'sample-article',
            title: 'How AI observability is reshaping enterprise SRE playbooks',
            type: 'article',
            description:
              'The latest frameworks engineering teams are adopting to keep generative AI products resilient and compliant.',
            url: '#',
            published_at: new Date().toISOString(),
          },
          {
            id: 'sample-video',
            title: 'Lunch & Learn: Architecting data pipelines for multi-cloud analytics',
            type: 'video',
            description:
              'A 9-minute walkthrough of a federated data mesh used by high-performing retail teams in 2025.',
            url: '#',
            published_at: new Date().toISOString(),
          },
        ])
      } finally {
        setLoading(false)
      }
    }

    loadFeed()
  }, [])

  const handleMarkComplete = () => {
    setTechScore(prev => prev + 8)
    setStreak(prev => {
      const next = prev + 1
      if (next > longestStreak) {
        setLongestStreak(next)
      }
      return next
    })
    setStatusMessage('Activity logged! Your streak has been extended.')
    setTimeout(() => setStatusMessage(null), 3200)
  }

  const heroContent = useMemo(() => feed[0], [feed])

  return (
    <div className="mx-auto max-w-6xl pb-24">
      <header className="mb-8 rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-8 shadow-xl shadow-black/30">
        <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Employee dashboard</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">Welcome back to your industry pulse</h1>
        <p className="mt-3 text-sm text-[#d6e6da]/80">
          One completed insight nudges your streak. Finish today&apos;s pick and watch your tech score respond instantly.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-3">
        <StatCard label="Tech score" value={techScore} accent />
        <StatCard label="Current streak" value={`${streak} day${streak === 1 ? '' : 's'}`} />
        <StatCard label="Longest streak" value={`${longestStreak} days`} />
      </div>

      {statusMessage && (
        <p className="mt-4 rounded-xl border border-[#1f3327] bg-[#132118] px-4 py-3 text-sm text-[#9FE870]">
          {statusMessage}
        </p>
      )}

      <section className="mt-10 grid gap-8 md:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-8 shadow-lg shadow-black/30">
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Today&apos;s spotlight</p>
            {loading && <p className="mt-6 animate-pulse text-sm text-[#d6e6da]/70">Loading fresh insights…</p>}

            {!loading && heroContent && (
              <>
                <div className="mt-4 flex flex-wrap items-center gap-3">
                  <span className="rounded-full bg-[#1d2c24] px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-[#9FE870]">
                    {heroContent.type}
                  </span>
                  <span className="text-xs text-[#b4ccbf]/70">
                    {new Date(heroContent.published_at).toLocaleDateString()}
                  </span>
                </div>
                <h2 className="mt-5 text-2xl font-semibold text-white">{heroContent.title}</h2>
                {heroContent.description && (
                  <p className="mt-3 text-sm text-[#d6e6da]/80">{heroContent.description}</p>
                )}
                <div className="mt-6 flex flex-wrap items-center gap-3">
                  <a
                    href={`/content/${heroContent.id}`}
                    className="rounded-full border border-[#9FE870]/40 px-4 py-2 text-xs font-semibold text-[#9FE870] hover:bg-[#132118]"
                  >
                    Open content
                  </a>
                  <button
                    onClick={handleMarkComplete}
                    className="rounded-full bg-[#9FE870] px-4 py-2 text-xs font-semibold text-[#0B1410] transition hover:scale-105"
                  >
                    Mark activity complete
                  </button>
                </div>
              </>
            )}

            {!loading && !heroContent && (
              <p className="mt-4 text-sm text-[#d6e6da]/70">
                We&apos;re preparing new content for you. Check back in a moment.
              </p>
            )}
          </div>

          <div className="rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-8 shadow-lg shadow-black/20">
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">In your queue</p>
            <div className="mt-4 space-y-4">
              {feed.slice(1).map(item => (
                <article key={item.id} className="rounded-2xl border border-white/5 bg-[#101d16]/60 p-5">
                  <div className="flex items-center gap-3 text-xs text-[#8fbf7d]">
                    <span className="uppercase tracking-[0.3em]">{item.type}</span>
                    <span className="text-[#b4ccbf]/60">
                      {new Date(item.published_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                  </div>
                  <h3 className="mt-3 text-lg font-semibold text-white">{item.title}</h3>
                  {item.description && (
                    <p className="mt-2 text-xs text-[#b4ccbf]/80">{item.description.substring(0, 140)}…</p>
                  )}
                  <a
                    href={`/content/${item.id}`}
                    className="mt-4 inline-flex text-xs font-semibold text-[#9FE870] hover:text-[#bffb9c]"
                  >
                    View → 
                  </a>
                </article>
              ))}

              {!loading && feed.slice(1).length === 0 && (
                <p className="text-sm text-[#b4ccbf]/70">
                  Once you finish today&apos;s spotlight we&apos;ll queue additional pieces tailored to your role.
                </p>
              )}
            </div>
          </div>
        </div>

        <aside className="space-y-6">
          <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 shadow-lg shadow-black/30">
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Learning objectives</p>
            <ul className="mt-4 space-y-3 text-xs text-[#b4ccbf]/80">
              <li>• Understand how today’s trend influences your current roadmap.</li>
              <li>• Apply takeaways in a 3-question adaptive quiz to reinforce context.</li>
              <li>• Share highlights with your team from the dashboard once complete.</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 shadow-lg shadow-black/30">
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Upcoming beats</p>
            <p className="mt-3 text-sm text-[#d6e6da]/85">
              Tomorrow we&apos;ll rotate to a short-form video on sustainable AI infrastructure with follow-up micro
              exercises.
            </p>
          </div>
        </aside>
      </section>
    </div>
  )
}

function StatCard({ label, value, accent = false }: { label: string; value: number | string; accent?: boolean }) {
  return (
    <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 shadow-lg shadow-black/30">
      <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">{label}</p>
      <p
        className={`mt-3 text-3xl font-semibold ${
          accent ? 'text-[#9FE870]' : 'text-white'
        }`}
      >
        {value}
      </p>
    </div>
  )
}

