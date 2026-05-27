import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../services/api'

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

export default function ExamResultPage() {
  const { id, aid } = useParams()
  const [result, setResult] = useState(null)
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadResult() {
      setLoading(true)
      setError('')
      try {
        const { data } = await api.get(`/exams/${id}/result/${aid}`)
        if (cancelled) return
        setResult(data)
        const questionIds = Object.keys(data.answers || {}).map((qid) => Number(qid))
        const questionResponses = await Promise.all(questionIds.map((qid) => api.get(`/questions/${qid}`)))
        if (cancelled) return
        setQuestions(questionResponses.map((response) => response.data))
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load exam result.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    loadResult()
    return () => {
      cancelled = true
    }
  }, [id, aid])

  const questionMap = useMemo(() => {
    return questions.reduce((map, question) => {
      map[question.id] = question
      return map
    }, {})
  }, [questions])

  if (loading) return <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-slate-500">Loading exam result...</div>
  if (error) return <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-rose-600">{error}</div>
  if (!result) return null

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-3xl font-bold text-slate-900">Exam result</h1>
        <p className="mt-3 text-slate-600">Your score and question-by-question breakdown.</p>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Score</p>
            <p className="mt-3 text-3xl font-semibold text-slate-900">{result.score} / {result.total_marks}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Time</p>
            <p className="mt-3 text-3xl font-semibold text-slate-900">{formatTime(result.time_taken_seconds)}</p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Attempt</p>
            <p className="mt-3 text-3xl font-semibold text-slate-900">#{result.attempt_number}</p>
          </div>
        </div>

        <div className="mt-10 space-y-5">
          {Object.entries(result.answers || {}).map(([questionId, answer]) => {
            const question = questionMap[Number(questionId)]
            return (
              <article key={questionId} className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-semibold text-slate-900">{question ? question.title : `Question ${questionId}`}</p>
                    <p className="text-sm text-slate-500">Your answer</p>
                  </div>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">Question ID {questionId}</span>
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-2xl bg-white p-4 text-sm text-slate-700 shadow-sm">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Submitted answer</p>
                    <p className="mt-2 font-medium text-slate-900">{answer || 'No answer'}</p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 text-sm text-slate-700 shadow-sm">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Correct answer</p>
                    <p className="mt-2 font-medium text-slate-900">{question?.correct_answer ?? 'Unknown'}</p>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      </div>
    </div>
  )
}
