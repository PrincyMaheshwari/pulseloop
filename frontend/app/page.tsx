'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">PulseLoop</h1>
        <p className="text-xl mb-8">Industry Trend Awareness Platform</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link href="/dashboard" className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
            <h2 className="text-2xl font-semibold mb-2">Dashboard</h2>
            <p>View your personalized feed and learning progress</p>
          </Link>
          
          <Link href="/admin" className="p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
            <h2 className="text-2xl font-semibold mb-2">Admin</h2>
            <p>Manage organizations and view analytics</p>
          </Link>
        </div>
      </div>
    </main>
  )
}


