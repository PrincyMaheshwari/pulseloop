'use client'

'use client'

import Link from 'next/link'

const features = [
  { title: 'AI-curated articles', description: 'Stay aligned with the fastest moving industry insights every morning.' },
  { title: 'Interactive knowledge checks', description: 'Adaptive quizzes and exercises generated in under 30 seconds.' },
  { title: 'Actionable analytics', description: 'Track streaks, tech scores, and organisational readiness in real-time.' },
]

export default function Home() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-12 pb-24 md:flex-row md:items-center">
      <div className="flex-1 space-y-6">
        <nav className="flex items-center gap-2 text-xs uppercase tracking-[0.4em] text-[#8fbf7d]">
          <Link href="/" className="hover:text-white">Home</Link>
          <span>•</span>
          <span>Experience</span>
          <span>•</span>
          <span>PulseLoop OS</span>
        </nav>

        <div className="rounded-3xl bg-gradient-to-br from-[#101f18] via-[#12221a] to-[#0b1711] p-10 shadow-2xl shadow-black/40">
          <p className="mb-6 inline-flex rounded-full bg-[#1d2c24] px-4 py-2 text-xs font-semibold tracking-[0.3em] text-[#9FE870] uppercase">
            Web Design
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-white md:text-5xl">
            Elevate your team’s industry intuition with <span className="text-[#9FE870]">PulseLoop</span>
          </h1>
          <p className="mt-5 max-w-2xl text-base text-[#d6e6da]/80 md:text-lg">
            Curated tech, business, and market intelligence—summarised, animated, and packaged with adaptive quizzes so
            your people stay ahead without breaking focus.
          </p>

          <div className="mt-8 flex flex-col gap-4 rounded-2xl border border-white/5 bg-[#0f1b14]/60 p-6 text-sm text-[#d6e6da] md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Choose your vantage point</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Who&apos;s logging in today?</h2>
            </div>
            <div className="flex flex-col gap-3 md:flex-row">
              <Link
                href="/employee"
                className="inline-flex items-center justify-center rounded-full border border-[#9FE870]/50 px-6 py-3 text-sm font-semibold text-[#9FE870] transition hover:bg-[#9FE870] hover:text-[#0B1410] hover:shadow-lg hover:shadow-lime-300/30 focus-visible:bg-[#9FE870] focus-visible:text-[#0B1410] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#9FE870]/50 active:bg-[#9FE870] active:text-[#0B1410]"
              >
                I&apos;m an employee
              </Link>
              <Link
                href="/admin"
                className="inline-flex items-center justify-center rounded-full border border-[#9FE870]/50 px-6 py-3 text-sm font-semibold text-[#9FE870] transition hover:bg-[#9FE870] hover:text-[#0B1410] hover:shadow-lg hover:shadow-lime-300/30 focus-visible:bg-[#9FE870] focus-visible:text-[#0B1410] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#9FE870]/50 active:bg-[#9FE870] active:text-[#0B1410]"
              >
                I oversee learning
              </Link>
            </div>
          </div>
        </div>
      </div>

      <aside className="flex-1 space-y-6 rounded-3xl border border-white/5 bg-[#101d16]/60 p-8 shadow-lg shadow-black/40">
        <div className="rounded-2xl bg-gradient-to-br from-[#24382d] via-[#1b2a23] to-transparent p-6">
          <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Pilot snapshot</p>
          <p className="mt-3 text-2xl font-semibold text-white">57 teams / 4 industries</p>
          <p className="mt-2 text-sm text-[#d6e6da]/80">
            Average streak length jumped from 0.8 to 5.2 days once PulseLoop replaced manual newsletters.
          </p>
        </div>

        <ul className="space-y-6 text-sm text-[#d6e6da]/80">
          {features.map(feature => (
            <li key={feature.title} className="rounded-2xl border border-white/5 bg-[#0f1b14]/70 p-5">
              <p className="text-sm font-semibold text-white">{feature.title}</p>
              <p className="mt-2 text-xs leading-relaxed text-[#d6e6da]/75">{feature.description}</p>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  )
}

