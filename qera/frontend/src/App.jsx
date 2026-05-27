import { Routes, Route, Navigate } from 'react-router-dom'
import PageStub from './components/PageStub'

const routeMap = [
  { path: '/', title: 'Home', description: 'Landing page placeholder for QERA.' },
  { path: '/login', title: 'Login', description: 'Student and admin login pages.' },
  { path: '/register', title: 'Register', description: 'Student registration page.' },
  { path: '/dashboard', title: 'Dashboard', description: 'Main student dashboard placeholder.' },
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
  { path: '/profile/me', title: 'My Profile', description: 'Personal profile placeholder.' },
  { path: '/bookmarks', title: 'Bookmarks', description: 'Bookmarked questions placeholder.' },
  { path: '/notifications', title: 'Notifications', description: 'Notifications page placeholder.' },
  { path: '/admin/*', title: 'Admin Area', description: 'Admin dashboard and moderation placeholder.' },
]

function App() {
  return (
    <Routes>
      {routeMap.map((route) => (
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
