'use client'

import { useMemo, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'

const PLAN_DETAILS: Record<
  string,
  {
    title: string
    price: string
    description: string
    features: string[]
  }
> = {
  starter: {
    title: 'Starter',
    price: 'USD 1,250 / month',
    description: 'Perfect for pilot teams that want curated insights and quizzes for up to 250 employees.',
    features: [
      '250 seats across 2 departments',
      'Weekly AI-curated highlight packs',
      'Adaptive quizzes with review hints',
      'Email analytics for managers',
    ],
  },
  growth: {
    title: 'Growth',
    price: 'USD 3,400 / month',
    description: 'Scale learning across regions with full automation, transcripts, and analytics integrations.',
    features: [
      '1,200 seats with regional segmentation',
      'Unlimited content sources + Azure transcripts',
      'Animated summaries with ElevenLabs narration',
      'Salesforce and Slack analytics connectors',
    ],
  },
  enterprise: {
    title: 'Enterprise',
    price: 'Custom pricing',
    description: 'Tailored for global rollouts that require advanced security, SSO, and dedicated support.',
    features: [
      'Unlimited seats with role-based pathways',
      'Dedicated knowledge curator & quarterly workshops',
      'SSO, SCIM, and audit logging included',
      'Priority roadmap shaping and white-glove onboarding',
    ],
  },
}

export default function AdminCheckoutPage() {
  const params = useSearchParams()
  const router = useRouter()
  const [processing, setProcessing] = useState(false)
  const [acceptedTerms, setAcceptedTerms] = useState(false)

  const planKey = (params.get('plan') || 'growth').toLowerCase()
  const plan = useMemo(() => PLAN_DETAILS[planKey] ?? PLAN_DETAILS.growth, [planKey])

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (processing || !acceptedTerms) return
    setProcessing(true)

    setTimeout(() => {
      setProcessing(false)
      router.push('/admin?status=checkout-success')
    }, 1500)
  }

  return (
    <div className="mx-auto max-w-5xl pb-24">
      <button
        onClick={() => router.push('/admin')}
        className="mt-8 text-sm text-[#8fbf7d]/80 transition hover:text-[#9FE870]"
      >
        ← Back to admin console
      </button>

      <section className="mt-6 grid gap-8 rounded-3xl border border-white/5 bg-[#0f1b14]/70 p-8 shadow-2xl shadow-black/40 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Secure checkout</p>
            <h1 className="mt-3 text-3xl font-semibold text-white">
              Complete your {plan.title} subscription
            </h1>
            <p className="mt-3 text-sm text-[#d6e6da]/75">
              Payments are processed via a PCI-DSS compliant processor. You can upgrade or downgrade plans anytime from
              the admin console.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="rounded-2xl border border-white/5 bg-[#101d16]/70 p-5">
              <p className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">Billing contact</p>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <Field label="First name" placeholder="Jordan" required />
                <Field label="Last name" placeholder="Rivera" required />
              </div>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <Field type="email" label="Work email" placeholder="jordan@company.com" required />
                <Field label="Company" placeholder="Acme Corp" required />
              </div>
            </div>

            <div className="rounded-2xl border border-white/5 bg-[#101d16]/70 p-5">
              <p className="text-xs uppercase tracking-[0.25em] text-[#8fbf7d]">Payment method</p>
              <div className="mt-4 grid gap-4">
                <Field label="Card number" placeholder="4242 4242 4242 4242" required inputMode="numeric" />
                <div className="grid gap-4 md:grid-cols-2">
                  <Field label="Expiry date" placeholder="MM / YY" required />
                  <Field label="CVC" placeholder="123" required inputMode="numeric" />
                </div>
                <Field label="Billing address" placeholder="123 Market Street" required />
                <div className="grid gap-4 md:grid-cols-3">
                  <Field label="City" placeholder="San Francisco" required />
                  <Field label="State / Region" placeholder="CA" required />
                  <Field label="Postal code" placeholder="94105" required />
                </div>
              </div>
            </div>

            <label className="flex items-start gap-3 text-xs text-[#b4ccbf]/75">
              <input
                type="checkbox"
                checked={acceptedTerms}
                onChange={event => setAcceptedTerms(event.target.checked)}
                className="mt-1 h-4 w-4 rounded border border-white/30 bg-transparent text-[#9FE870] focus:ring-[#9FE870]"
              />
              <span>
                I agree to the <span className="text-[#9FE870]">Master Subscription Agreement</span> and authorize PulseLoop
                to charge the card above for the selected plan.
              </span>
            </label>

            <button
              type="submit"
              disabled={!acceptedTerms || processing}
              className="w-full rounded-full bg-[#9FE870] px-6 py-3 text-sm font-semibold text-[#0B1410] transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:bg-[#9fe870]/40 disabled:text-[#0B1410]/60"
            >
              {processing ? 'Processing payment…' : `Subscribe to ${plan.title}`}
            </button>
          </form>
        </div>

        <aside className="flex h-full flex-col rounded-3xl border border-white/5 bg-[#101d16]/70 p-6">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-[#8fbf7d]">Plan summary</p>
            <h2 className="mt-3 text-2xl font-semibold text-white">{plan.title} plan</h2>
            <p className="mt-2 text-sm text-[#d6e6da]/75">{plan.description}</p>
          </div>

          <div className="mt-6 rounded-2xl border border-[#9FE870]/30 bg-[#132118] p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-[#9FE870]">Billing</p>
            <p className="mt-3 text-3xl font-semibold text-white">{plan.price}</p>
            <p className="mt-2 text-xs text-[#b4ccbf]/70">Billed monthly. Cancel or change plan anytime.</p>
          </div>

          <div className="mt-6 space-y-3 text-xs text-[#b4ccbf]/75">
            {plan.features.map(feature => (
              <p key={feature} className="flex items-start gap-2">
                <span className="mt-1 h-1.5 w-1.5 rounded-full bg-[#9FE870]" />
                <span>{feature}</span>
              </p>
            ))}
          </div>

          <div className="mt-8 rounded-2xl border border-white/5 bg-[#0f1b14]/70 p-5 text-xs text-[#b4ccbf]/70">
            <p className="font-semibold text-white">Need procurement paperwork?</p>
            <p className="mt-2">
              Email <span className="text-[#9FE870]">billing@pulseloop.ai</span> for MSAs, SOC 2 reports, and vendor forms.
            </p>
          </div>
        </aside>
      </section>
    </div>
  )
}

type FieldProps = {
  label: string
  placeholder: string
  required?: boolean
  type?: string
  inputMode?: React.HTMLAttributes<HTMLInputElement>['inputMode']
}

function Field({ label, placeholder, required, type = 'text', inputMode }: FieldProps) {
  return (
    <label className="space-y-2 text-xs text-[#8fbf7d]">
      <span className="tracking-[0.25em] uppercase">{label}</span>
      <input
        type={type}
        placeholder={placeholder}
        required={required}
        inputMode={inputMode}
        className="w-full rounded-xl border border-white/10 bg-[#0a1711] px-4 py-3 text-sm text-white placeholder:text-[#597365] focus:border-[#9FE870] focus:outline-none"
      />
    </label>
  )
}


