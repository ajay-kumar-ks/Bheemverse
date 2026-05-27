# QERA — Implementation Plan
> Stack: React+Tailwind / FastAPI / SQLite / ai-services
> Legend: ✅ Done | 🔄 In Progress | ⬜ Not Started
> **AI AGENT INSTRUCTION:** At the start of every session, read this file top-to-bottom. Use the checkboxes to understand what is complete, what is active, and what is next. Never re-implement a ✅ task. Always pick up from the first 🔄 or the first ⬜ task in the current phase.

---

## PHASE OVERVIEW (Quick Status Snapshot)

| Phase | Name | Status | Tasks Done |
|-------|------|--------|------------|
| P1 | Project Scaffold & Config | ✅ | 6 / 6 |
| P2 | Database Layer | ✅ | 5 / 5 |
| P3 | Auth Module | ⬜ | 0 / 6 |
| P4 | Questions Module | ⬜ | 0 / 8 |
| P5 | Exams Module | ⬜ | 0 / 7 |
| P6 | Leaderboard Module | ⬜ | 0 / 4 |
| P7 | User Profile & Bookmarks | ⬜ | 0 / 5 |
| P8 | Comments & Notifications | ⬜ | 0 / 5 |
| P9 | Search Module | ⬜ | 0 / 4 |
| P10 | AI Services Module | ⬜ | 0 / 10 |
| P11 | Admin Module | ⬜ | 0 / 6 |
| P12 | Frontend — Scaffold & Auth | ⬜ | 0 / 7 |
| P13 | Frontend — Questions UI | ⬜ | 0 / 6 |
| P14 | Frontend — Exams UI | ⬜ | 0 / 7 |
| P15 | Frontend — Leaderboard & Profile UI | ⬜ | 0 / 5 |
| P16 | Frontend — Admin UI | ⬜ | 0 / 5 |
| P17 | Frontend — AI Features UI | ⬜ | 0 / 5 |
| P18 | Integration, QA & Hardening | ⬜ | 0 / 6 |

---

## PHASE 1 — Project Scaffold & Config
**Goal:** Repo structure, dependency setup, environment config, running skeletons for both frontend and backend.
**Status:** ✅ Completed

- [x] P1.1 — Init monorepo folder structure as per FOLDER MAP in QERA.mem (`qera/frontend`, `qera/backend`, `qera/ai-services`, `qera/database`, `qera/docs`)
- [x] P1.2 — Backend: init Python venv; install `fastapi`, `uvicorn`, `python-jose[cryptography]`, `passlib[bcrypt]`, `pydantic`, `aiosqlite`, `slowapi`, `python-multipart`; create `requirements.txt`
- [x] P1.3 — Backend: create `main.py` (FastAPI app instance, CORS middleware, router includes, lifespan), `config.py` (env vars: SECRET_KEY, DB_PATH, ALLOWED_ORIGIN), `database.py` (aiosqlite connection pool, WAL mode enable)
- [x] P1.4 — Frontend: `npm create vite@latest frontend -- --template react`; install `tailwindcss`, `react-router-dom`, `axios`, `zustand` (or Context); configure Tailwind
- [x] P1.5 — Frontend: scaffold `App.jsx` with React Router route stubs for all routes listed in QERA.mem FRONTEND ROUTES section; create placeholder page components
- [x] P1.6 — Verify: backend runs on `uvicorn main:app --reload`; frontend runs on `npm run dev`; both reachable; CORS allows frontend origin

---

## PHASE 2 — Database Layer
**Goal:** Full SQLite schema in place, migration system, seed data for dev.
**Status:** ✅ Completed

