# QERA Platform — Implementation Checklist & Developer Quick Start

> Generated from QERA.md analysis. Use this alongside the main documentation for quick reference during development.

---

## Project Setup Checklist

### Phase 1: Infrastructure & Config
- [ ] Create project folder structure (frontend, backend, ai-services, database, docs)
- [ ] Initialize Node.js backend project with `npm init`
- [ ] Initialize React frontend with Create React App or Vite
- [ ] Set up MySQL database and schema (see schema.sql)
- [ ] Create `.env` files (DB credentials, JWT secret, LLM API keys)
- [ ] Install core dependencies:
  - **Backend:** express, mysql2, jsonwebtoken, bcryptjs, cors, dotenv, express-validator
  - **Frontend:** react-router-dom, axios, tailwindcss, zustand (or context API)

### Phase 2: Backend Development
- [ ] Create `app.js` with Express server setup, CORS config, middleware order
- [ ] Implement `authMiddleware.js` — JWT verify & decode
- [ ] Implement `roleMiddleware.js` — check role === 'admin'
- [ ] Create error handler middleware
- [ ] Build **Auth Module** (`authController.js`, `authService.js`, `authRoutes.js`)
  - [ ] Register endpoint with input validation
  - [ ] Login endpoint with bcrypt password compare & JWT generation
  - [ ] `/me` endpoint to get current user from token
- [ ] Build **Question Module** (CRUD, comments, likes, bookmarks)
  - [ ] Implement duplicate detection on create (call AI service)
  - [ ] Implement tag suggestion & difficulty analysis
  - [ ] Implement comment moderation (call AI service)
- [ ] Build **Exam Module** (CRUD, attempts, scoring, leaderboard integration)
  - [ ] Implement attempt creation
  - [ ] Implement scoring logic (compare answers to correct answers)
  - [ ] Ensure first attempt only populates leaderboard
  - [ ] Implement leaderboard rank computation (window function)
- [ ] Build **User Module** (profile, bookmarks, notifications)
- [ ] Build **Leaderboard Module** (global & per-exam queries)
- [ ] Build **AI Module** (gateway to ai-services/)
- [ ] Build **Search Module** (keyword + semantic modes)
- [ ] Build **Notification Module** (event log + polling)
- [ ] Implement database layer (models/ folder with raw SQL queries)
- [ ] Add rate limiting to auth endpoints (10 req/min per IP)

### Phase 3: AI Services
- [ ] Create `ai-services/` module with 10 AI feature implementations:
  1. `questionGenerator.js`
  2. `examGenerator.js`
  3. `duplicateDetector.js`
  4. `difficultyAnalyzer.js`
  5. `explanationGenerator.js`
  6. `tagGenerator.js`
  7. `recommendationEngine.js`
  8. `studyAssistant.js`
  9. `moderationFilter.js`
  10. `semanticSearch.js`
- [ ] Integrate each with LLM API (OpenAI, Anthropic, etc.)
- [ ] Test prompt engineering & response parsing

### Phase 4: Frontend Development
- [ ] Set up React router for all routes (see Routes table in QERA.md)
- [ ] Create **Auth Pages** (`Login.jsx`, `Register.jsx`)
  - [ ] Form validation & error display
  - [ ] Token storage (localStorage) & context setup
- [ ] Create **Question Pages** (`QuestionList.jsx`, `CreateQuestion.jsx`, `ViewQuestion.jsx`)
  - [ ] Search & filter UI (keyword, tags, difficulty, type)
  - [ ] Create form with AI suggestion UI (tags, difficulty)
  - [ ] Comment thread UI with moderation notice for flagged content
  - [ ] Like & bookmark buttons
- [ ] Create **Exam Pages** (`ExamList.jsx`, `AttendExam.jsx`, `ResultPage.jsx`)
  - [ ] Countdown timer component (auto-submit on 0)
  - [ ] Question renderer (MCQ, true/false, short answer, descriptive)
  - [ ] Answer submission form
  - [ ] Result breakdown page with explanations & leaderboard position
