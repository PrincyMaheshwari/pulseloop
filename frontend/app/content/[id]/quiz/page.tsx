'use client'

import { useCallback, useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'

import { useApiClient } from '@/lib/api'

interface QuizQuestion {
  question: string
  options: string[]
  correct_answer: number
  explanation?: string
}

interface Quiz {
  id: string
  questions: QuizQuestion[]
}

interface QuizSubmitResponse {
  status: string
  correct_count?: number
  wrong_count?: number
  review_hints?: any
  next_quiz_id?: string
  tech_score_change?: number
  tech_score?: number
  current_streak?: number
  longest_streak?: number
}

export default function QuizPage() {
  const api = useApiClient()
  const params = useParams()
  const router = useRouter()
  const contentId = params.id as string
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [answers, setAnswers] = useState<number[]>([])
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState<QuizSubmitResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [nextQuizId, setNextQuizId] = useState<string | null>(null)

  const loadOriginalQuiz = useCallback(async () => {
    try {
      const data = await api.getJson<Quiz>(`/api/quiz/content/${contentId}`)
      setQuiz(data)
      setAnswers(new Array(data.questions.length).fill(-1))
      setNextQuizId(null)
    } catch (error) {
      console.error('Error fetching quiz:', error)
      alert('Unable to load quiz at this time.')
    } finally {
      setLoading(false)
    }
  }, [api, contentId])

  useEffect(() => {
    let cancelled = false

    const initialise = async () => {
      setLoading(true)
      const urlParams = new URLSearchParams(window.location.search)
      const isRetry = urlParams.get('retry') === 'true'

      if (isRetry) {
        try {
          const data = await api.getJson<Quiz>(`/api/quiz/content/${contentId}/retry`)
          if (!cancelled) {
            setQuiz(data)
            setAnswers(new Array(data.questions.length).fill(-1))
            setNextQuizId(data.id)
            setLoading(false)
          }
        } catch (error) {
          console.error('Error fetching retry quiz:', error)
          alert('Retry quiz not available. Loading the original quiz instead.')
          if (!cancelled) {
            await loadOriginalQuiz()
          }
        }
      } else if (!cancelled) {
        await loadOriginalQuiz()
      }
    }

    initialise()

    return () => {
      cancelled = true
    }
  }, [api, contentId, loadOriginalQuiz])

  const handleAnswerChange = (questionIndex: number, answerIndex: number) => {
    const newAnswers = [...answers]
    newAnswers[questionIndex] = answerIndex
    setAnswers(newAnswers)
  }

  const handleSubmit = async () => {
    if (answers.some(a => a === -1)) {
      alert('Please answer all questions')
      return
    }

    try {
      const payload = {
        answers,
        quiz_id: nextQuizId || quiz?.id,
      }
      const data = await api.postJson<QuizSubmitResponse>(`/api/quiz/content/${contentId}/submit`, payload)
      setResult(data)
      setSubmitted(true)
      if (data.next_quiz_id) {
        setNextQuizId(data.next_quiz_id)
      }
    } catch (error) {
      console.error('Error submitting quiz:', error)
      alert('Error submitting quiz')
    }
  }

  if (loading) {
    return <div className="p-8">Loading quiz...</div>
  }

  if (!quiz) {
    return <div className="p-8">Quiz not found</div>
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow p-8">
          <h1 className="text-3xl font-bold mb-8">Quiz</h1>
          
          {!submitted ? (
            <>
              {quiz.questions.map((question, qIndex) => (
                <div key={qIndex} className="mb-8">
                  <h2 className="text-xl font-semibold mb-4">
                    {qIndex + 1}. {question.question}
                  </h2>
                  <div className="space-y-2">
                    {question.options.map((option, oIndex) => (
                      <label
                        key={oIndex}
                        className="flex items-center p-3 border rounded hover:bg-gray-50 cursor-pointer"
                      >
                        <input
                          type="radio"
                          name={`question-${qIndex}`}
                          value={oIndex}
                          checked={answers[qIndex] === oIndex}
                          onChange={() => handleAnswerChange(qIndex, oIndex)}
                          className="mr-3"
                        />
                        {option}
                      </label>
                    ))}
                  </div>
                </div>
              ))}
              
              <button
                onClick={handleSubmit}
                className="w-full px-6 py-3 bg-primary-600 text-white rounded hover:bg-primary-700"
              >
                Submit Quiz
              </button>
            </>
          ) : (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Results</h2>
              <p className="text-lg mb-4">
                Correct: {result?.correct_count || 0} / {quiz.questions.length}
              </p>
              <p className="text-lg mb-4">
                Status: {result?.status === 'passed' ? '✅ Passed' : '❌ Needs Retry'}
              </p>
              {typeof result?.tech_score_change === 'number' && (
                <p className="text-sm text-[#9FE870] mb-2">
                  Tech score change: {result.tech_score_change > 0 ? '+' : ''}
                  {result.tech_score_change}
                </p>
              )}
              {typeof result?.tech_score === 'number' && (
                <p className="text-sm text-[#d6e6da]/80 mb-2">Current tech score: {result.tech_score}</p>
              )}
              {typeof result?.current_streak === 'number' && (
                <p className="text-sm text-[#d6e6da]/80">Current streak: {result.current_streak} days</p>
              )}
              {typeof result?.longest_streak === 'number' && (
                <p className="text-sm text-[#d6e6da]/60">Longest streak: {result.longest_streak} days</p>
              )}
              
              {result?.review_hints &&
                (() => {
                  const isRetry = result.status === 'retry'
                  const containerClass = isRetry
                    ? 'bg-yellow-50 text-[#0b1410]'
                    : 'bg-[#101d16]/70 border border-white/5 text-[#d6e6da]'
                  const labelClass = isRetry ? 'text-sm font-medium text-[#0b1410]' : 'text-sm font-medium text-[#9FE870]'
                  const chipClass = isRetry
                    ? 'rounded-full bg-[#f5d565] px-3 py-1 text-xs font-semibold text-[#4a3a00]'
                    : 'rounded-full bg-[#132118] px-3 py-1 text-xs font-semibold text-[#9FE870]'
                  const bulletClass = isRetry ? 'list-disc space-y-1 pl-5 text-sm text-[#0b1410]' : 'list-disc space-y-1 pl-5 text-sm text-[#d6e6da]'

                  return (
                    <div className={`mt-6 rounded p-4 ${containerClass}`}>
                      <h3 className="font-semibold mb-2">Review Hints</h3>
                      {result.review_hints.timestamps && result.review_hints.timestamps.length > 0 && (
                        <div className="mb-3">
                          <p className={labelClass}>Re-watch these sections:</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {result.review_hints.timestamps.map((ts: string) => (
                              <span key={ts} className={chipClass}>
                                {ts}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {result.review_hints.articleHighlights && result.review_hints.articleHighlights.length > 0 && (
                        <div className="mb-3">
                          <p className={labelClass}>Re-read these paragraphs:</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {result.review_hints.articleHighlights.map((highlight: any, index: number) => {
                              const paragraphIndex =
                                typeof highlight === 'number'
                                  ? highlight
                                  : (highlight?.paragraphIndex ?? highlight) as number
                              return (
                                <span key={`${paragraphIndex}-${index}`} className={chipClass}>
                                  Paragraph {paragraphIndex + 1}
                                </span>
                              )
                            })}
                          </div>
                        </div>
                      )}
                      {result.review_hints.concepts && result.review_hints.concepts.length > 0 && (
                        <div className="mt-2">
                          <p className={labelClass}>Focus on these concepts:</p>
                          <ul className={`mt-2 ${bulletClass}`}>
                            {result.review_hints.concepts.map((concept: string) => (
                              <li key={concept}>{concept}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      <button
                        onClick={() => {
                          setSubmitted(false)
                          setAnswers([])
                          setResult(null)
                          if (result.status === 'retry') {
                            router.push(`/content/${contentId}/quiz?retry=true`)
                            window.location.reload()
                          }
                        }}
                        className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                      >
                        {result.status === 'retry' ? 'Retry Quiz' : 'Review Content'}
                      </button>
                    </div>
                  )
                })()}
              
              <button
                onClick={() => router.push('/dashboard')}
                className="mt-6 px-6 py-3 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Back to Dashboard
              </button>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}


