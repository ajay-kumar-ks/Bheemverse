# QERA — Developer Quickstart (Compressed)

---

## Phase 1: Setup
- [ ] Project structure: frontend, backend, ai-services, database, docs
- [ ] Backend: `npm init`, install express, mysql2, jsonwebtoken, bcryptjs, cors, dotenv, express-validator
- [ ] Frontend: React + react-router-dom, axios, tailwindcss, zustand
- [ ] MySQL setup + schema.sql
- [ ] `.env` files (DB, JWT secret, LLM API keys)

---

## Phase 2: Backend Core
- [ ] `app.js` — Express setup, CORS, middleware stack
- [ ] `authMiddleware.js` — JWT verify & decode
- [ ] `roleMiddleware.js` — role check (admin)
- [ ] Error handler middleware
- [ ] Rate limiter (auth endpoints: 10 req/min per IP)

---

## Phase 3: Auth Module (`/api/v1/auth`)
- [ ] `POST /register` — validate, bcrypt hash, INSERT user
- [ ] `POST /login` — find user, bcrypt compare, jwt.sign()
- [ ] `POST /admin/login` — admin token (8h expiry)
- [ ] `GET /me` — return current user from token

---

## Phase 4: Question Module (`/api/v1/questions`)
- [ ] CRUD endpoints (GET list, GET detail, POST, PUT, DELETE)
- [ ] AI: duplicate detection on create → return 409 if flagged
- [ ] AI: tag suggestion (if no tags provided)
- [ ] AI: difficulty prediction (if not set)
- [ ] Like endpoint (denormalized `likes_count` counter)
- [ ] Bookmark endpoints
- [ ] Comments (self-referential, parent_id for replies)
- [ ] Comment moderation via AI (flag toxic/spam)

---

## Phase 5: Exam Module (`/api/v1/exams`)
- [ ] CRUD endpoints
- [ ] `POST /exams/:id/attempt` — create attempt record (auto-increment attempt_number)
- [ ] `POST /exams/:id/submit` — score answers vs correct_answer
- [ ] **Critical:** First attempt only (attempt_number == 1) → INSERT into leaderboard
- [ ] `GET /exams/:id/result/:attemptId` — return result + leaderboard rank
- [ ] Rank computation: `RANK() OVER (ORDER BY score DESC, time ASC)`

---

## Phase 6: User Module (`/api/v1/users`)
- [ ] `GET /:id/profile` — public profile view
- [ ] `PUT /me` — update own profile
- [ ] `GET /me/bookmarks`, `/me/exams`, `/me/questions`
- [ ] `GET /me/notifications` (polling-based)
- [ ] `PUT /notifications/:id/read`

---

## Phase 7: Leaderboard Module (`/api/v1/leaderboard`)
- [ ] `GET /global` — aggregate first-attempt scores all exams
- [ ] `GET /exam/:examId` — per-exam ranking
- [ ] Ranking: score DESC → time_taken_seconds ASC → submitted_at ASC

---

## Phase 8: AI Module (`/api/v1/ai`)
- [ ] `POST /generate-questions` — topic/text → MCQ/short answer
- [ ] `POST /generate-exam` — admin only, build from bank or generate
- [ ] `POST /explain` — on-demand explanation
- [ ] `POST /check-duplicate` — embedding similarity
- [ ] `POST /suggest-tags` — auto-tag
- [ ] `POST /analyze-difficulty` — easy/medium/hard
- [ ] `POST /recommend` — weak topic suggestions
- [ ] `POST /study-assistant` — conversational Q&A

---

## Phase 9: Search Module (`/api/v1/search`)
- [ ] `GET /questions?q=keyword&tags=X&difficulty=Y&type=Z&mode=keyword|semantic`
- [ ] Keyword: SQL FULLTEXT index on title, description
- [ ] Semantic: AI embed query → cosine similarity
- [ ] Apply filters (tags, difficulty, type)

---

## Phase 10: Notifications (`/api/v1/notifications`)
- [ ] `GET /` — all notifications
- [ ] `PUT /:id/read` — mark single as read
- [ ] `PUT /read-all` — mark all as read
- [ ] Triggers: new_exam, comment_reply, leaderboard_update, new_question

