'use client'

import { useAuth } from '@/lib/auth/auth-provider'

export function AuthStatus() {
  const { isAuthenticated, signOut } = useAuth()

  if (!isAuthenticated) {
    return null
  }

  return (
    <button
      type="button"
      onClick={signOut}
      className="rounded-full border border-[#9FE870]/40 px-4 py-2 text-xs font-semibold text-[#9FE870] transition hover:bg-[#132118]"
    >
      Sign out
    </button>
  )
}