- [x] P2.1 — Write `database/schema.sql` with all 11 tables: `users`, `questions`, `question_options`, `tags`, `question_tags`, `exams`, `exam_questions`, `exam_attempts`, `leaderboard`, `bookmarks`, `comments`, `notifications` — exactly matching QERA.mem DATABASE SCHEMA; include FTS5 virtual table for questions full-text search; enable WAL via PRAGMA
- [x] P2.2 — Write `database.py` `init_db()` function that reads and executes `schema.sql` on startup; call from FastAPI lifespan
- [x] P2.3 — Write `database/migrations/` migration runner: each migration is a numbered `.sql` file; runner tracks applied migrations in a `_migrations` meta-table
- [x] P2.4 — Write `database/seeds/dev_seed.sql`: 2 admin users, 5 student users, 10 sample questions with options and tags, 2 sample exams, sample attempts and leaderboard entries
- [x] P2.5 — Verify: `python -m database.init` creates `qera.db`; all tables present; FTS5 index populated from seed; WAL journal file appears

---

## PHASE 3 — Auth Module
**Goal:** Register, login (student + admin), JWT middleware, role dependency — all endpoints working.
**Status:** ⬜ Not Started

- [ ] P3.1 — `backend/models/user_model.py`: raw SQLite CRUD — `create_user()`, `get_user_by_email()`, `get_user_by_id()`; parameterized queries only
- [ ] P3.2 — `backend/schemas/auth_schema.py`: Pydantic v2 models — `RegisterRequest`, `LoginRequest`, `UserOut`, `TokenOut`
- [ ] P3.3 — `backend/services/auth_service.py`: `register_user()` (unique email check → bcrypt.hash rounds=12 → INSERT), `login_user()` (fetch → bcrypt.verify → jwt.encode with exp; student=24h, admin=8h)
- [ ] P3.4 — `backend/middlewares/auth.py`: `get_current_user` FastAPI Depends — extract Bearer → `jwt.decode` → return user dict; `backend/middlewares/role.py`: `require_admin` Depends — checks `role==admin`, raises 403 otherwise
- [ ] P3.5 — `backend/routers/auth_router.py`: wire `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/admin/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`; apply slowapi rate limit (10/min) on login + register
- [ ] P3.6 — Verify: register → 201; duplicate email → 409; login → JWT token; wrong password → 401; `GET /me` with valid token → user object; `GET /me` without token → 401; admin login → role=admin in token

---

## PHASE 4 — Questions Module
**Goal:** Full CRUD for questions with options and tags; like and bookmark toggles; comment endpoints; AI pipeline hooks (duplicate, tag, difficulty) called on create.
**Status:** ⬜ Not Started

- [ ] P4.1 — `backend/models/question_model.py`: `create_question()`, `get_question_by_id()`, `list_questions(page,limit)`, `update_question()`, `delete_question()`, `toggle_like()` (atomic UPDATE likes_count), `toggle_bookmark()`; insert options and tags in same transaction
- [ ] P4.2 — `backend/schemas/question_schema.py`: `QuestionCreate`, `QuestionUpdate`, `QuestionOut` (with nested options + tags), `CommentOut`, `CommentCreate`
- [ ] P4.3 — `backend/services/question_service.py`: orchestrate create flow — validate → call `ai_service.check_duplicate()` → warn flag → call `ai_service.suggest_tags()` if tags=[] → call `ai_service.analyze_difficulty()` if difficulty unset → `question_model.create_question()` → return
- [ ] P4.4 — `backend/models/comment_model.py`: `create_comment()`, `get_comments_by_question()` (threaded: top-level + replies), `flag_comment()`
- [ ] P4.5 — `backend/routers/question_router.py`: wire all 10 endpoints from QERA.mem QUESTIONS section; auth Depends on mutating routes; owner-or-admin check on PUT/DELETE
- [ ] P4.6 — `backend/routers/comment_router.py`: wire `GET /{id}/comments`, `POST /{id}/comments`, `POST /{id}/comments/{cid}/reply`; moderation_filter auto-called on every comment POST
- [ ] P4.7 — Notification triggers: on new public question → insert notification for topic followers (stub for now: notify all students); on comment → notify question owner; on reply → notify comment author
- [ ] P4.8 — Verify: create MCQ question (all fields) → returns with AI-filled tags + difficulty; duplicate question → warning in response; like toggle idempotent; bookmark toggle; comment thread with reply; non-owner PUT → 403

