import { Routes, Route, Navigate } from 'react-router-dom'
import PageStub from './components/PageStub'
import ProtectedRoute from './components/common/ProtectedRoute'
import AdminRoute from './components/common/AdminRoute'
import AppLayout from './components/layout/AppLayout'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import { useAuth } from './context/AuthContext'

const stubRoutes = [
  { path: '/questions', title: 'Questions', description: 'Question bank list placeholder.' },
  { path: '/questions/create', title: 'Create Question', description: 'Question creation form placeholder.' },
  { path: '/questions/:id', title: 'Question Details', description: 'Question detail view placeholder.' },
  { path: '/exams', title: 'Exams', description: 'Exam list placeholder.' },
  { path: '/exams/create', title: 'Create Exam', description: 'Exam creation page placeholder.' },
  { path: '/exams/:id', title: 'Exam Details', description: 'Exam details page placeholder.' },
  { path: '/exams/:id/attend', title: 'Attend Exam', description: 'Exam attendance page placeholder.' },
  { path: '/exams/:id/result/:aid', title: 'Exam Result', description: 'Exam result summary placeholder.' },
  { path: '/leaderboard', title: 'Leaderboard', description: 'Global leaderboard placeholder.' },
  { path: '/leaderboard/exam/:id', title: 'Exam Leaderboard', description: 'Exam-specific leaderboard placeholder.' },
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
          <Route path="/profile/me" element={<PageStub title="My Profile" description="Personal profile placeholder." />} />
          <Route path="/bookmarks" element={<PageStub title="Bookmarks" description="Bookmarked questions placeholder." />} />
          <Route path="/notifications" element={<PageStub title="Notifications" description="Notifications page placeholder." />} />
          <Route path="/exams/:id/attend" element={<PageStub title="Attend Exam" description="Exam attendance page placeholder." />} />
          <Route path="/exams/:id/result/:aid" element={<PageStub title="Exam Result" description="Exam result summary placeholder." />} />
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