- [ ] Create **Leaderboard Pages** (global & per-exam)
- [ ] Create **Profile Pages** (own & public)
- [ ] Create **Dashboard** (summary, stats, recent activity)
- [ ] Create **Admin Dashboard** (only if admin role)
- [ ] Implement notification polling (30s interval)
- [ ] Implement error handling & loading states across all pages
- [ ] Style with Tailwind CSS

### Phase 5: Database & Testing
- [ ] Create `schema.sql` with all table definitions
- [ ] Create seed data (`seeds/` folder) for testing
- [ ] Run integration tests on API endpoints
- [ ] Test leaderboard ranking logic with multiple attempts
- [ ] Test AI service responses & error handling
- [ ] Test auth flows (register, login, token expiry)
- [ ] Test role-based access control (student vs admin)

### Phase 6: Deployment
- [ ] Set up backend hosting (Heroku, AWS, Azure, etc.)
- [ ] Set up frontend hosting (Vercel, Netlify, etc.)
- [ ] Configure production `.env` variables
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for production frontend URL
- [ ] Test end-to-end on staging environment
- [ ] Deploy frontend & backend

---

## Core Flows to Implement

### 1. Register & Login
```
POST /auth/register + validation → bcrypt hash → INSERT user → return 200
POST /auth/login → find user → bcrypt compare → jwt.sign() → return token
```

### 2. Create Question
```
POST /questions → validate input → AI: check duplicate
  → if duplicate: return 409 (student confirms)
  → AI: suggest tags (if none) → AI: predict difficulty (if not set)
  → INSERT question + options + tags → return created question
```

### 3. Attempt Exam
```
POST /exams/:id/attempt → create exam_attempts row (attempt_number = 1 or 2, etc.)
  → Frontend: countdown timer
POST /exams/:id/submit → validate answers → calculate score
  → if attempt_number == 1: INSERT into leaderboard
  → compute rank with window function → return result
```

### 4. Comment on Question
```
POST /questions/:id/comments → AI: check if toxic/spam
  → if flagged: INSERT with is_flagged = true
  → Notification to question owner → return comment
```

### 5. Search Questions
```
GET /search/questions?q=keyword&mode=semantic
  → if keyword: SQL FULLTEXT search
  → else if semantic: AI embed query → cosine similarity over embeddings
  → apply filters (tags, difficulty, type) → return ranked results
```

---

## Database Schema Essentials

### Key Constraints
- `users.email` — UNIQUE
- `questions.user_id` — FK to users
- `exam_attempts.attempt_number` — auto-increment per exam
- `leaderboard.attempt_id` — only for attempt_number == 1
- `comments.parent_id` — NULL for top-level, set for replies
- All timestamps — DATETIME DEFAULT CURRENT_TIMESTAMP

### Indexing Strategy
- `users(email)` — unique, for login lookup
- `questions(user_id)` — FK lookup
- `questions(FULLTEXT title, description)` — keyword search
- `exam_attempts(exam_id, user_id, attempt_number)` — composite for leaderboard
- `leaderboard(exam_id, score DESC, time_taken_seconds ASC)` — ranking
- `comments(question_id, parent_id)` — thread retrieval

---

## API Endpoint Summary (All prefixed with `/api/v1`)

### Auth
- `POST /auth/register` — Public
- `POST /auth/login` — Public
- `POST /auth/admin/login` — Public
- `GET /auth/me` — Protected

### Questions
- `GET /questions` — Public, paginated
- `GET /questions/:id` — Public
- `POST /questions` — Protected (student)
- `PUT /questions/:id` — Protected (owner|admin)
- `DELETE /questions/:id` — Protected (owner|admin)
- `POST /questions/:id/like` — Protected
- `POST /questions/:id/bookmark` — Protected
- `GET /questions/:id/comments` — Public
- `POST /questions/:id/comments` — Protected
- `POST /questions/:id/comments/:commentId/reply` — Protected

### Exams
- `GET /exams` — Public
- `GET /exams/:id` — Public
- `POST /exams` — Protected (student)
- `PUT /exams/:id` — Protected (owner|admin)
- `DELETE /exams/:id` — Protected (owner|admin)
- `POST /exams/:id/attempt` — Protected
- `POST /exams/:id/submit` — Protected
- `GET /exams/:id/result/:attemptId` — Protected
- `GET /exams/:id/leaderboard` — Public