---

## PHASE 5 — Exams Module
**Goal:** Exam CRUD, attempt flow (start → timer → submit → score → leaderboard insert), result retrieval.
**Status:** ⬜ Not Started

- [ ] P5.1 — `backend/models/exam_model.py`: `create_exam()`, `get_exam_by_id()` (with questions), `list_exams()`, `update_exam()`, `delete_exam()`, `create_attempt()`, `get_attempt()`, `submit_attempt()` (saves answers JSON, score, time), `get_result()`
- [ ] P5.2 — `backend/schemas/exam_schema.py`: `ExamCreate`, `ExamOut`, `AttemptStart`, `AttemptSubmit` (attempt_id, time_taken_seconds, answers dict), `ResultOut`
- [ ] P5.3 — `backend/services/exam_service.py`: `score_exam()` — iterate submitted answers vs correct_answer per question → compute score; enforce time constraint (time_taken_seconds ≤ duration_minutes×60 + 30s grace → reject if exceeded); determine attempt_number for this user+exam
- [ ] P5.4 — `backend/services/leaderboard_service.py`: `insert_leaderboard_entry()` (only if attempt_number==1); `recompute_ranks()` using SQLite RANK() window function — `UPDATE leaderboard SET rank = ...` via subquery; `get_exam_leaderboard()`, `get_global_leaderboard()`
- [ ] P5.5 — `backend/routers/exam_router.py`: wire all 10 endpoints from QERA.mem EXAMS section; `POST /generate` gated by `require_admin`
- [ ] P5.6 — Notification trigger: on exam submit (attempt_number==1) → notify exam creator with rank; on new public exam → notify all students
- [ ] P5.7 — Verify: create exam with 3 questions; start attempt → attempt_id returned; submit correct answers → score computed; second attempt → attempt_number=2, NOT in leaderboard; time exceeded → 422; result endpoint returns score+breakdown+rank

---

## PHASE 6 — Leaderboard Module
**Goal:** Global and per-exam leaderboard endpoints, correct ranking logic.
**Status:** ⬜ Not Started

- [ ] P6.1 — `backend/routers/leaderboard_router.py`: `GET /api/v1/leaderboard/global` (all students, sum of first-attempt scores, tiebreak by accuracy %), `GET /api/v1/leaderboard/exam/{examId}` (per-exam, score DESC → time ASC → submitted_at ASC)
- [ ] P6.2 — `backend/models/leaderboard_model.py`: `get_global_leaderboard()` — JOIN users+leaderboard+exam_attempts; compute accuracy = (correct/total_attempted)×100; `get_exam_leaderboard(exam_id)`
- [ ] P6.3 — Rank caching: after `recompute_ranks()` in Phase 5, ranks stored as INTEGER in leaderboard table; re-triggered on every new first-attempt submission for that exam
- [ ] P6.4 — Verify: leaderboard returns correct order; tie scenario (same score) breaks by time; global leaderboard shows profile stats (Global Rank, Exams Attended, Accuracy %)

---

## PHASE 7 — User Profile & Bookmarks
**Goal:** Profile view with stats, profile update, bookmarked questions, user's own questions/exams.
**Status:** ⬜ Not Started

- [ ] P7.1 — `backend/models/user_model.py` additions: `get_user_profile_stats()` (Global Rank, Exams Attended COUNT, Exams Created COUNT, Questions Created COUNT, Accuracy %), `update_user()`, `get_user_bookmarks()`, `get_user_questions()`, `get_user_exams()`
- [ ] P7.2 — `backend/routers/user_router.py`: wire `GET /{id}/profile`, `PUT /me`, `GET /me/bookmarks`, `GET /me/exams`, `GET /me/questions`, `GET /me/notifications`, `PUT /me/notifications/{id}/read`
- [ ] P7.3 — Avatar upload: `PUT /me` accepts optional `avatar_url` text field (URL); no file upload in this phase
- [ ] P7.4 — `backend/routers/notification_router.py`: `GET /api/v1/notifications/`, `PUT /api/v1/notifications/{id}/read`, `PUT /api/v1/notifications/read-all`
- [ ] P7.5 — Verify: profile stats accurate after exam attempts; bookmarks list correct; notifications mark-read works; profile update persists

