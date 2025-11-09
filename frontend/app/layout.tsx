import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'], weight: ['400', '500', '600', '700'] })

export const metadata: Metadata = {
  title: 'PulseLoop - Industry Trend Awareness',
  description: 'Stay updated on industry trends with AI-curated content',
}

const navLinks = [
  { label: 'Work', href: '/' },
  { label: 'Services', href: '/' },
  { label: 'Subscriptions', href: '/' },
  { label: 'Pricing', href: '/' },
  { label: 'About us', href: '/' },
  { label: 'Use Cases', href: '/' },
  { label: 'Resources', href: '/' },
]

function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 backdrop-blur bg-black/10 border-b border-white/5">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 md:px-10">
        <Link href="/" className="flex items-center gap-3">
          <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[#9FE870] to-[#67D76E] shadow-lg">
            <span className="block h-4 w-4 rotate-45 rounded-sm bg-[#0B1410]" />
          </span>
          <div className="leading-tight">
            <p className="text-lg font-semibold text-white tracking-wide">PulseLoop</p>
            <p className="text-xs uppercase tracking-[0.3em] text-[#9FE870]">Industry IQ</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-8 text-sm font-medium text-[#d2e6d8] md:flex">
          {navLinks.map(link => (
            <Link
              key={link.label}
              href={link.href}
              className="transition hover:text-white"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <div className="flex gap-3 text-xs uppercase tracking-wider text-[#9FE870]">
            <span className="rounded-full border border-[#9FE870]/50 px-3 py-1">57 Projects</span>
            <span className="rounded-full border border-[#9FE870]/50 px-3 py-1">4 Awards</span>
          </div>
          <Link
            href="#"
            className="rounded-full border border-[#9FE870]/50 bg-[#0F1B16]/70 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-green-400/10 transition hover:bg-[#9FE870] hover:text-[#0B1410]"
          >
            Schedule a call
          </Link>
        </div>
      </div>
    </header>
  )
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#07100c] text-[#ecf4ed]`}>
        <div className="min-h-screen bg-gradient-to-br from-[#0b1913] via-[#08140f] to-[#040806] text-[#ecf4ed]">
          <SiteHeader />
          <main className="px-6 pb-20 pt-10 md:px-10">{children}</main>
        </div>
      </body>
    </html>
  )
}


