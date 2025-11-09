'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'

const institutions = [
  'PulseLoop Labs',
  'TechStride University',
  'Northwind Analytics',
  'Globex Solutions',
  'Innova Health Systems',
]

type ContentSummary = {
  id: string
  title: string
  type: 'article' | 'video' | 'podcast'
  url: string
  description?: string
}

type DailyOptionsResponse = {
  article?: ContentSummary | null
  video?: ContentSummary | null
  podcast?: ContentSummary | null
}

export default function EmployeeLanding() {
  const [step, setStep] = useState<'form' | 'learning'>('form')
  const [profile, setProfile] = useState({
    email: '',
    password: '',
    institution: institutions[0],
    jobTitle: '',
  })
  const [content, setContent] = useState<ContentSummary | null>(null)
  const [loadingContent, setLoadingContent] = useState(false)
  const [techScore, setTechScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [quizCompleted, setQuizCompleted] = useState(false)
  const [completionMessage, setCompletionMessage] = useState<string | null>(null)

  const disabled = useMemo(
    () =>
      !profile.email ||
      !profile.password ||
      !profile.jobTitle ||
      !profile.institution ||
      !profile.email.endsWith('.com') && !profile.email.endsWith('.edu'),
    [profile],
  )

  const loadContent = async () => {
    setLoadingContent(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/feed/daily-options`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer placeholder_token',
        },
      })

      if (response.ok) {
        const data: DailyOptionsResponse = await response.json()
        const preferred = data.video ?? data.article ?? data.podcast ?? null
        setContent(
          preferred ?? {
            id: 'sample-1',
            title: 'How edge AI is transforming predictive maintenance in 2025',
            description:
              'A quick primer on deploying lightweight models at the edge to cut downtime by 37% across advanced manufacturing lines.',
            type: 'article',
            url: '#',
          },
        )
      } else {
        fallbackContent()
      }
    } catch (error) {
      console.warn('Unable to load feed; using fallback content.', error)
      fallbackContent()
    } finally {
      setLoadingContent(false)
    }
  }

  const fallbackContent = () =>
    setContent({
      id: 'sample-1',
      title: 'How edge AI is transforming predictive maintenance in 2025',
      description:
        'A quick primer on deploying lightweight models at the edge to cut downtime by 37% across advanced manufacturing lines.',
      type: 'article',
      url: '#',
    })

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (disabled) return
    setStep('learning')
    loadContent()
  }

  const handleCompleteActivity = () => {
    setStreak(prev => prev + 1)
    setTechScore(prev => prev + 12)
    setCompletionMessage('Great work! Your streak just nudged forward.')
    setTimeout(() => setCompletionMessage(null), 3200)
  }

  const handleCompleteQuiz = () => {
    setQuizCompleted(true)
    setTechScore(prev => prev + 18)
    setCompletionMessage('Quiz submitted! We unlocked new recommendations for tomorrow.')
    setTimeout(() => setCompletionMessage(null), 3200)
  }

  return (
    <div className="mx-auto max-w-5xl pb-24">
      <Link href="/" className="text-sm text-[#8fbf7d]/80 transition hover:text-[#9FE870]">
        ← Back to home
      </Link>

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
            <li>• Completing one activity immediately boosts your streak to keep motivation high.</li>
          </ul>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-white/5 bg-[#111f18]/70 p-6">
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
            Create profile & continue
          </button>
        </form>
      </section>

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

              {!loadingContent && content && (
                <div className="mt-6 rounded-2xl border border-white/5 bg-[#0c1912]/80 p-6">
                  <span className="inline-flex items-center rounded-full bg-[#1d2c24] px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-[#9FE870]">
                    {content.type}
                  </span>
                  <h3 className="mt-4 text-xl font-semibold text-white">{content.title}</h3>
                  {content.description && (
                    <p className="mt-3 text-sm text-[#b4ccbf]/80">{content.description}</p>
                  )}
                  <div className="mt-5 flex flex-wrap items-center gap-3">
                    <a
                      href={content.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center rounded-full border border-[#9FE870]/40 px-4 py-2 text-xs font-semibold text-[#9FE870] hover:bg-[#132118]"
                    >
                      Open content
                    </a>
                    <button
                      onClick={handleCompleteActivity}
                      className="inline-flex items-center justify-center rounded-full bg-[#9FE870] px-4 py-2 text-xs font-semibold text-[#0B1410] hover:scale-105"
                    >
                      Mark as complete
                    </button>
                    <button
                      onClick={handleCompleteQuiz}
                      disabled={quizCompleted}
                      className="inline-flex items-center justify-center rounded-full border border-white/15 px-4 py-2 text-xs font-semibold text-white transition hover:border-[#9FE870]/50 disabled:cursor-not-allowed disabled:border-white/5 disabled:text-white/40"
                    >
                      {quizCompleted ? 'Quiz completed' : 'Take the quick quiz'}
                    </button>
                  </div>
                  {completionMessage && (
                    <p className="mt-4 rounded-xl bg-[#13231b] px-4 py-3 text-sm text-[#9FE870]">
                      {completionMessage}
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
                  <StatCard label="Next unlock" value={streak >= 3 ? 'Team leaderboard' : 'Custom playlists'} />
                </div>
              </div>

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


