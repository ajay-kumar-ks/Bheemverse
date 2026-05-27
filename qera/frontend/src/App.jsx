import { Routes, Route, Navigate } from 'react-router-dom'
import PageStub from './components/PageStub'
import ProtectedRoute from './components/common/ProtectedRoute'
import AdminRoute from './components/common/AdminRoute'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import QuestionsPage from './pages/questions/QuestionsPage'
import QuestionDetailPage from './pages/questions/QuestionDetailPage'
import CreateQuestionPage from './pages/questions/CreateQuestionPage'
import ExamsPage from './pages/exams/ExamsPage'
import ExamDetailPage from './pages/exams/ExamDetailPage'
import CreateExamPage from './pages/exams/CreateExamPage'
import AttendExamPage from './pages/exams/AttendExamPage'
import ExamResultPage from './pages/exams/ExamResultPage'
import ExamLeaderboardPage from './pages/exams/ExamLeaderboardPage'
import { useAuth } from './context/AuthContext'

const stubRoutes = [
  { path: '/leaderboard', title: 'Leaderboard', description: 'Global leaderboard placeholder.' },
  { path: '/profile/:uid', title: 'Public Profile', description: 'Public profile placeholder.' },
  { path: '/bookmarks', title: 'Bookmarks', description: 'Bookmarked questions placeholder.' },
  { path: '/notifications', title: 'Notifications', description: 'Notifications page placeholder.' },
]

function HomeRedirect() {
  const { isAuthenticated, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-slate-600">
        Loading…
      </div>
    )
  }
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/questions" element={<QuestionsPage />} />
          <Route path="/questions/:id" element={<QuestionDetailPage />} />
          <Route path="/questions/create" element={<CreateQuestionPage />} />
          <Route path="/exams" element={<ExamsPage />} />
          <Route path="/exams/create" element={<CreateExamPage />} />
          <Route path="/exams/:id" element={<ExamDetailPage />} />
          <Route path="/exams/:id/attend" element={<AttendExamPage />} />
          <Route path="/exams/:id/result/:aid" element={<ExamResultPage />} />
          <Route path="/leaderboard/exam/:id" element={<ExamLeaderboardPage />} />
          <Route path="/profile/me" element={<PageStub title="My Profile" description="Personal profile placeholder." />} />
          <Route path="/bookmarks" element={<PageStub title="Bookmarks" description="Bookmarked questions placeholder." />} />
          <Route path="/notifications" element={<PageStub title="Notifications" description="Notifications page placeholder." />} />
        </Route>
      </Route>

      <Route element={<AdminRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/admin/*" element={<PageStub title="Admin Area" description="Admin dashboard and moderation placeholder." />} />
        </Route>
      </Route>

      {stubRoutes
        .filter((route) => !['/bookmarks', '/notifications'].includes(route.path))
        .map((route) => (
          <Route
            key={route.path}
            path={route.path}
            element={<PageStub title={route.title} description={route.description} />}
          />
        ))}

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
