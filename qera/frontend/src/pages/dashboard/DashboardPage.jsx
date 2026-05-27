import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import api from '../../services/api'

function StatCard({ label, value, hint }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [recentQuestions, setRecentQuestions] = useState([])
  const [recentExams, setRecentExams] = useState([])
  const [loadError, setLoadError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [questionsRes, examsRes] = await Promise.all([
          api.get('/questions/', { params: { page: 1, limit: 5 } }),
          api.get('/exams/', { params: { page: 1, limit: 5 } }),
        ])
        if (!cancelled) {
          setRecentQuestions(questionsRes.data ?? [])
          setRecentExams(examsRes.data ?? [])
        }
      } catch {
        if (!cancelled) {
          setLoadError('Could not load recent activity. Is the API running?')
        }
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {user?.name?.split(' ')[0]}</h1>
        <p className="mt-2 text-slate-600">Your learning hub for questions, exams, and progress.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Exams attended" value="—" hint="Available after profile API (Phase 7)" />
        <StatCard label="Questions created" value="—" hint="Available after profile API (Phase 7)" />
        <StatCard label="Global rank" value="—" hint="Available after leaderboard API (Phase 6)" />
        <StatCard label="Accuracy" value="—" hint="Available after profile API (Phase 7)" />
      </div>

      {loadError && (
        <p className="mt-6 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">{loadError}</p>
      )}

      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Recent questions</h2>
            <Link to="/questions" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
              View all
            </Link>
          </div>
          {recentQuestions.length === 0 ? (
            <p className="text-sm text-slate-500">No questions yet.</p>
          ) : (
            <ul className="space-y-3">
              {recentQuestions.map((q) => (
                <li key={q.id}>
                  <Link
                    to={`/questions/${q.id}`}
                    className="block rounded-xl border border-slate-100 px-4 py-3 hover:border-indigo-200 hover:bg-indigo-50/40"
                  >
                    <p className="font-medium text-slate-900">{q.title}</p>
                    <p className="mt-1 text-xs text-slate-500 capitalize">{q.difficulty} · {q.type}</p>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Recent exams</h2>
            <Link to="/exams" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
              View all
            </Link>
          </div>
          {recentExams.length === 0 ? (
            <p className="text-sm text-slate-500">No exams yet.</p>
          ) : (
            <ul className="space-y-3">
              {recentExams.map((exam) => (
                <li key={exam.id}>
                  <Link
                    to={`/exams/${exam.id}`}
                    className="block rounded-xl border border-slate-100 px-4 py-3 hover:border-indigo-200 hover:bg-indigo-50/40"
                  >
                    <p className="font-medium text-slate-900">{exam.title}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {exam.duration_minutes} min · {exam.total_marks} marks
                    </p>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
