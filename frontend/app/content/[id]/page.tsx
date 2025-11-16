'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

import { useApiClient } from '@/lib/api'

interface StoryboardStep {
  step: number
  type: string
  title: string
  description: string
}

interface AnimatedSummary {
  storyboard: StoryboardStep[]
  audio_url: string
}

interface ContentItem {
  id: string
  title: string
  type: 'article' | 'video' | 'podcast'
  url: string
  description?: string
  summary?: string
  published_at: string
  animated_summary?: AnimatedSummary
  tags?: string[]
  priority_score?: number
}

export default function ContentPage() {
  const api = useApiClient()
  const params = useParams()
  const contentId = params.id as string
  const [content, setContent] = useState<ContentItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [showSummary, setShowSummary] = useState(false)
  const [animatedSummary, setAnimatedSummary] = useState<AnimatedSummary | null>(null)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [audioPlaying, setAudioPlaying] = useState(false)

  useEffect(() => {
    let cancelled = false
    api
      .getJson<ContentItem>(`/api/content/${contentId}`)
      .then(result => {
        if (!cancelled) {
          setContent(result)
          setLoading(false)
        }
      })
      .catch(error => {
        console.error('Error fetching content:', error)
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [api, contentId])

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  if (!content) {
    return <div className="p-8">Content not found</div>
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/dashboard" className="text-primary-600 hover:underline mb-4 inline-block">
          ← Back to Dashboard
        </Link>
        
        <div className="bg-white rounded-lg shadow p-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded text-sm">
              {content.type}
            </span>
            <span className="text-sm text-gray-500">
              {new Date(content.published_at).toLocaleDateString()}
            </span>
            {typeof content.priority_score === 'number' && (
              <span className="ml-auto rounded-full border border-primary-200 px-3 py-1 text-xs font-semibold text-primary-600">
                Priority {(content.priority_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
          
          <h1 className="text-3xl font-bold mb-4">{content.title}</h1>
          
          {content.description && (
            <p className="text-gray-600 mb-6">{content.description}</p>
          )}

          {content.tags && content.tags.length > 0 && (
            <div className="mb-6 flex flex-wrap gap-2">
              {content.tags.map(tag => (
                <span key={tag} className="rounded-full border border-primary-200 px-3 py-1 text-xs font-semibold text-primary-600">
                  #{tag}
                </span>
              ))}
            </div>
          )}
          
          {/* Content Type Specific Rendering */}
          {content.type === 'article' && (
            <div className="mb-6">
              <a
                href={content.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline"
              >
                Read Full Article →
              </a>
            </div>
          )}
          
          {content.type === 'video' && (
            <div className="mb-6">
              <iframe
                width="100%"
                height="500"
                src={content.url.replace('watch?v=', 'embed/')}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          )}
          
          {content.type === 'podcast' && (
            <div className="mb-6">
              <audio controls className="w-full">
                <source src={content.url} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>
          )}
          
          {/* Animated Summary Button */}
          <button
            onClick={async () => {
              if (!showSummary) {
                setLoadingSummary(true)
                try {
                  const summary = await api.getJson<AnimatedSummary>(`/api/content/${contentId}/summary`)
                  setAnimatedSummary(summary)
                  setShowSummary(true)
                } catch (error: any) {
                  console.error('Error fetching animated summary:', error)
                  const errorMessage = error?.message || 'Error loading animated summary'
                  alert(errorMessage)
                } finally {
                  setLoadingSummary(false)
                }
              } else {
                setShowSummary(false)
                setCurrentStep(0)
                setAudioPlaying(false)
              }
            }}
            className="mb-6 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
            disabled={loadingSummary}
          >
            {loadingSummary ? 'Loading...' : showSummary ? 'Hide' : 'Show'} Animated Summary
          </button>
          
          {showSummary && animatedSummary && (
            <div className="mb-6 p-4 bg-gray-50 rounded">
              <h2 className="text-xl font-semibold mb-4">Animated Summary</h2>
              
              {/* Storyboard Steps */}
              <div className="mb-4 space-y-4">
                {animatedSummary.storyboard.map((step, index) => (
                  <div
                    key={step.step}
                    className={`p-4 rounded border-2 ${
                      index === currentStep
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 bg-white'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold">
                        {step.step}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-1">{step.title}</h3>
                        <p className="text-gray-700">{step.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Audio Player */}
              {animatedSummary.audio_url && (
                <div className="mt-4">
                  <audio
                    src={animatedSummary.audio_url}
                    controls
                    onPlay={() => setAudioPlaying(true)}
                    onPause={() => setAudioPlaying(false)}
                    onEnded={() => setAudioPlaying(false)}
                    className="w-full"
                  />
                </div>
              )}
              
              {/* Navigation Controls */}
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                  disabled={currentStep === 0}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentStep(Math.min(animatedSummary.storyboard.length - 1, currentStep + 1))}
                  disabled={currentStep === animatedSummary.storyboard.length - 1}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
          
          {/* Quiz Link */}
          <Link
            href={`/content/${contentId}/quiz`}
            className="block mt-8 px-6 py-3 bg-primary-600 text-white rounded hover:bg-primary-700 text-center"
          >
            Take Quiz
          </Link>
        </div>
      </div>
    </main>
  )
}