---

## PHASE 8 — Comments & Notifications (Completeness Pass)
**Goal:** Ensure all comment moderation logic and notification triggers from all modules are wired end-to-end.
**Status:** ⬜ Not Started

- [ ] P8.1 — Confirm all notification INSERT triggers exist: new_exam, new_question, comment_on_question, reply_to_comment, rank_change, admin_announcement
- [ ] P8.2 — Admin flag workflow: `POST /api/v1/admin/comments/{id}/flag` sets `is_flagged=1`; flagged comments hidden in public `GET /{id}/comments` (filter `is_flagged=0`); admin sees all
- [ ] P8.3 — `backend/services/notification_service.py`: `create_notification(user_id, type, message, reference_id, reference_type)` helper used by all modules
- [ ] P8.4 — Polling contract: `GET /notifications` returns unread count + list; sorted by created_at DESC; frontend polls every 30s
- [ ] P8.5 — Verify: full notification flow — student A comments on student B's question → B gets notification; student A replies to B's comment → B gets reply notification; admin flags comment → hidden from public feed

---

## PHASE 9 — Search Module
**Goal:** Keyword search via FTS5, filters, semantic search fallback stub.
**Status:** ⬜ Not Started

- [ ] P9.1 — `backend/models/search_model.py`: `keyword_search_questions(q, tags, difficulty, type, page)` — FTS5 MATCH query on questions_fts virtual table JOIN questions; apply tag/difficulty/type filters; `keyword_search_exams(q)`
- [ ] P9.2 — `backend/routers/search_router.py`: `GET /api/v1/search/questions?q=&tags=&difficulty=&type=&mode=`, `GET /api/v1/search/exams?q=`; if mode=semantic OR keyword returns <3 results → call `ai_service.semantic_search()`
- [ ] P9.3 — FTS5 sync: on every `INSERT`/`UPDATE`/`DELETE` to questions table, keep `questions_fts` virtual table in sync via triggers in schema.sql
- [ ] P9.4 — Verify: search "python" returns questions containing that word; tag filter narrows results; difficulty filter works; fewer than 3 keyword results triggers semantic fallback (returns stub array if AI not yet wired)

---

## PHASE 10 — AI Services Module
**Goal:** All 10 ai-services implemented; wired into backend via `ai_service.py` gateway; all auto-triggers active.
**Status:** ⬜ Not Started

- [ ] P10.1 — `backend/ai_service.py`: central gateway module; each function calls the corresponding ai-services Python module; handles errors gracefully (AI failure must NEVER block core CRUD — wrap in try/except, return safe defaults)
- [ ] P10.2 — `ai-services/duplicate_detector.py`: embed question text; cosine similarity against existing questions; return `{is_duplicate, confidence, similar_ids[]}`; threshold >0.88
- [ ] P10.3 — `ai-services/tag_generator.py`: prompt LLM with question title+description; return 3-7 tag strings
- [ ] P10.4 — `ai-services/difficulty_analyzer.py`: prompt LLM with question content; return `{difficulty: easy|medium|hard, confidence: float}`
- [ ] P10.5 — `ai-services/explanation_generator.py`: given question+options+correct_answer → return plain-text explanation string
- [ ] P10.6 — `ai-services/question_generator.py`: given topic/text/PDF content → return list of question dicts matching QuestionCreate shape
- [ ] P10.7 — `ai-services/exam_generator.py`: given topic+count+difficulty_dist+duration → return full exam object with questions; admin only
- [ ] P10.8 — `ai-services/moderation_filter.py`: given text → return `{is_toxic, is_spam, reason}`; called auto on every comment POST and optional on question create
- [ ] P10.9 — `ai-services/recommendation_engine.py`: given user attempt history + bookmarks → return ranked list of `{exam_id|question_id, reason}`
- [ ] P10.10 — `ai-services/study_assistant.py`: conversational NL QA; given `{question, optional question_id}` → fetch question context if id given → return answer string; `ai-services/semantic_search.py`: embed query → nearest-neighbor against question embeddings → return ranked question_id list

