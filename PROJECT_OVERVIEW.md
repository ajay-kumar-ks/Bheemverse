# QERA Project Overview

## Project Snapshot

QERA is a full-stack exam preparation platform built with:
- Frontend: React 18, Vite, Tailwind CSS, React Router DOM, Axios
- Backend: FastAPI, SQLite, aiosqlite, Pydantic v2, JWT auth, SlowAPI rate limiting
- Deployment pattern: frontend proxy to backend via Vite `/api` proxy
- DB: local SQLite file with schema, migrations, and dev seed data

## Completed Work

### Major completed modules
- Project scaffold and configuration
- SQLite database schema, migrations, and seed data
- Authentication: register, login, JWT token, auth middleware, admin role
- Questions: CRUD, options, tags, search, likes, bookmarks, comments
- Exams: exam CRUD, attempt flow, scoring, results, leaderboard insert
- Leaderboard: exam-level and global leaderboard ranking
- Profiles & bookmarks: user stats, profile update, user-specific content
- Notifications: create/read/mark read, notification endpoints
- Admin backend: user management, content moderation, exam generation hooks
- Frontend UI: auth, dashboard, questions, exams, leaderboard, profile, admin

### Skipped / not implemented
- Full AI services package (`ai-services` module) is deferred
- Phase 17 frontend AI feature UI is not implemented
- Phase 18 integration, QA, hardening is not completed

## Project Architecture

### Backend structure

`qera/backend/`
- `main.py` — FastAPI app, CORS, middleware, router registration, DB startup/shutdown
- `config.py` — app settings (SECRET_KEY, DB_PATH, ALLOWED_ORIGIN)
- `database.py` — SQLite connection, WAL mode, schema execution, migrations runner
- `requirements.txt` — backend Python dependency manifest

`qera/backend/routers/`
- `auth_router.py` — `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, admin login, logout
- `question_router.py` — question CRUD, like/bookmark, question comments, search integration
- `comment_router.py` — comments and threaded replies for questions
- `exam_router.py` — exam creation, start attempt, submit attempt, result, exam leaderboard
- `leaderboard_router.py` — global and exam leaderboard endpoints
- `user_router.py` — user profile, bookmarks, user questions/exams, notifications
- `notification_router.py` — notification list and read actions
- `admin_router.py` — admin-only user/content moderation endpoints
- `search_router.py` — search question/exam APIs
- `health.py` — health check endpoint

`qera/backend/models/`
- `user_model.py` — user CRUD, profile stats, bookmarks, questions, exams
- `question_model.py` — save/load questions, options, tags, likes, bookmarks
- `exam_model.py` — exam persistence, attempts, scoring, results
- `leaderboard_model.py` — leaderboard retrieval and ranking
- `notification_model.py` — notification create/read operations
- `comment_model.py` — threaded comment storage and retrieval
- `search_model.py` — SQLite FTS5 search query builder

`qera/backend/services/`
- `auth_service.py` — register/login logic, bcrypt hashing, JWT generation and validation
- `question_service.py` — question creation pipeline and AI stub integration
- `exam_service.py` — exam scoring and attempt orchestration
- `leaderboard_service.py` — leaderboard update helper
- `notification_service.py` — notification creation and delivery logic
- `ai_service.py` — AI stubs for duplicate detection, tags, difficulty, moderation, semantic search

`qera/backend/middlewares/`
- `auth.py` — Bearer token validation and current user dependency
- `role.py` — admin role guard
- `rate_limit.py` — rate limiter configuration

### Frontend structure

`qera/frontend/`
- `package.json` — frontend dependencies and scripts
- `vite.config.js` — React + Tailwind plugin and proxy to backend
- `src/main.jsx` — React root and `AuthProvider` mount
- `src/App.jsx` — route definitions and protected route wrappers
- `src/services/api.js` — Axios client, JWT header injection, 401 handler
- `src/context/AuthContext.jsx` — auth state, token persistence, login/register/logout, refresh user
- `src/components/layout/` — `Navbar`, `AppLayout`, route wrappers
- `src/components/common/` — `ProtectedRoute`, `AdminRoute`
- `src/pages/` — actual pages for auth, dashboard, questions, exams, leaderboard, profile, notifications, admin
- `src/pages/profile/` — public profile, my profile, placeholder profile views
- `src/pages/questions/` — questions list, detail, create, and comments
- `src/pages/exams/` — exam list, create, attend, result, exam leaderboard
- `src/pages/leaderboard/` — leaderboard UI
- `src/pages/admin/` — admin pages for dashboard, user management, moderation, content review

### Database & data flow

`qera/database/schema.sql`
- Tables: `users`, `questions`, `question_options`, `tags`, `question_tags`, `exams`, `exam_questions`, `exam_attempts`, `leaderboard`, `bookmarks`, `comments`, `notifications`, `_migrations`
- FTS5 virtual table: `questions_fts`, with triggers to keep search index synced
- `migrations/` folder manages incremental DB changes by name tracking
- `seeds/dev_seed.sql` populates sample users, questions, exams, attempts, leaderboard records

## Core flow summary

### App startup
1. Frontend starts via `npm run dev`; Vite proxies `/api` requests to backend on `http://127.0.0.1:8000`
2. Backend starts via `uvicorn main:app --reload`
3. Backend init loads SQLite DB, applies schema, runs migrations, enables PRAGMA foreign keys and WAL

