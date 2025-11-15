'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import { useApiClient } from '@/lib/api'

type ContentItem = {
  id: string
  title: string
  type: 'article' | 'video' | 'podcast'
  url: string
  description?: string
  published_at: string
  tags?: string[]
  priority_score?: number
}

export default function Dashboard() {
  const api = useApiClient()
  const [feed, setFeed] = useState<ContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [techScore, setTechScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [longestStreak, setLongestStreak] = useState(0)
  const [statusMessage, setStatusMessage] = useState<string | null>(null)

  const loadStats = useCallback(async () => {
    try {
      const data = await api.getJson<{ user: { tech_score?: number; current_streak?: number; longest_streak?: number } }>(
        '/api/me/stats'
      )
      setTechScore(data.user?.tech_score ?? 0)
      setStreak(data.user?.current_streak ?? 0)
      setLongestStreak(data.user?.longest_streak ?? 0)
    } catch (error) {
      console.warn('Unable to fetch user stats', error)
      setTechScore(0)
      setStreak(0)
      setLongestStreak(0)
    }
  }, [api])

  useEffect(() => {
    let cancelled = false
    const loadFeed = async () => {
      try {
        const data = await api.getJson<{ feed: ContentItem[] }>('/api/feed')
        if (!cancelled) {
          setFeed(Array.isArray(data.feed) ? data.feed : [])
        }
      } catch (error) {
        console.warn('Unable to fetch feed.', error)
        if (!cancelled) {
          setFeed([])
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadFeed()
    loadStats()

    return () => {
      cancelled = true
    }
  }, [api, loadStats])

  useEffect(() => {
    const handler = () => {
      loadStats()
    }
    window.addEventListener('focus', handler)
    return () => {
      window.removeEventListener('focus', handler)
    }
  }, [loadStats])

  const heroContent = useMemo(() => feed[0], [feed])

  const handleMarkComplete = useCallback(async () => {
    if (!heroContent) {
      return
    }
    try {
      await api.postJson(`/api/content/${heroContent.id}/complete`, {})
      setStatusMessage('Marked as viewed. Complete the quiz to boost your streak.')
      await loadStats()
    } catch (error) {
      console.error('Unable to mark content complete', error)
      setStatusMessage('Unable to mark content as viewed right now.')
    } finally {
      setTimeout(() => setStatusMessage(null), 3200)
    }
  }, [api, heroContent, loadStats])

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-24">
      <section className="mt-6 flex flex-col gap-6 rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-6 shadow-xl shadow-black/30 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Pulse status</p>
          <h1 className="mt-3 text-3xl font-semibold text-white">Today’s insight, on-point.</h1>
          <p className="mt-2 text-sm text-[#d6e6da]/75">
            One curated briefing and quiz each day is all you need to keep your streak and tech score moving.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <MetricPill label="Tech score" value={techScore} />
          <MetricPill label="Current streak" value={`${streak}d`} />
          <MetricPill label="Longest" value={`${longestStreak}d`} subtle />
        </div>
      </section>

      {statusMessage && (
        <p className="rounded-2xl border border-[#1f3327]/70 bg-[#132118] px-4 py-3 text-sm text-[#9FE870] transition">
          {statusMessage}
        </p>
      )}

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-white/5 bg-[#101d16]/75 p-6 shadow-lg shadow-black/30">
            <header className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Today</p>
                <h2 className="mt-3 text-2xl font-semibold text-white">
                  {loading ? 'Loading your spotlight…' : heroContent?.title ?? 'Fresh insight landing soon'}
                </h2>
              </div>
              {!loading && heroContent && (
                <span className="rounded-full bg-[#1d2c24] px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-[#9FE870]">
                  {heroContent.type}
                </span>
              )}
            </header>

            {!loading && heroContent && (
              <>
                {heroContent.description && (
                  <p className="mt-4 text-sm text-[#d6e6da]/75">{heroContent.description}</p>
                )}
                <div className="mt-4 flex flex-wrap gap-2">
                  {heroContent.tags?.slice(0, 4).map(tag => (
                    <span key={tag} className="rounded-full border border-[#9FE870]/30 bg-[#132118] px-3 py-1 text-xs font-semibold text-[#9FE870]">
                      #{tag}
                    </span>
                  ))}
                  {typeof heroContent.priority_score === 'number' && (
                    <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-[#d6e6da]/70">
                      Priority {(heroContent.priority_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <div className="mt-6 flex flex-wrap gap-3">
                  <a
                    href={`/content/${heroContent.id}`}
                    className="inline-flex items-center rounded-full border border-[#9FE870]/40 px-4 py-2 text-xs font-semibold text-[#9FE870] hover:bg-[#132118]"
                  >
                    Open content
                  </a>
                  <button
                    type="button"
                    onClick={handleMarkComplete}
                    className="inline-flex items-center rounded-full bg-[#9FE870] px-4 py-2 text-xs font-semibold text-[#0B1410] transition hover:scale-[1.02]"
                  >
                    Log session
                  </button>
                </div>
              </>
            )}

            {!loading && !heroContent && (
              <p className="mt-6 text-sm text-[#b4ccbf]/70">
                No assignment yet—check back shortly or ask your admin to tag new sources.
              </p>
            )}
          </div>

          <div className="rounded-3xl border border-white/5 bg-[#0f1b14]/60 p-6 shadow-lg shadow-black/20">
            <header className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Queue</p>
              <span className="text-xs text-[#8fbf7d]/70">
                {loading ? 'Loading…' : `${Math.max(feed.length - 1, 0)} items`}
              </span>
            </header>
            <div className="mt-4 space-y-4">
              {feed.slice(1, 4).map(item => (
                <article
                  key={item.id}
                  className="rounded-2xl border border-white/5 bg-[#101d16]/70 p-5 transition hover:border-[#9FE870]/30"
                >
                  <div className="flex items-center justify-between text-xs text-[#8fbf7d]">
                    <span className="uppercase tracking-[0.25em]">{item.type}</span>
                    <span className="text-[#b4ccbf]/60">
                      {new Date(item.published_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  <h3 className="mt-3 text-base font-semibold text-white">{item.title}</h3>
                  {item.description && (
                    <p className="mt-2 text-xs text-[#b4ccbf]/80">{item.description.substring(0, 120)}…</p>
                  )}
                  <div className="mt-3 flex flex-wrap gap-2">
                    {item.tags?.slice(0, 3).map(tag => (
                      <span key={tag} className="rounded-full border border-[#9FE870]/25 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-[#9FE870]">
                        {tag}
                      </span>
                    ))}
                    {typeof item.priority_score === 'number' && (
                      <span className="rounded-full border border-white/10 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-[#d6e6da]/60">
                        {(item.priority_score * 100).toFixed(0)}% fit
                      </span>
                    )}
                  </div>
                  <a
                    href={`/content/${item.id}`}
                    className="mt-3 inline-flex text-xs font-semibold text-[#9FE870] hover:text-[#bffb9c]"
                  >
                    View →
                  </a>
                </article>
              ))}

              {!loading && feed.slice(1).length === 0 && (
                <p className="rounded-2xl border border-white/5 bg-[#101d16]/60 px-5 py-6 text-sm text-[#b4ccbf]/70">
                  Finish the spotlight to unlock the next set of role-tuned pieces.
                </p>
              )}
            </div>
          </div>
        </div>

        <aside className="space-y-6">
          <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 shadow-lg shadow-black/30">
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Momentum tips</p>
            <ul className="mt-4 space-y-3 text-xs text-[#b4ccbf]/80">
              <li>• Skim the AI summary before diving deep.</li>
              <li>• Capture two takeaways from the quiz explanations.</li>
              <li>• Share one highlight in your team channel.</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 shadow-lg shadow-black/30">
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Tomorrow</p>
            <p className="mt-3 text-sm text-[#d6e6da]/80">
              Expect a short video on sustainable AI infrastructure with a scenario-based follow-up quiz.
            </p>
          </div>

          <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 shadow-lg shadow-black/30">
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Signals</p>
            <ul className="mt-4 space-y-3 text-xs text-[#b4ccbf]/80">
              <li>• Podcast consumption up 12% across your cohort.</li>
              <li>• Adaptive compliance module unlocked two new quizzes.</li>
              <li>• Enable streak nudges to protect your run.</li>
            </ul>
          </div>
        </aside>
      </section>
    </div>
  )
}

function MetricPill({ label, value, subtle }: { label: string; value: number | string; subtle?: boolean }) {
  return (
    <div
      className={`rounded-full border px-4 py-2 text-sm font-medium ${
        subtle
          ? 'border-white/15 bg-transparent text-[#8fbf7d]'
          : 'border-[#9FE870]/40 bg-[#132118] text-[#9FE870]'
      }`}
    >
      <span className="text-xs uppercase tracking-[0.3em]">{label}</span>
      <span className="ml-2 text-base">{value}</span>
    </div>
  )
}