---

## Phase 11: Database Layer
- [ ] Models folder with raw SQL queries (no ORM)
- [ ] Parameterized queries (no string interpolation)
- [ ] Indexes: users(email), questions(FULLTEXT), exam_attempts(exam_id, user_id, attempt_number), leaderboard(exam_id, score, time)

---

## Phase 12: AI Services (10 modules)
1. `questionGenerator.js` — Topic/text → questions
2. `examGenerator.js` — Build exams (admin)
3. `duplicateDetector.js` — Embeddings similarity check
4. `difficultyAnalyzer.js` — Predict easy/medium/hard
5. `explanationGenerator.js` — Why answers correct
6. `tagGenerator.js` — Auto-tags
7. `recommendationEngine.js` — Weak topic suggestions
8. `studyAssistant.js` — Chat Q&A
9. `moderationFilter.js` — Toxic/spam detection
10. `semanticSearch.js` — Embedding-based retrieval

---

## Phase 13: Frontend Routes
| Route | Auth | Component |
|-------|------|-----------|
| `/login`, `/register` | No | Login/Register forms |
| `/dashboard` | Student | Home, stats, activity |
| `/questions`, `/questions/create`, `/questions/:id` | No/Student/No | List, form, viewer |
| `/exams`, `/exams/create`, `/exams/:id` | No/Student/No | List, form, detail |
| `/exams/:id/attend` | Student | Timer, Q display, submit |
| `/exams/:id/result/:attemptId` | Student | Score, breakdown, rank |
| `/leaderboard`, `/leaderboard/exam/:id` | No | Global & per-exam ranks |
| `/profile/:userId`, `/profile/me` | No/Student | Public & own profiles |
| `/bookmarks`, `/notifications` | Student | Bookmarks, events |
| `/admin/*` | Admin | Dashboard (role-gated) |

---

## Phase 14: Frontend Components
- **Auth:** Login/Register forms, context provider, token storage
- **Question:** Card, create form, viewer, comment thread, like/bookmark buttons
- **Exam:** Card, detail, attend page with timer, result breakdown
- **Leaderboard:** Table with rank/score/time/accuracy
- **Notifications:** Polling (30s), list, read toggle
- **Layout:** Navbar, sidebar, footer
- **Common:** Buttons, inputs, modals, loaders, error alerts

---

## Critical Business Rules
| Rule | Implementation |
|------|---|
| First attempt only ranks | Only insert `attempt_number == 1` into leaderboard |
| Duplicate detection | Auto on create; return 409; student confirms override |
| Auto-submit exams | Timer hits 0 → submit; backend validates `time_taken ≤ duration + 30s grace` |
| Comment moderation | AI flags before save; `is_flagged = true`; hidden until admin review |
| Denormalized counters | Update `likes_count` atomically; don't re-query COUNT |
| Password security | bcrypt 12 rounds; never plaintext; use bcrypt.compare() |
| JWT expiry | Student 24h, Admin 8h |
| Leaderboard ties | score DESC → time ASC → date ASC |

---

## Database Tables (Minimal Schema)
```
users(id, name, email UNIQUE, password_hash, role, avatar_url, bio, timestamps)
questions(id, user_id, title, description, type, correct_answer, difficulty, explanation, is_public, likes_count, timestamps)
question_options(id, question_id, option_text, option_order)
question_tags(question_id, tag_id) [join table]
tags(id, name UNIQUE)
exams(id, user_id, title, description, duration_minutes, total_marks, is_public, randomize_order, timestamps)
exam_questions(id, exam_id, question_id, marks, question_order)
exam_attempts(id, exam_id, user_id, attempt_number, score, total_marks, time_taken_seconds, submitted_at, answers JSON)
leaderboard(id, exam_id, user_id, attempt_id, score, time_taken_seconds, rank) [first attempt only]
comments(id, question_id, user_id, parent_id [NULL=top-level], content, is_flagged, created_at)
bookmarks(user_id, question_id, created_at)
notifications(id, user_id, type, message, reference_id, reference_type, is_read, created_at)
```

---