### Auth flow
1. User registers: `POST /api/v1/auth/register`
2. User logs in: `POST /api/v1/auth/login`; backend returns JWT + user data
3. Frontend stores JWT in `localStorage`; Axios adds `Authorization: Bearer <token>` on requests
4. Protected routes use `ProtectedRoute`; admin routes use `AdminRoute`
5. `GET /api/v1/auth/me` refreshes current user profile

### Question flow
1. Create question: frontend submits `POST /api/v1/questions/` with title, type, options, difficulty, tags, description
2. Backend service calls AI stub hooks for duplicate detection, tag suggestions, difficulty estimation
3. Question model inserts question, options, tags, and updates full-text search index
4. Search hits use FTS5 query with optional difficulty/type/tag filters
5. Like/bookmark toggles use dedicated endpoints and persist counts
6. Comments and replies stored with parent-child threading; moderation filter applied on POST

### Exam flow
1. Exam creation: `POST /api/v1/exams/` with question list and exam metadata
2. User starts exam: `POST /api/v1/exams/{id}/attempts` → new attempt ID
3. Attempt submission: `POST /api/v1/exams/{id}/submit` with answers + time; backend scores and stores result
4. First attempt result may update leaderboard; subsequent attempts are recorded but not leaderboard-eligible
5. `GET /api/v1/exams/{id}/result/{attemptId}` returns breakdown

### Profile/leaderboard flow
1. Profile loads via `GET /api/v1/users/me` or `GET /api/v1/users/{id}`
2. Profile includes stats: exams attended, exams created, questions created, accuracy, global rank, recent questions, recent exams
3. Leaderboard pages use global and exam-specific endpoints for sorted ranking
4. Notifications are read via `GET /api/v1/notifications/` and marked read with PUT

## Connections between modules

- Auth is the foundation: every protected backend route depends on `auth.py`; admin-only routes also depend on `role.py`
- Questions, exams, and comments all create notifications; notification service is cross-cutting
- Questions feed search and bookmark flows; search connects to question model via FTS5
- Exam attempts update leaderboard; leaderboard service uses exam attempt and user models
- Profile endpoints aggregate data from user, question, exam, leaderboard, and notification models
- Admin module can suspend users, delete content, moderate flagged items; it depends on auth and content models

## Dependencies

### Backend dependencies (`requirements.txt`)
- `fastapi` — web framework
- `uvicorn[standard]` — ASGI server
- `python-jose[cryptography]` — JWT token generation and verification
- `passlib[bcrypt]`, `bcrypt<5` — password hashing and verification
- `pydantic>=2.9.0`, `pydantic-settings>=1.0.0` — request/response validation
- `email-validator` — email schema validation
- `aiosqlite>=0.18.0` — async SQLite driver
- `slowapi>=0.1.6` — rate limiting middleware
- `python-multipart>=0.0.6` — multipart support if needed

### Frontend dependencies (`package.json`)
- `react` / `react-dom` — UI framework
- `axios` — HTTP client
- `react-router-dom` — client-side routing
- `zustand` — lightweight state management (unused in current code except package install)
- `tailwindcss` / `postcss` / `autoprefixer` — styling
- `vite` / `@vitejs/plugin-react` — build tooling

## What is fully done

- Backend HTTP API for auth, questions, exams, leaderboard, profiles, bookmarks, comments, notifications, user/admin management
- Frontend pages for login, registration, dashboard, question list/detail/create, exam list/create/attend/result, leaderboard, profile, bookmarks, notifications, admin pages
- SQLite database and migration pipeline
- JWT auth and protected routing with role checks
- User profile read/update and supporting stats
- Search with FTS5 plus stub semantic fallback
- Notification lifecycle and read actions
- Admin moderation and user management flows

## What is not done yet or deferred

### Backend
- Full AI service package inside `ai-services/` is not implemented
- AI generation of questions/exams/explanations is stubbed in `backend/services/ai_service.py`
- No true semantic search embeddings service; semantic search returns `null` stub
- No production hardening, metrics, logging, and deployment scripts
- No file upload support for avatars; only `avatar_url`

### Frontend
- Phase 17 AI features UI is absent: no chat/assistant interface, no AI-generated content portal
- Profile and dashboard cards are populated from backend data but may show placeholders if backend stats are empty
- Some admin UI behavior may remain stubbed or not fully polished
- No offline support or PWA readiness

## Recommended next work

1. Implement `ai-services/` package and connect `backend/services/ai_service.py` to real AI modules
2. Add AI feature UI pages and integrate them with backend AI endpoints
3. Harden backend error handling, logging, and rate limiting
4. Add automated tests for API and frontend integration
5. Add production build/deploy docs and containerization
6. Improve frontend admin features and data refresh flows

## Summary

QERA is a mostly complete full-stack MVP for exam/question management with all core modules implemented except full AI integration and final QA/hardening. The backend is organized by routers, services, models, and middleware. The frontend is organized by pages, layout components, auth context, and API service. The app flow is standard: auth enables protected endpoints, question/exam creation feeds content, notifications connect actions across domains, and leaderboard/profile pages aggregate user performance.
