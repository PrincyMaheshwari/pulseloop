'use client'

import { useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'

const companies = [
  'Salesforce',
  'Snowflake',
  'Databricks',
  'ServiceNow',
  'CrowdStrike',
  'Okta',
  'Atlassian',
  'GitLab',
  'HashiCorp',
  'Canva',
]

type AdminView = 'selection' | 'auth' | 'dashboard'

type DashboardSnapshot = {
  totalUsers: number
  activeUsers: number
  avgTechScore: number
  participationRate: number
  notes: string[]
  actions: string[]
  sources: string[]
}

const hardcodedSnapshots: Record<string, DashboardSnapshot> = {
  Salesforce: {
    totalUsers: 1780,
    activeUsers: 1314,
    avgTechScore: 72.4,
    participationRate: 0.78,
    notes: [
      'Solution engineers now complete video explainers 2.4x more frequently than written briefings.',
      'Customer success managers request more AI-driven objection handling playbooks.',
      'New hire journey reduced time-to-first-demo by 13%.',
    ],
    actions: [
      'Roll out “Quarterly product pulse” playlist to LATAM cohort.',
      'Enable Slack digest for top underperformed concepts each Friday.',
      'Inject HubSpot integration updates into next week’s pipeline.',
    ],
    sources: [
      'Official Salesforce product launch feeds',
      'Gartner CRM analytics briefings',
      'Field innovation podcast with solution architects',
    ],
  },
  Snowflake: {
    totalUsers: 940,
    activeUsers: 705,
    avgTechScore: 68.9,
    participationRate: 0.75,
    notes: [
      'Data scientists prefer condensed transcripts with schema diagrams.',
      'Sales engineering squads adopted the analytics playlist in 4 geos.',
      'Partner enablement requests surfaced 12 new topics for Q3.',
    ],
    actions: [
      'Add Lakehouse comparison brief into EMEA track.',
      'Map ingestion backlog to the new Azure Marketplace playbook.',
      'Schedule AMA with platform architects after next keynote.',
    ],
    sources: [
      'Snowflake engineering blog RSS',
      'dbt community podcasts',
      'Redshift vs BigQuery benchmark coverage',
    ],
  },
}

export default function AdminPage() {
  const [view, setView] = useState<AdminView>('selection')
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null)
  const [credentials, setCredentials] = useState({ email: '', password: '' })
  const [authError, setAuthError] = useState<string | null>(null)

  const snapshot = useMemo(() => {
    if (!selectedCompany) return null
    return hardcodedSnapshots[selectedCompany] ?? {
      totalUsers: 420,
      activeUsers: 318,
      avgTechScore: 65.1,
      participationRate: 0.68,
      notes: [
        'Video briefings continue to nudge streaks above 4 days.',
        'Leadership requests a curated board-ready summary every Monday.',
        'AI transcripts shorten onboarding by ~15%.',
      ],
      actions: [
        'Tag upcoming product updates to relevant personas.',
        'Launch quarterly executive insight pack.',
        'Enable automated quiz follow-up emails.',
      ],
      sources: [
        'Official newsroom feeds',
        'Industry analyst short form reports',
        'Community podcasts with key customers',
      ],
    } as DashboardSnapshot
  }, [selectedCompany])

  const handleCompanySelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCompany(event.target.value)
    setAuthError(null)
  }

  const handleCredentialSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!credentials.email.endsWith('@pulseloop.ai') && !credentials.email.endsWith('@enterprise.com')) {
      setAuthError('This pilot accepts admin emails ending with @pulseloop.ai or @enterprise.com.')
      return
    }
    setAuthError(null)
    setView('dashboard')
  }

  if (view === 'selection') {
    return (
      <div className="mx-auto max-w-5xl space-y-8 rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-10 shadow-xl shadow-black/30">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Administrator access</p>
          <h1 className="mt-4 text-3xl font-semibold text-white">Select your organisation to continue</h1>
          <p className="mt-3 text-sm text-[#d6e6da]/80">
            Each company workspace loads its own telemetry, credential model, and content source catalog.
          </p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-[#101d16]/70 p-6">
          <label className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Choose company</label>
          <select
            className="mt-3 w-full rounded-xl border border-[#9FE870]/40 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
            value={selectedCompany ?? ''}
            onChange={handleCompanySelect}
          >
            <option value="" disabled>
              Select organisation
            </option>
            {companies.map(company => (
              <option key={company} value={company}>
                {company}
              </option>
            ))}
          </select>
          <button
            disabled={!selectedCompany}
            onClick={() => selectedCompany && setView('auth')}
            className="mt-6 inline-flex w-full items-center justify-center rounded-full bg-[#9FE870] px-6 py-3 text-sm font-semibold text-[#0B1410] transition hover:scale-105 disabled:cursor-not-allowed disabled:bg-[#9fe870]/40"
          >
            Continue
          </button>
        </div>
      </div>
    )
  }

  if (view === 'auth') {
    return (
      <div className="mx-auto max-w-md space-y-6 rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-10 shadow-xl shadow-black/30">
        <button
          onClick={() => setView('selection')}
          className="text-xs text-[#8fbf7d]/80 transition hover:text-[#9FE870]"
        >
          ← Change company
        </button>
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Secure checkpoint</p>
          <h2 className="mt-3 text-2xl font-semibold text-white">{selectedCompany}</h2>
          <p className="mt-2 text-sm text-[#d6e6da]/80">
            Enter your admin credentials to reveal the organisation dashboard.
          </p>
        </div>

        <form onSubmit={handleCredentialSubmit} className="space-y-4">
          <div>
            <label className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Work email</label>
            <input
              type="email"
              className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
              placeholder="you@pulseloop.ai"
              value={credentials.email}
              onChange={event => setCredentials(prev => ({ ...prev, email: event.target.value }))}
              required
            />
          </div>
          <div>
            <label className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Password</label>
            <input
              type="password"
              className="mt-2 w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white focus:border-[#9FE870] focus:outline-none"
              placeholder="8+ characters"
              value={credentials.password}
              onChange={event => setCredentials(prev => ({ ...prev, password: event.target.value }))}
              required
              minLength={8}
            />
          </div>
          {authError && (
            <p className="rounded-xl border border-[#572020] bg-[#2b1010] px-4 py-3 text-xs text-[#ffb5b5]">
              {authError}
            </p>
          )}
          <button
            type="submit"
            className="w-full rounded-full bg-[#9FE870] px-6 py-3 text-sm font-semibold text-[#0B1410] transition hover:scale-[1.02]"
          >
            Authenticate
          </button>
        </form>
      </div>
    )
  }

  if (!snapshot) return null

  return (
    <div className="mx-auto max-w-6xl space-y-10 pb-24">
      <header className="rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-8 shadow-xl shadow-black/30">
        <button
          onClick={() => setView('selection')}
          className="text-xs text-[#8fbf7d]/80 transition hover:text-[#9FE870]"
        >
          ← Switch organisation
        </button>
        <p className="mt-4 text-xs uppercase tracking-[0.3em] text-[#9FE870]">Administrator</p>
        <h1 className="mt-3 text-3xl font-semibold text-white">{selectedCompany} learning cockpit</h1>
        <p className="mt-3 text-sm text-[#d6e6da]/80">
          Hardcoded snapshot to illustrate the analytics experience for {selectedCompany}. All metrics update from your
          actual data stream in production.
        </p>
      </header>

      <section className="grid gap-6 md:grid-cols-4">
        <InsightCard label="Total users" value={snapshot.totalUsers} />
        <InsightCard label="Active this week" value={snapshot.activeUsers} />
        <InsightCard label="Avg tech score" value={snapshot.avgTechScore.toFixed(1)} accent />
        <InsightCard label="Participation rate" value={`${(snapshot.participationRate * 100).toFixed(1)}%`} />
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-8 shadow-lg shadow-black/30">
          <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Signals to watch</p>
          <ul className="mt-5 space-y-4 text-sm text-[#d6e6da]/80">
            {snapshot.notes.map(note => (
              <li key={note}>• {note}</li>
            ))}
          </ul>
        </div>

        <div className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-8 shadow-lg shadow-black/30">
          <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Immediate actions</p>
          <ol className="mt-5 space-y-3 text-sm text-[#d6e6da]/80">
            {snapshot.actions.map((action, index) => (
              <li key={action}>
                {index + 1}. {action}
              </li>
            ))}
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
          {snapshot.sources.map(source => (
            <div key={source} className="rounded-2xl border border-white/5 bg-[#101d16]/60 p-4">
              <p className="font-semibold text-white">{source}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-white/5 bg-[#101d16]/70 p-8 shadow-lg shadow-black/30">
        <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Subscription plans</p>
        <h2 className="mt-3 text-2xl font-semibold text-white">Choose the right scale for {selectedCompany}</h2>
        <p className="mt-2 text-sm text-[#b4ccbf]/80">
          Three tiers tailored to how fast you want to roll out curated learning across the organisation.
        </p>

        <div className="mt-6 grid gap-6 md:grid-cols-3">
          <PlanCard
            title="Starter"
            price="USD 1,250 / month"
            descriptions={[
              'Up to 250 employees across 2 departments',
              '5 curated sources + weekly highlight packs',
              'Adaptive quizzes + streak analytics',
              'Email summaries for managers',
            ]}
          />
          <PlanCard
            title="Growth"
            price="USD 3,400 / month"
            highlight
            descriptions={[
              'Up to 1,200 employees, regional segmentation',
              'Unlimited sources + automated transcripts',
              'Custom AI summaries & animated explainers',
              'Salesforce/Slack integration + BI export',
            ]}
          />
          <PlanCard
            title="Enterprise"
            price="Custom pricing"
            descriptions={[
              'Global rollout with role-based pathways',
              'Dedicated knowledge curator + SSO & SCIM',
              'Voice call briefings & realtime alerts',
              'Quarterly strategy workshops and white-glove onboarding',
            ]}
          />
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

function PlanCard({
  title,
  price,
  descriptions,
  highlight = false,
}: {
  title: string
  price: string
  descriptions: string[]
  highlight?: boolean
}) {
  const router = useRouter()

  const handleSelect = () => {
    const planSlug = title.toLowerCase()
    router.push(`/admin/checkout?plan=${encodeURIComponent(planSlug)}`)
  }

  return (
    <div
      className={`rounded-3xl border bg-[#101d16]/70 p-6 shadow-lg shadow-black/30 ${
        highlight ? 'border-[#9FE870]/60' : 'border-white/5'
      }`}
    >
      <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">{title}</p>
      <p className="mt-3 text-xl font-semibold text-white">{price}</p>
      <ul className="mt-4 space-y-3 text-sm text-[#d6e6da]/80">
        {descriptions.map(line => (
          <li key={line}>• {line}</li>
        ))}
      </ul>
      <button
        onClick={handleSelect}
        className={`mt-6 inline-flex w-full items-center justify-center rounded-full px-4 py-2 text-xs font-semibold transition ${
          highlight
            ? 'bg-[#9FE870] text-[#0B1410] hover:scale-105'
            : 'border border-[#9FE870]/40 text-[#9FE870] hover:bg-[#132118]'
        }`}
      >
        Select plan
      </button>
    </div>
  )
}

