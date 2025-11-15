'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import Link from 'next/link'

import { useApiClient } from '@/lib/api'

const institutions = [
  'PulseLoop Labs',
  'Salesforce',
  'Snowflake',
  'Databricks',
  'CrowdStrike',
  'ServiceNow',
  'Okta',
  'Atlassian',
  'GitLab',
  'HashiCorp',
  'Rippling',
  'Canva',
  'Notion',
]

type ContentSummary = {
  id: string
  title: string
  type: 'article' | 'video' | 'podcast'
  url: string
  description?: string
  published_at: string
  tags?: string[]
  priority_score?: number
}

type DailyOptionsResponse = {
  article?: ContentSummary | null
  video?: ContentSummary | null
  podcast?: ContentSummary | null
}

export default function EmployeeLanding() {
  const api = useApiClient()
  const [step, setStep] = useState<'form' | 'learning'>('form')
  const [profile, setProfile] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    institution: institutions[0],
    jobTitle: '',
  })
  const [contentItems, setContentItems] = useState<ContentSummary[]>([])
  const [activeContent, setActiveContent] = useState<ContentSummary | null>(null)
  const [loadingContent, setLoadingContent] = useState(false)
  const [techScore, setTechScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [longestStreak, setLongestStreak] = useState(0)
  const [summaryMessage, setSummaryMessage] = useState<string | null>(null)

  const disabled = useMemo(
    () =>
      !profile.firstName ||
      !profile.lastName ||
      !profile.email ||
      !profile.password ||
      !profile.jobTitle ||
      !profile.institution ||
      (!profile.email.endsWith('.com') && !profile.email.endsWith('.edu')),
    [profile],
  )

  const loadStats = useCallback(async () => {
    try {
      const data = await api.getJson<{ user: { tech_score?: number; current_streak?: number; longest_streak?: number } }>(
        '/api/me/stats',
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

  const loadContent = useCallback(async () => {
    setLoadingContent(true)
    setSummaryMessage(null)
    try {
      const data = await api.getJson<DailyOptionsResponse>('/api/feed/daily-options')
      const curated: ContentSummary[] = [data.article, data.video, data.podcast]
        .filter((entry): entry is ContentSummary => Boolean(entry))
        .map(item => ({
          ...item,
          published_at: item.published_at ?? new Date().toISOString(),
        }))

      const items = curated.length ? curated.slice(0, 3) : []
      setContentItems(items)
      setActiveContent(items[0] ?? null)
    } catch (error) {
      console.warn('Unable to load feed.', error)
      setContentItems([])
      setActiveContent(null)
    } finally {
      setLoadingContent(false)
      loadStats()
    }
  }, [api, loadStats])

  useEffect(() => {
    if (step === 'learning') {
      loadStats()
    }
  }, [loadStats, step])

  useEffect(() => {
    const handler = () => {
      if (step === 'learning') {
        loadStats()
      }
    }
    window.addEventListener('focus', handler)
    return () => {
      window.removeEventListener('focus', handler)
    }
  }, [loadStats, step])

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (disabled) return
    setStep('learning')
    loadContent()
  }

  const handleSelectContent = (item: ContentSummary) => {
    setActiveContent(item)
    setSummaryMessage(null)
  }

  const handleGenerateSummary = () => {
    if (!activeContent) return
    setSummaryMessage('Requested DeepSeek summary. We will notify you here once it is ready.')
  }

  return (
    <div className="mx-auto max-w-5xl pb-24">
      <Link href="/" className="text-sm text-[#8fbf7d]/80 transition hover:text-[#9FE870]">
        ← Back to home
      </Link>

      {step === 'form' ? (
        <section className="mt-8 grid gap-8 rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-8 shadow-xl shadow-black/30 md:grid-cols-2">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Employee access</p>
            <h1 className="mt-3 text-3xl font-semibold text-white">Create your learning passport</h1>
            <p className="mt-4 text-sm text-[#d6e6da]/80">
              Use your institution email to unlock curated daily briefings, animated explainers, and adaptive quizzes
              personalised to your role.
            </p>
            <ul className="mt-6 space-y-3 text-xs text-[#b4ccbf]/80">
              <li>• PulseLoop never shares your streak and score outside your organisation.</li>
              <li>• You can switch your role or industry preference anytime from the dashboard.</li>
              <li>• Complete the quiz to boost your streak and unlock next-day insights.</li>
            </ul>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-white/5 bg-[#111f18]/70 p-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">First name</label>
                <input
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
                  placeholder="Jordan"
                  value={profile.firstName}
                  onChange={event => setProfile(prev => ({ ...prev, firstName: event.target.value }))}
                  required
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">Last name</label>
                <input
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
                  placeholder="Rivera"
                  value={profile.lastName}
                  onChange={event => setProfile(prev => ({ ...prev, lastName: event.target.value }))}
                  required
                />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">Institution email</label>
              <input
                type="email"
                className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
                placeholder="you@institution.com"
                value={profile.email}
                onChange={event => setProfile(prev => ({ ...prev, email: event.target.value }))}
                required
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">Create password</label>
              <input
                type="password"
                className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
                placeholder="Minimum 8 characters"
                value={profile.password}
                onChange={event => setProfile(prev => ({ ...prev, password: event.target.value }))}
                required
                minLength={8}
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">Institution</label>
              <select
                className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
                value={profile.institution}
                onChange={event => setProfile(prev => ({ ...prev, institution: event.target.value }))}
              >
                {institutions.map(institution => (
                  <option key={institution} value={institution}>
                    {institution}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">Your role</label>
              <input
                type="text"
                className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
                placeholder="e.g. Cloud Solutions Architect"
                value={profile.jobTitle}
                onChange={event => setProfile(prev => ({ ...prev, jobTitle: event.target.value }))}
                required
              />
            </div>
            <button
              type="submit"
              disabled={disabled}
              className="w-full rounded-full bg-[#9FE870] px-6 py-3 text-sm font-semibold text-[#0B1410] transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:bg-[#9fe870]/40 disabled:text-[#0B1410]/60"
            >
              Create profile &amp; continue
            </button>
          </form>
        </section>
      ) : (
        <section className="mt-8 rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-6 shadow-xl shadow-black/30">
          <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Learning passport created</p>
          <h2 className="mt-3 text-2xl font-semibold text-white">
            Welcome, {profile.firstName} {profile.lastName}!
          </h2>
          <p className="mt-2 text-sm text-[#b4ccbf]/80">
            We’ve pinned content tailored to {profile.jobTitle} at {profile.institution}. Explore today’s feed below and
            complete the quiz to advance your streak.
          </p>
        </section>
      )}

      {step === 'learning' && (
        <section className="mt-12 space-y-8">
          <div className="grid gap-6 md:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-8 shadow-xl shadow-black/30">
              <h2 className="text-2xl font-semibold text-white">Your personalised spotlight</h2>
              <p className="mt-2 text-sm text-[#b4ccbf]/80">
                Based on <span className="font-semibold text-[#9FE870]">{profile.jobTitle}</span> at{' '}
                <span className="font-semibold text-[#9FE870]">{profile.institution}</span>
              </p>

              {loadingContent && (
                <p className="mt-6 animate-pulse text-sm text-[#d6e6da]/70">Curating the sharpest insight for you…</p>
              )}

              {!loadingContent && activeContent && (
                <div className="mt-6 rounded-2xl border border-white/5 bg-[#0c1912]/80 p-6">
                  <span className="inline-flex items-center rounded-full bg-[#1d2c24] px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-[#9FE870]">
                    {activeContent.type}
                  </span>
                  <h3 className="mt-4 text-xl font-semibold text-white">{activeContent.title}</h3>
                  {activeContent.description && (
                    <p className="mt-3 text-sm text-[#b4ccbf]/80">{activeContent.description}</p>
                  )}
                  <div className="mt-4 flex flex-wrap gap-2">
                    {activeContent.tags?.slice(0, 4).map(tag => (
                      <span key={tag} className="rounded-full border border-[#9FE870]/30 bg-[#132118] px-3 py-1 text-xs font-semibold text-[#9FE870]">
                        #{tag}
                      </span>
                    ))}
                    {typeof activeContent.priority_score === 'number' && (
                      <span className="rounded-full border border-white/10 px-3 py-1 text-xs text-[#d6e6da]/70">
                        Priority {(activeContent.priority_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <div className="mt-5 flex flex-wrap items-center gap-3">
                    <a
                      href={activeContent.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center rounded-full border border-[#9FE870]/40 px-4 py-2 text-xs font-semibold text-[#9FE870] hover:bg-[#132118]"
                    >
                      Open content
                    </a>
                    <button
                      type="button"
                      onClick={handleGenerateSummary}
                      className="inline-flex items-center justify-center rounded-full border border-[#9FE870]/40 px-4 py-2 text-xs font-semibold text-[#9FE870] hover:bg-[#132118]"
                    >
                      Generate summary via DeepSeek
                    </button>
                    <Link
                      href={`/content/${activeContent.id}/quiz`}
                      className="inline-flex items-center justify-center rounded-full border border-white/15 px-4 py-2 text-xs font-semibold text-white transition hover:border-[#9FE870]/50"
                    >
                      Take the quiz
                    </Link>
                  </div>
                  {summaryMessage && (
                    <p className="mt-4 rounded-xl bg-[#13231b] px-4 py-3 text-sm text-[#9FE870]">
                      {summaryMessage}
                    </p>
                  )}
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6">
                <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Momentum board</p>
                <div className="mt-4 grid gap-4">
                  <StatCard label="Tech score" value={techScore} suffix="pts" />
                  <StatCard label="Current streak" value={streak} suffix="days" />
                  <StatCard label="Longest streak" value={longestStreak} suffix="days" />
                </div>
              </div>

              <ContentRail items={contentItems} activeId={activeContent?.id ?? undefined} onSelect={handleSelectContent} />

              <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6">
                <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Tomorrow&apos;s preview</p>
                <ul className="mt-4 space-y-3 text-xs text-[#b4ccbf]/80">
                  <li>• Deep dive: Platform engineering patterns for AI-ready infrastructure.</li>
                  <li>• Quick brief: Regulatory heatmap for emerging AI compliance.</li>
                  <li>• Activity: Scenario-based decision tree for a cloud migration sprint.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}

function StatCard({ label, value, suffix }: { label: string; value: number | string; suffix?: string }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-[#0c1912]/80 p-4">
      <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">
        {value}
        {suffix && typeof value === 'number' ? <span className="text-base text-[#8fbf7d]"> {suffix}</span> : null}
      </p>
    </div>
  )
}

function ContentRail({
  items,
  activeId,
  onSelect,
}: {
  items: ContentSummary[]
  activeId?: string
  onSelect: (item: ContentSummary) => void
}) {
  if (!items.length) {
    return (
      <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6 text-sm text-[#b4ccbf]/75">
        Today&apos;s feed is warming up. Check back shortly for fresh drops.
      </div>
    )
  }

  return (
    <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-6">
      <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Today&apos;s feed</p>
      <div className="mt-4 space-y-4">
        {items.map(item => (
          <button
            key={item.id}
            onClick={() => onSelect(item)}
            className={`w-full rounded-2xl border px-4 py-4 text-left text-sm transition ${
              activeId === item.id
                ? 'border-[#9FE870]/60 bg-[#132118]'
                : 'border-white/5 bg-[#101d16]/60 hover:border-[#9FE870]/30'
            }`}
          >
            <div className="flex items-center gap-3 text-xs text-[#8fbf7d]">
              <span className="uppercase tracking-[0.3em]">{item.type}</span>
              <span className="text-[#b4ccbf]/60">
                {new Date(item.published_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
              </span>
            </div>
            <p className="mt-3 text-sm font-semibold text-white">{item.title}</p>
            {item.description && (
              <p className="mt-2 text-xs text-[#b4ccbf]/75">{item.description.substring(0, 140)}…</p>
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
          </button>
        ))}
      </div>
    </div>
  )
}