---

## PHASE 11 — Admin Module
**Goal:** All admin-only endpoints working: user management, content moderation, exam generation, report handling, batch AI moderation.
**Status:** ⬜ Not Started

- [ ] P11.1 — `backend/routers/admin_router.py`: prefix `/api/v1/admin`; all routes gated by `require_admin` Depends
- [ ] P11.2 — User management endpoints: `GET /admin/users` (paginated list), `PUT /admin/users/{id}/suspend` (set suspended flag), `DELETE /admin/users/{id}` (soft delete or hard delete with cascade)
- [ ] P11.3 — Content moderation endpoints: `GET /admin/questions/flagged`, `DELETE /admin/questions/{id}`, `GET /admin/comments/flagged`, `DELETE /admin/comments/{id}`, `PUT /admin/comments/{id}/unflag`
- [ ] P11.4 — Exam management: `GET /admin/exams` (all exams including private), `POST /api/v1/exams/generate` (already in exam router, admin-gated) — wire to `exam_generator.py`
- [ ] P11.5 — Batch AI moderation: `POST /admin/moderate/batch` — fetch all unmoderated questions/comments → run `moderation_filter` on each → auto-flag toxic content → return summary report
- [ ] P11.6 — Verify: student token on any `/admin/*` route → 403; admin can suspend user; batch moderation processes items and returns count; flagged questions hidden from public list

---

## PHASE 12 — Frontend: Scaffold & Auth UI
**Goal:** React app routing complete, auth pages (login/register), JWT storage, axios interceptor, protected route wrapper.
**Status:** ⬜ Not Started

- [ ] P12.1 — `frontend/src/context/AuthContext.jsx`: store `{user, token}`; expose `login()`, `logout()`, `register()`; persist token to localStorage; read on mount
- [ ] P12.2 — `frontend/src/services/api.js`: axios instance with `baseURL=/api/v1`; request interceptor adds `Authorization: Bearer <token>`; response interceptor handles 401 → auto logout
- [ ] P12.3 — `frontend/src/components/common/ProtectedRoute.jsx`: wraps routes requiring auth; redirects to /login if no token; `AdminRoute.jsx`: additionally checks role=admin
- [ ] P12.4 — `frontend/src/pages/auth/LoginPage.jsx`: email+password form → `POST /auth/login` → store token → redirect to /dashboard; show error on 401
- [ ] P12.5 — `frontend/src/pages/auth/RegisterPage.jsx`: name+email+password → `POST /auth/register` → auto-login → redirect to /dashboard
- [ ] P12.6 — `frontend/src/pages/dashboard/DashboardPage.jsx`: welcome, recent questions, recent exams, stats cards (Exams Attended, Questions Created, Global Rank, Accuracy %)
- [ ] P12.7 — `frontend/src/components/layout/Navbar.jsx`: logo, nav links, user avatar+dropdown (profile/logout); notification bell with unread badge (polling every 30s)

---

## PHASE 13 — Frontend: Questions UI
**Goal:** Question list, detail view, create form with AI feedback, like/bookmark, comments.
**Status:** ⬜ Not Started

- [ ] P13.1 — `QuestionsPage.jsx`: paginated list; search bar + filters (difficulty, type, tags); keyword/semantic toggle; each card shows title, tags, difficulty badge, likes
- [ ] P13.2 — `QuestionDetailPage.jsx`: full question with options; like button (toggle); bookmark button (toggle); AI explanation panel (expandable, calls `POST /ai/explain`); comments thread
- [ ] P13.3 — `CreateQuestionPage.jsx`: multi-step form — type selector → fields for title/description/options/correct_answer → on submit: show duplicate warning if detected → show AI-suggested tags (editable) → show AI-predicted difficulty (editable) → submit
- [ ] P13.4 — `CommentSection.jsx` component: threaded display (top-level + indented replies); add comment form; reply button inline; show flagged state (hidden text) for non-admin
- [ ] P13.5 — `frontend/src/hooks/useQuestions.js`: custom hook for paginated fetch, optimistic like/bookmark toggle
- [ ] P13.6 — Verify: create question end-to-end with AI suggestions; duplicate question shows warning modal with "Override & Submit" option; comments and replies render correctly

