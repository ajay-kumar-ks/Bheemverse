import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import api from '../../services/api'

const attemptStorageKey = (examId) => `qera_exam_attempt_${examId}`

function formatTimer(seconds) {
  const mins = String(Math.floor(seconds / 60)).padStart(2, '0')
  const secs = String(seconds % 60).padStart(2, '0')
  return `${mins}:${secs}`
}

export default function AttendExamPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [questions, setQuestions] = useState([])
  const [attempt, setAttempt] = useState(null)
  const [answers, setAnswers] = useState({})
  const [remainingSeconds, setRemainingSeconds] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const storageKey = attemptStorageKey(id)

  useEffect(() => {
    let cancelled = false
    let interval = null

    const getStoredAttempt = () => {
      try {
        const raw = sessionStorage.getItem(storageKey)
        return raw ? JSON.parse(raw) : null
      } catch {
        return null
      }
    }

    const saveAttempt = (value) => sessionStorage.setItem(storageKey, JSON.stringify(value))
    const clearStoredAttempt = () => sessionStorage.removeItem(storageKey)

    async function bootstrap() {
      setLoading(true)
      setError('')
      try {
        const [examRes, stored] = await Promise.all([
          api.get(`/exams/${id}`),
          Promise.resolve(getStoredAttempt()),
        ])
        if (cancelled) return

        const examData = examRes.data
        setExam(examData)

        let currentAttempt = stored
        if (!currentAttempt || currentAttempt.examId !== Number(id)) {
          const { data } = await api.post(`/exams/${id}/start`)
          currentAttempt = {
            attemptId: data.id,
            examId: Number(id),
            attemptNumber: data.attempt_number,
            startedAt: Date.now(),
            durationMinutes: examData.duration_minutes,
          }
          saveAttempt(currentAttempt)
        }

        setAttempt(currentAttempt)

        const questionDetails = await Promise.all(
          examData.questions.map((item) => api.get(`/questions/${item.question_id}`)),
        )
        if (cancelled) return
        setQuestions(questionDetails.map((response) => response.data))

        const elapsed = Math.floor((Date.now() - currentAttempt.startedAt) / 1000)
        const remaining = Math.max(0, examData.duration_minutes * 60 - elapsed)
        setRemainingSeconds(remaining)

        if (remaining <= 0) {
          await handleSubmit(currentAttempt, examData, answers, clearStoredAttempt, true)
          return
        }

        interval = setInterval(() => {
          setRemainingSeconds((current) => {
            if (current <= 1) {
              clearInterval(interval)
              return 0
            }
            return current - 1
          })
        }, 1000)
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Unable to load exam session.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    bootstrap()

    return () => {
      cancelled = true
      if (interval) clearInterval(interval)
    }
  }, [id])

  useEffect(() => {
    if (remainingSeconds === 0 && attempt && exam) {
      const stored = sessionStorage.getItem(storageKey)
      if (stored) {
        const currentAttempt = JSON.parse(stored)
        handleSubmit(currentAttempt, exam, answers, () => sessionStorage.removeItem(storageKey), true).catch(() => {})
      }
    }
  }, [remainingSeconds, attempt, exam, answers, storageKey])

  const setAnswer = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
  }

  const handleSubmit = async (currentAttempt, examData, currentAnswers, clearFn, auto = false) => {
    if (!currentAttempt || !examData) return
    if (saving) return
    setSaving(true)
    setError('')
    try {
      const timeTaken = examData.duration_minutes * 60 - remainingSeconds
      const { data } = await api.post(`/exams/${id}/submit`, {
        attempt_id: currentAttempt.attemptId,
        time_taken_seconds: timeTaken,
        answers: Object.fromEntries(
          Object.entries(currentAnswers).map(([question, answer]) => [String(question), answer?.toString() || '']),
        ),
      })
      clearFn()
      navigate(`/exams/${id}/result/${data.id}`)
    } catch (err) {
      if (!auto) {
        setError(err.response?.data?.detail || 'Unable to submit exam.')
      }
    } finally {
      setSaving(false)
    }
  }

  const handleManualSubmit = async () => {
    if (!window.confirm('Submit your answers and finish the exam?')) return
    const stored = sessionStorage.getItem(storageKey)
    if (!stored) {
      setError('No active attempt found.')
      return
    }
    const attemptData = JSON.parse(stored)
    await handleSubmit(attemptData, exam, answers, () => sessionStorage.removeItem(storageKey), false)
  }

  const perQuestion = useMemo(() => {
    if (!questions.length) return []
    return questions
  }, [questions])

  if (loading) return <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-slate-500">Preparing your exam...</div>
  if (error) return <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-rose-600">{error}</div>
  if (!exam || !attempt) return null

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">{exam.title}</h1>
          <p className="mt-2 text-slate-600">Attempt #{attempt.attemptNumber}. You have {formatTimer(remainingSeconds)} remaining.</p>
        </div>
        <button
          onClick={handleManualSubmit}
          disabled={saving}
          className="rounded-xl bg-rose-600 px-5 py-3 text-sm font-semibold text-white hover:bg-rose-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Submit exam
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="space-y-6">
          {perQuestion.map((question, index) => (
            <article key={question.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-slate-900">Q{index + 1}. {question.title}</p>
                  <p className="mt-2 text-sm text-slate-500">{question.type} · {question.difficulty}</p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">{exam.questions[index]?.marks ?? 1} pts</span>
              </div>

              {question.options?.length ? (
                <div className="mt-4 space-y-3">
                  {question.options.map((option) => (
                    <label key={option.id} className="flex cursor-pointer items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                      <input
                        type={question.type === 'mcq' ? 'radio' : 'radio'}
                        name={`question-${question.id}`}
                        value={option.option_text}
                        checked={answers[question.id] === option.option_text}
                        onChange={(e) => setAnswer(question.id, e.target.value)}
                        className="h-4 w-4 text-indigo-600"
                      />
                      <span className="text-sm text-slate-700">{option.option_order}. {option.option_text}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <textarea
                  value={answers[question.id] || ''}
                  onChange={(e) => setAnswer(question.id, e.target.value)}
                  placeholder="Type your answer here"
                  rows={4}
                  className="mt-4 w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
                />
              )}
            </article>
          ))}
        </section>

        <aside className="space-y-5">
          <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Exam summary</h2>
            <dl className="mt-4 space-y-3 text-sm text-slate-600">
              <div className="flex justify-between">
                <span>Duration</span>
                <span>{exam.duration_minutes} min</span>
              </div>
              <div className="flex justify-between">
                <span>Total marks</span>
                <span>{exam.total_marks}</span>
              </div>
              <div className="flex justify-between">
                <span>Question count</span>
                <span>{questions.length}</span>
              </div>
              <div className="flex justify-between">
                <span>Attempt</span>
                <span>#{attempt.attemptNumber}</span>
              </div>
            </dl>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Instructions</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-600">
              <li>Answer every question to maximize your score.</li>
              <li>Your answers are saved only when you submit.</li>
              <li>When time reaches zero, the exam submits automatically.</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  )
}