## API Endpoint Summary (All `/api/v1`)
```
POST   /auth/register
POST   /auth/login
POST   /auth/admin/login
GET    /auth/me

GET    /questions (paginated)
GET    /questions/:id
POST   /questions (student)
PUT    /questions/:id (owner|admin)
DELETE /questions/:id (owner|admin)
POST   /questions/:id/like (student)
POST   /questions/:id/bookmark (student)
GET    /questions/:id/comments
POST   /questions/:id/comments (student)
POST   /questions/:id/comments/:commentId/reply (student)

GET    /exams (paginated)
GET    /exams/:id
POST   /exams (student)
PUT    /exams/:id (owner|admin)
DELETE /exams/:id (owner|admin)
POST   /exams/:id/attempt (student)
POST   /exams/:id/submit (student)
GET    /exams/:id/result/:attemptId (student)
GET    /exams/:id/leaderboard

GET    /users/:id/profile
PUT    /users/me (student)
GET    /users/me/bookmarks (student)
GET    /users/me/exams (student)
GET    /users/me/questions (student)
GET    /users/me/notifications (student)

GET    /leaderboard/global
GET    /leaderboard/exam/:examId

POST   /ai/generate-questions (student)
POST   /ai/generate-exam (admin)
POST   /ai/explain (student)
POST   /ai/check-duplicate (student)
POST   /ai/suggest-tags (student)
POST   /ai/analyze-difficulty (student)
POST   /ai/recommend (student)
POST   /ai/study-assistant (student)

GET    /search/questions (query: q, tags, difficulty, type, mode)
GET    /search/exams

GET    /notifications (student)
PUT    /notifications/:id/read (student)
PUT    /notifications/read-all (student)
```

---

## Security Checklist
- [ ] Auth: JWT middleware on protected routes
- [ ] Input: Server-side validation (express-validator)
- [ ] SQL: Parameterized queries (no interpolation)
- [ ] Passwords: bcrypt 12 rounds
- [ ] Secrets: `.env` (never committed)
- [ ] CORS: Frontend origin only
- [ ] Rate limit: Auth endpoints (10 req/min/IP)
- [ ] Admin: Role-gated routes
- [ ] Tokens: 24h student, 8h admin expiry
- [ ] Logs: No sensitive data

---

## Common Pitfalls
1. ⚠️ First attempt logic — use explicit attempt_number check
2. ⚠️ Denormalized counters — update atomically, don't re-query
3. ⚠️ JWT in localStorage — consider httpOnly cookies for production
4. ⚠️ Leaderboard ties — implement consistent tiebreaker
5. ⚠️ AI failures — graceful fallbacks, cached results
6. ⚠️ Comment deletion — flag instead of immediate delete
7. ⚠️ Exam timer — validate backend, not just frontend
8. ⚠️ Pagination — required on all list endpoints

---

## Testing
- [ ] Unit: authService, questionService, examService, leaderboardService
- [ ] Integration: All API endpoints
- [ ] Leaderboard: Multiple attempts, ranking logic
- [ ] Duplicate detection: Varied similarity scores
- [ ] Comment moderation: Toxic & clean inputs
- [ ] RBAC: Student vs admin endpoints
- [ ] Error responses: 400, 401, 403, 404, 409, 500
- [ ] E2E: Register → Create Q → Create Exam → Attempt → Result

---

## Folder Structure
```
qera/
├── frontend/src/
│   ├── components/common, question, exam, leaderboard, layout
│   ├── pages/auth, dashboard, exams, questions, leaderboard, profile, admin
│   ├── hooks/, context/, services/, utils/
│   └── App.jsx
├── backend/src/
│   ├── config/, controllers/, services/, models/
│   ├── routes/, middlewares/, utils/
│   └── app.js
├── ai-services/ (10 modules)
├── database/schema.sql, migrations/, seeds/
└── docs/
```

---

## Key Payloads
**POST /auth/register:** `{name, email, password}`
**POST /auth/login:** Returns `{token, user}`
**POST /questions:** `{title, description, type, options, correct_answer, difficulty, explanation, tags}`
**POST /exams/:id/submit:** `{attempt_id, time_taken_seconds, answers: {question_id: answer}}`

---

*QERA Compressed Reference | v1.0 | May 2026*