### Users
- `GET /users/:id/profile` — Public
- `PUT /users/me` — Protected
- `GET /users/me/bookmarks` — Protected
- `GET /users/me/exams` — Protected
- `GET /users/me/questions` — Protected
- `GET /users/me/notifications` — Protected

### Leaderboard
- `GET /leaderboard/global` — Public
- `GET /leaderboard/exam/:examId` — Public

### AI
- `POST /ai/generate-questions` — Protected (student)
- `POST /ai/generate-exam` — Protected (admin)
- `POST /ai/explain` — Protected
- `POST /ai/check-duplicate` — Protected
- `POST /ai/suggest-tags` — Protected
- `POST /ai/analyze-difficulty` — Protected
- `POST /ai/recommend` — Protected
- `POST /ai/study-assistant` — Protected

### Search
- `GET /search/questions` — Public (query params: q, tags, difficulty, type, mode)
- `GET /search/exams` — Public

### Notifications
- `GET /notifications` — Protected
- `PUT /notifications/:id/read` — Protected
- `PUT /notifications/read-all` — Protected

---

## Security Checklist

- [ ] All routes require auth middleware for protected endpoints
- [ ] All input validated server-side (express-validator)
- [ ] All SQL queries parameterized (no string interpolation)
- [ ] Passwords hashed with bcrypt (rounds = 12)
- [ ] JWT secret stored in `.env` (never committed)
- [ ] CORS configured to allow only frontend origin
- [ ] Rate limiting on auth endpoints (10 req/min per IP)
- [ ] Admin routes gated by role check
- [ ] JWT token expiry enforced (24h student, 8h admin)
- [ ] No sensitive data in logs or error messages
- [ ] HTTPS enforced in production

---

## Common Pitfalls to Avoid

1. **First Attempt Logic** — Only `attempt_number = 1` should be inserted into leaderboard. Multiple `INSERT` statements can cause duplicates.
2. **Denormalized Counters** — Update `likes_count` atomically with the like/unlike operation, don't re-query.
3. **JWT in localStorage** — Consider security implications; use httpOnly cookies for production if possible.
4. **Leaderboard Ties** — Implement tiebreaker: score DESC → time ASC → date ASC to break ties consistently.
5. **AI Service Failures** — Gracefully handle LLM API downtime; return defaults or cached results.
6. **Comment Moderation Lag** — Flag toxic comments but don't delete immediately; let admin review.
7. **Exam Timer** — Frontend enforces timer, but backend must validate `time_taken_seconds` against `duration_minutes` (with grace period).
8. **Pagination** — Always paginate list endpoints to prevent OOM on large result sets.

---

## Testing Checklist

- [ ] Unit tests for all services (authService, questionService, etc.)
- [ ] Integration tests for API endpoints
- [ ] Test leaderboard ranking with multiple attempts
- [ ] Test duplicate detection with varied similarity scores
- [ ] Test comment moderation with toxic & clean inputs
- [ ] Test JWT expiry & refresh logic
- [ ] Test role-based access control (student can't access admin endpoints)
- [ ] Test pagination on list endpoints
- [ ] Test error responses (400, 401, 403, 404, 409, 500)
- [ ] End-to-end test: register → create question → create exam → attempt → view result

---

## File Structure Reminder

```
qera/
├── frontend/src/
│   ├── components/common, question, exam, leaderboard, layout
│   ├── pages/auth, dashboard, exams, questions, leaderboard, profile, admin
│   ├── hooks/
│   ├── context/
│   ├── services/
│   └── utils/
├── backend/src/
│   ├── config/
│   ├── controllers/
│   ├── services/
│   ├── models/
│   ├── routes/
│   ├── middlewares/
│   └── utils/
├── ai-services/ (10 modules)
├── database/schema.sql, migrations/, seeds/
└── docs/QERA.md, api-reference.md, ai-agent-guide.md
```

---

*Document version: 1.0 | For QERA development teams | Last updated: May 2026*