---

## PHASE 14 — Frontend: Exams UI
**Goal:** Exam list, detail, create, attend (timer), result page.
**Status:** ⬜ Not Started

- [ ] P14.1 — `ExamsPage.jsx`: list with search, public filter; exam cards showing title, question count, duration, creator
- [ ] P14.2 — `ExamDetailPage.jsx`: exam metadata + question preview list; "Start Exam" button → POST attempt → navigate to attend page
- [ ] P14.3 — `CreateExamPage.jsx`: title/description/duration/marks fields; question picker (search question bank, add to exam with marks); randomize toggle; publish toggle
- [ ] P14.4 — `AttendExamPage.jsx`: countdown timer (duration_minutes×60 seconds); question navigator; answer selector per question type (MCQ radio, true/false toggle, short answer text); auto-submit on timer=0 OR manual submit; confirm dialog on nav-away; POST /exams/{id}/submit
- [ ] P14.5 — `ExamResultPage.jsx`: score + total; per-question breakdown (your answer vs correct answer); AI explanation per question (expandable); rank badge; link to leaderboard
- [ ] P14.6 — `ExamLeaderboardPage.jsx` (embedded in ExamDetail and standalone): table of top scorers for that exam; highlight current user's row
- [ ] P14.7 — Verify: timer auto-submits; refreshing attend page mid-exam retains attempt_id from state; result page shows all breakdown; second attempt allowed but not on leaderboard

---

## PHASE 15 — Frontend: Leaderboard & Profile UI
**Goal:** Global leaderboard, per-exam leaderboard, user profile pages, bookmarks page, notifications page.
**Status:** ⬜ Not Started

- [ ] P15.1 — `GlobalLeaderboardPage.jsx`: table ranked by total score; columns: Rank, Name, Exams Attended, Accuracy %, Total Score; search by name; highlight logged-in user
- [ ] P15.2 — `ProfilePage.jsx`: public view — avatar, bio, stats (Global Rank, Exams Attended, Exams Created, Questions Created, Accuracy %); tabs for Created Questions / Created Exams
- [ ] P15.3 — `MyProfilePage.jsx` (`/profile/me`): same as above + edit button → inline edit for name/bio/avatar_url
- [ ] P15.4 — `BookmarksPage.jsx`: list of bookmarked questions; remove bookmark; click → QuestionDetail
- [ ] P15.5 — `NotificationsPage.jsx`: list of all notifications; mark single read; "Mark All Read" button; type icons for different notification types

---

## PHASE 16 — Frontend: Admin UI
**Goal:** Admin dashboard, user management, content moderation, exam management.
**Status:** ⬜ Not Started

- [ ] P16.1 — `admin/AdminDashboardPage.jsx`: stats overview — total users, total questions, total exams, flagged content count, recent activity feed
- [ ] P16.2 — `admin/UserManagementPage.jsx`: paginated user table; search; suspend/unsuspend toggle; delete with confirm modal
- [ ] P16.3 — `admin/ContentModerationPage.jsx`: tabs for Flagged Questions / Flagged Comments; each item shows content + reporter context; Approve (unflag) / Delete buttons
- [ ] P16.4 — `admin/ExamManagementPage.jsx`: list all exams (including private); edit/delete any; "Generate AI Exam" form — topic, count, difficulty distribution, duration → POST /exams/generate
- [ ] P16.5 — `admin/BatchModerationPage.jsx`: "Run Batch AI Moderation" button → POST /admin/moderate/batch → display summary (flagged count, items reviewed)

---

