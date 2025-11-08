'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import axios from 'axios'

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

export default function QuizPage() {
  const params = useParams()
  const router = useRouter()
  const contentId = params.id as string
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [answers, setAnswers] = useState<number[]>([])
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [nextQuizId, setNextQuizId] = useState<string | null>(null)

  useEffect(() => {
    // Check if this is a retry
    const urlParams = new URLSearchParams(window.location.search)
    const isRetry = urlParams.get('retry') === 'true'
    
    if (isRetry) {
      // Get retry quiz
      const user_id = 'user_placeholder_id' // TODO: Get from auth
      axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/quiz/content/${contentId}/retry?user_id=${user_id}`)
        .then(response => {
          setQuiz(response.data)
          setAnswers(new Array(response.data.questions.length).fill(-1))
          setNextQuizId(response.data.id)
          setLoading(false)
        })
        .catch(error => {
          console.error('Error fetching retry quiz:', error)
          alert('Retry quiz not available. Please try the original quiz.')
          // Fallback to original quiz
          loadOriginalQuiz()
        })
    } else {
      loadOriginalQuiz()
    }
  }, [contentId])

  const loadOriginalQuiz = () => {
    axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/quiz/content/${contentId}`)
      .then(response => {
        setQuiz(response.data)
        setAnswers(new Array(response.data.questions.length).fill(-1))
        setNextQuizId(null)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching quiz:', error)
        setLoading(false)
      })
  }

  const handleAnswerChange = (questionIndex: number, answerIndex: number) => {
    const newAnswers = [...answers]
    newAnswers[questionIndex] = answerIndex
    setAnswers(newAnswers)
  }

  const handleSubmit = () => {
    if (answers.some(a => a === -1)) {
      alert('Please answer all questions')
      return
    }

    // TODO: Replace with actual user_id from auth
    const user_id = 'user_placeholder_id'

    axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/quiz/content/${contentId}/submit`, {
      user_id,
      answers,
      quiz_id: nextQuizId || quiz?.id  // Use next_quiz_id if retrying, otherwise current quiz id
    })
      .then(response => {
        setResult(response.data)
        setSubmitted(true)
        // Store next_quiz_id for potential retry
        if (response.data.next_quiz_id) {
          setNextQuizId(response.data.next_quiz_id)
        }
      })
      .catch(error => {
        console.error('Error submitting quiz:', error)
        alert('Error submitting quiz')
      })
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
              
              {result?.status === 'retry' && result?.review_hints && (
                <div className="mt-6 p-4 bg-yellow-50 rounded">
                  <h3 className="font-semibold mb-2">Review Hints</h3>
                  {result.review_hints.timestamps && result.review_hints.timestamps.length > 0 && (
                    <p>Re-watch these sections: {result.review_hints.timestamps.join(', ')}</p>
                  )}
                  {result.review_hints.articleHighlights && result.review_hints.articleHighlights.length > 0 && (
                    <p>Re-read these paragraphs: {result.review_hints.articleHighlights.map((h: any) => h.paragraphIndex + 1).join(', ')}</p>
                  )}
                  <button
                    onClick={() => {
                      // Reset state and reload with retry quiz
                      setSubmitted(false)
                      setAnswers([])
                      setResult(null)
                      router.push(`/content/${contentId}/quiz?retry=true`)
                      // Reload the page to fetch retry quiz
                      window.location.reload()
                    }}
                    className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                  >
                    Retry Quiz
                  </button>
                </div>
              )}
              
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