## PHASE 17 — Frontend: AI Features UI
**Goal:** Study assistant chat, AI question generator, recommendation panel, difficulty/tag UI feedback.
**Status:** ⬜ Not Started

- [ ] P17.1 — `StudyAssistantPage.jsx`: chat-style UI; user types question (optionally linked to a question from bank via search); sends `POST /ai/study-assistant`; displays conversational reply; maintains message history in local state for the session
- [ ] P17.2 — `AIQuestionGeneratorPage.jsx` (student): input topic/paste text; select count, type, difficulty; generates preview of questions; each question can be edited before bulk-saving to question bank
- [ ] P17.3 — `RecommendationsPanel.jsx` (component on Dashboard): calls `POST /ai/recommend` on dashboard load; shows ranked list of recommended exams and questions with reason strings
- [ ] P17.4 — AI tag chips on CreateQuestionPage: display suggested tags as clickable chips (add/remove); difficulty badge shows confidence score as tooltip
- [ ] P17.5 — Duplicate warning modal: shown when `is_duplicate=true` on question create; shows confidence %, links to similar questions; "Override & Submit" or "Cancel" actions

---

## PHASE 18 — Integration, QA & Hardening
**Goal:** End-to-end testing, security audit, performance, error handling, deployment readiness.
**Status:** ⬜ Not Started

- [ ] P18.1 — End-to-end flow test: new student registers → creates question → creates exam → another student attends → leaderboard updates → notifications arrive → admin reviews flagged content
- [ ] P18.2 — Security audit: confirm all `/admin/*` routes reject student tokens; confirm no raw SQL string interpolation anywhere; confirm CORS blocks non-frontend origins; confirm bcrypt used (no plain hashes); rate limit on auth tested
- [ ] P18.3 — Error handling pass: all FastAPI routers return proper HTTP codes (400 validation, 401 unauth, 403 forbidden, 404 not found, 422 unprocessable, 500 with generic message); frontend shows user-friendly error toasts for each
- [ ] P18.4 — AI failure resilience: confirm every `ai_service.py` call is wrapped in try/except; question create succeeds even if AI services are down (tags default to [], difficulty defaults to "medium")
- [ ] P18.5 — SQLite performance: add indexes on `questions.user_id`, `exam_attempts.exam_id`, `exam_attempts.user_id`, `leaderboard.exam_id`, `notifications.user_id`; verify FTS5 queries use index
- [ ] P18.6 — README.md: local dev setup instructions (Python venv, npm install, env vars, `python init_db.py`, uvicorn + vite commands); environment variable reference table

---

## TASK COUNT REFERENCE

| Phase | Total Tasks |
|-------|------------|
| P1 | 6 |
| P2 | 5 |
| P3 | 6 |
| P4 | 8 |
| P5 | 7 |
| P6 | 4 |
| P7 | 5 |
| P8 | 5 |
| P9 | 4 |
| P10 | 10 |
| P11 | 6 |
| P12 | 7 |
| P13 | 6 |
| P14 | 7 |
| P15 | 5 |
| P16 | 5 |
| P17 | 5 |
| P18 | 6 |
| **Total** | **106** |

---

## HOW TO USE THIS FILE (for humans and AI agents)

**Updating progress:** When a task is completed, change `- [ ]` to `- [x]` and update the Phase Overview table's "Tasks Done" count and status emoji.

**Status emojis:**
- ⬜ = Not started (0 tasks done)
- 🔄 = In progress (≥1 task done, not all done)
- ✅ = Complete (all tasks in phase done)

**For AI agents — session start protocol:**
1. Read this file fully.
2. Find the first phase that is 🔄 In Progress — continue from the first unchecked `- [ ]` task in it.
3. If no phase is 🔄, find the first ⬜ phase and start from P1.1.
4. After completing each task, update its checkbox and the phase overview table before moving on.
5. Never skip a task. Never re-do a ✅ task.
6. If a task depends on an uncompleted prior task, stop and flag it.

**For humans:** Check the Phase Overview table at the top for a quick snapshot of where the build stands.
