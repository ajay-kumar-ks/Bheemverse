# QERA — AI-Powered Exam & Question Platform
### Complete Project Reference Document
> This document is the single source of truth for the QERA platform. It is written to be fully understood by both human developers and AI agents working on this codebase.

---

## Table of Contents

1. [Project Summary](#1-project-summary)
2. [Goals & Purpose](#2-goals--purpose)
3. [User Roles & Permissions](#3-user-roles--permissions)
4. [System Architecture Overview](#4-system-architecture-overview)
5. [Folder Structure](#5-folder-structure)
6. [Database Schema](#6-database-schema)
7. [Backend Modules & API Design](#7-backend-modules--api-design)
8. [Frontend Modules](#8-frontend-modules)
9. [AI Services](#9-ai-services)
10. [Feature Specifications](#10-feature-specifications)
11. [Business Logic & Rules](#11-business-logic--rules)
12. [Data Flow Diagrams](#12-data-flow-diagrams)
13. [Security & Auth](#13-security--auth)
14. [Notification System](#14-notification-system)
15. [Search System](#15-search-system)
16. [Leaderboard System](#16-leaderboard-system)
17. [Future Scope](#17-future-scope)
18. [Glossary](#18-glossary)

---

## 1. Project Summary

**QERA** is a collaborative, AI-powered web platform for students to create, share, attend, and discuss exams and questions. It merges an online examination engine, a community question bank, competitive leaderboards, and multiple AI-driven automation features into a single learning ecosystem.

**Core value proposition:**
- Students both *consume* and *contribute* educational content.
- AI reduces manual work (question generation, tagging, moderation, explanation).
- Competitive ranking motivates consistent participation.
- The architecture is designed to be agent-friendly — AI agents can read, generate, moderate, and analyze content through well-defined module boundaries.

---

## 2. Goals & Purpose

| # | Goal |
|---|------|
| 1 | Allow students to create and share questions |
| 2 | Allow students to create and publish public exams |
| 3 | Build a collaborative, searchable question bank |
| 4 | Enable competitive learning via rankings and leaderboards |
| 5 | Use AI to automate question/exam generation |
| 6 | Use AI for search, moderation, recommendations, and difficulty analysis |
| 7 | Design the system in an AI-agent-friendly, modular architecture |

---

## 3. User Roles & Permissions

### 3.1 Student

The primary user of the platform. Students self-register and interact with all public content.

**Capabilities:**

| Category | Actions |
|----------|---------|
| Auth | Register, login, logout, update profile |
| Questions | Create, view, search, like, bookmark, comment, reply |
| Exams | Create, publish, attend, view results |
| Social | Comment on questions, reply to comments, follow discussions |
| Leaderboard | View global and per-exam leaderboards |
| Notifications | Receive and view notifications |
| Profile | View own and others' public profiles |
| AI Tools | Use AI Study Assistant, view AI-generated explanations |

**Restrictions:**
- Cannot access admin dashboard
- Cannot delete/moderate other students' content
- Cannot generate platform-wide exams

---

### 3.2 Admin

Platform managers with elevated privileges.

**Capabilities:**

| Category | Actions |
|----------|---------|
| Auth | Login to admin dashboard |
| Users | View, suspend, delete user accounts |
| Questions | Delete, edit, or flag questions |
| Comments | Moderate, delete comments |
| Exams | Manage all exams, generate AI/random exams platform-wide |
| Reports | Handle reported content |
| Platform | Monitor activity, configure settings |
| AI | Trigger AI-based exam generation, moderation scans |

---

## 4. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│              React + Tailwind CSS (SPA)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐    │
│  │  Auth UI │ │Exam Pages│ │Question  │ │  Dashboard   │    │
│  │          │ │          │ │  Pages   │ │  & Profile   │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘    │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (JSON over HTTPS)
┌─────────────────────────▼───────────────────────────────────┐
│                       BACKEND LAYER                         │
│              Node.js + Express.js (MVC Pattern)             │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌─────────┐    │
│  │  Auth  │ │Question│ │  Exam  │ │  User  │ │Leaderbd │    │
│  │ Module │ │ Module │ │ Module │ │ Module │ │ Module  │    │
│  └────────┘ └────────┘ └────────┘ └────────┘ └─────────┘    │
│  ┌────────┐ ┌────────┐ ┌────────┐                           │
│  │   AI   │ │Notific.│ │ Search │                           │
│  │ Module │ │ Module │ │ Module │                           │
│  └────────┘ └────────┘ └────────┘                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴────────────────┐
          │                                │
┌─────────▼──────────┐          ┌──────────▼─────────┐
│    MySQL Database  │          │    AI Services     │
│  (Primary Storage) │          │  (External / LLM)  │
└────────────────────┘          └────────────────────┘
```

**Key design principles:**
- MVC pattern on the backend — Controllers handle HTTP, Services contain business logic, Models interface with DB.
- AI features are isolated in a dedicated `ai-services/` module to allow independent scaling or swapping.
- JWT-based stateless auth — no server-side sessions.
- The system is modular enough for AI agents to target individual modules without side effects.

---

## 5. Folder Structure

```
qera/
│
├── frontend/                        # React SPA
│   ├── public/
│   ├── src/
│   │   ├── assets/                  # Images, icons, fonts
│   │   ├── components/              # Reusable UI components
│   │   │   ├── common/              # Buttons, inputs, modals
│   │   │   ├── question/            # Question card, form, viewer
│   │   │   ├── exam/                # Exam card, timer, result
│   │   │   ├── leaderboard/         # Leaderboard table, rank badge
│   │   │   └── layout/              # Navbar, sidebar, footer
│   │   ├── pages/                   # Route-level page components
│   │   │   ├── auth/                # Login, Register
│   │   │   ├── dashboard/           # Student dashboard
│   │   │   ├── exams/               # Exam list, attend, result
│   │   │   ├── questions/           # Question list, create, view
│   │   │   ├── leaderboard/         # Global & per-exam boards
│   │   │   ├── profile/             # Own and public profiles
│   │   │   └── admin/               # Admin dashboard pages
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── context/                 # Auth context, theme context
│   │   ├── services/                # Axios API service functions
│   │   ├── utils/                   # Helper functions
│   │   └── App.jsx                  # Router setup
│   └── package.json
│
├── backend/                         # Node.js + Express API
│   ├── src/
│   │   ├── config/                  # DB config, env config, JWT config
│   │   ├── controllers/             # Route handler functions
│   │   │   ├── authController.js
│   │   │   ├── questionController.js
│   │   │   ├── examController.js
│   │   │   ├── userController.js
│   │   │   ├── leaderboardController.js
│   │   │   ├── aiController.js
│   │   │   ├── notificationController.js
│   │   │   └── searchController.js
│   │   ├── services/                # Business logic layer
│   │   │   ├── authService.js
│   │   │   ├── questionService.js
│   │   │   ├── examService.js
│   │   │   ├── userService.js
│   │   │   ├── leaderboardService.js
│   │   │   ├── aiService.js
│   │   │   ├── notificationService.js
│   │   │   └── searchService.js
│   │   ├── models/                  # MySQL query functions (no ORM)
│   │   │   ├── userModel.js
│   │   │   ├── questionModel.js
│   │   │   ├── examModel.js
│   │   │   └── ...
│   │   ├── routes/                  # Express route definitions
│   │   │   ├── authRoutes.js
│   │   │   ├── questionRoutes.js
│   │   │   ├── examRoutes.js
│   │   │   └── ...
│   │   ├── middlewares/             # Auth guard, role guard, error handler
│   │   │   ├── authMiddleware.js
│   │   │   ├── roleMiddleware.js
│   │   │   └── errorHandler.js
│   │   ├── utils/                   # JWT helper, password hash, validators
│   │   └── app.js                   # Express app setup
│   ├── server.js                    # Entry point
│   └── package.json
│
├── ai-services/                     # AI feature implementations
│   ├── questionGenerator.js         # Generate questions from text/topic
│   ├── examGenerator.js             # Build full exams automatically
│   ├── duplicateDetector.js         # Semantic similarity check
│   ├── difficultyAnalyzer.js        # Predict difficulty level
│   ├── explanationGenerator.js      # Generate answer explanations
│   ├── tagGenerator.js              # Auto-generate tags/topics
│   ├── recommendationEngine.js      # Personalized recommendations
│   ├── studyAssistant.js            # Conversational Q&A assistant
│   ├── moderationFilter.js          # Toxicity and spam detection
│   └── semanticSearch.js            # Embedding-based search
│
├── database/
│   ├── schema.sql                   # Full database schema
│   ├── seeds/                       # Sample/test data
│   └── migrations/                  # Schema version changes
│
├── docs/
│   ├── QERA.md                      # This file — master reference
│   ├── api-reference.md             # Full API endpoint docs
│   └── ai-agent-guide.md            # Guide for AI agents working on this project
│
└── README.md                        # Quick start guide
```

---

## 6. Database Schema

### Entity Relationship Summary

```
users ──────────┬──── questions ──────── question_options
                │          │
                │          ├──── comments
                │          │         └──── comments (replies, self-ref)
                │          ├──── bookmarks
                │          ├──── tags (via question_tags join table)
                │          └──── exam_questions
                │
                ├──── exams ─────────── exam_questions
                │          └──────────── exam_attempts ──── leaderboard
                │
                └──── notifications
```

---

### Table Definitions

#### `users`
|     Column    | Type | Notes |
|---------------|------|-------|
| id            | INT PK AUTO_INCREMENT | |
| name          | VARCHAR(100) | |
| email         | VARCHAR(150) UNIQUE | |
| password_hash | VARCHAR(255) | bcrypt hashed |
| role          | ENUM('student','admin') | Default: student |
| avatar_url    | VARCHAR(255) | Optional |
| bio           | TEXT | Optional |
| created_at    | DATETIME | |
| updated_at    | DATETIME | |

---

#### `questions`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| user_id | INT FK → users.id | Creator |
| title | VARCHAR(255) | |
| description | TEXT | Full question body |
| type | ENUM('mcq','true_false','short_answer','descriptive') | |
| correct_answer | TEXT | For MCQ: option id; for others: text |
| difficulty | ENUM('easy','medium','hard') | Can be AI-predicted |
| explanation | TEXT | AI or manually written |
| is_public | BOOLEAN | Default: true |
| likes_count | INT | Denormalized counter |
| created_at | DATETIME | |
| updated_at | DATETIME | |

---

#### `question_options`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| question_id | INT FK → questions.id | |
| option_text | TEXT | |
| option_order | INT | Display order (1–4) |

---

#### `tags`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| name | VARCHAR(100) UNIQUE | |

#### `question_tags` (join table)
| Column | Type |
|--------|------|
| question_id | INT FK |
| tag_id | INT FK |

---

#### `exams`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| user_id | INT FK → users.id | Creator |
| title | VARCHAR(255) | |
| description | TEXT | |
| duration_minutes | INT | Timer limit |
| total_marks | INT | Sum of all question marks |
| is_public | BOOLEAN | |
| randomize_order | BOOLEAN | Shuffle question order |
| created_at | DATETIME | |
| updated_at | DATETIME | |

---

#### `exam_questions`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| exam_id | INT FK → exams.id | |
| question_id | INT FK → questions.id | |
| marks | INT | Marks for this question in this exam |
| question_order | INT | Display order |

---

#### `exam_attempts`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| exam_id | INT FK → exams.id | |
| user_id | INT FK → users.id | |
| attempt_number | INT | 1 = first attempt |
| score | INT | |
| total_marks | INT | Snapshot at time of attempt |
| time_taken_seconds | INT | Actual time used |
| submitted_at | DATETIME | |
| answers | JSON | Map of question_id → given_answer |

---

#### `leaderboard`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| exam_id | INT FK → exams.id | |
| user_id | INT FK → users.id | |
| attempt_id | INT FK → exam_attempts.id | First attempt only |
| score | INT | |
| time_taken_seconds | INT | |
| rank | INT | Computed dynamically or cached |

---

#### `bookmarks`
| Column | Type |
|--------|------|
| user_id | INT FK → users.id |
| question_id | INT FK → questions.id |
| created_at | DATETIME |

---

#### `comments`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| question_id | INT FK → questions.id | |
| user_id | INT FK → users.id | |
| parent_id | INT FK → comments.id | NULL = top-level; set = reply |
| content | TEXT | |
| is_flagged | BOOLEAN | AI or user-flagged |
| created_at | DATETIME | |

---

#### `notifications`
| Column | Type | Notes |
|--------|------|-------|
| id | INT PK AUTO_INCREMENT | |
| user_id | INT FK → users.id | Recipient |
| type | VARCHAR(50) | e.g. 'new_exam', 'comment_reply', 'leaderboard_update' |
| message | TEXT | |
| reference_id | INT | ID of the related entity |
| reference_type | VARCHAR(50) | e.g. 'exam', 'question', 'comment' |
| is_read | BOOLEAN | Default: false |
| created_at | DATETIME | |

---

## 7. Backend Modules & API Design

> All routes are prefixed with `/api/v1`. All protected routes require `Authorization: Bearer <token>` header.

---

### Auth Module — `/api/v1/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | Public | Register new student account |
| POST | `/login` | Public | Login, returns JWT |
| POST | `/admin/login` | Public | Admin login, returns JWT with admin role |
| GET | `/me` | Student | Get current user info from token |
| POST | `/logout` | Student | Invalidate session (client-side token clear) |

**Register payload:**
```json
{
  "name": "string",
  "email": "string",
  "password": "string"
}
```

**Login response:**
```json
{
  "token": "jwt_string",
  "user": { "id": 1, "name": "...", "role": "student" }
}
```

---

### Question Module — `/api/v1/questions`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Public | List all public questions (paginated) |
| GET | `/:id` | Public | Get single question with options |
| POST | `/` | Student | Create a new question |
| PUT | `/:id` | Student (owner) | Update own question |
| DELETE | `/:id` | Student (owner) / Admin | Delete question |
| POST | `/:id/like` | Student | Toggle like on question |
| POST | `/:id/bookmark` | Student | Toggle bookmark |
| GET | `/:id/comments` | Public | Get comments for question |
| POST | `/:id/comments` | Student | Add comment |
| POST | `/:id/comments/:commentId/reply` | Student | Reply to comment |

**Create question payload:**
```json
{
  "title": "string",
  "description": "string",
  "type": "mcq | true_false | short_answer | descriptive",
  "options": [
    { "option_text": "string", "option_order": 1 }
  ],
  "correct_answer": "string",
  "difficulty": "easy | medium | hard",
  "explanation": "string",
  "tags": ["tag1", "tag2"]
}
```

---

### Exam Module — `/api/v1/exams`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Public | List all public exams |
| GET | `/:id` | Public | Get exam details and questions |
| POST | `/` | Student | Create exam |
| PUT | `/:id` | Student (owner) / Admin | Update exam |
| DELETE | `/:id` | Student (owner) / Admin | Delete exam |
| POST | `/:id/attempt` | Student | Start exam attempt |
| POST | `/:id/submit` | Student | Submit exam answers |
| GET | `/:id/result/:attemptId` | Student | View attempt result |
| GET | `/:id/leaderboard` | Public | View per-exam leaderboard |
| POST | `/generate` | Admin | AI/random exam generation |

**Submit exam payload:**
```json
{
  "attempt_id": 1,
  "time_taken_seconds": 3420,
  "answers": {
    "question_id_1": "selected_option_id_or_text",
    "question_id_2": "true"
  }
}
```

---

### User Module — `/api/v1/users`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/:id/profile` | Public | View public profile |
| PUT | `/me` | Student | Update own profile |
| GET | `/me/bookmarks` | Student | Get bookmarked questions |
| GET | `/me/exams` | Student | Get created/attended exams |
| GET | `/me/questions` | Student | Get created questions |
| GET | `/me/notifications` | Student | Get notifications |
| PUT | `/me/notifications/:id/read` | Student | Mark notification as read |

---

### Leaderboard Module — `/api/v1/leaderboard`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/global` | Public | Global student ranking |
| GET | `/exam/:examId` | Public | Per-exam leaderboard |

---

### AI Module — `/api/v1/ai`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/generate-questions` | Student | Generate questions from topic/text |
| POST | `/generate-exam` | Admin | Generate full exam automatically |
| POST | `/explain` | Student | Get explanation for a question |
| POST | `/check-duplicate` | Student | Check if question is duplicate |
| POST | `/suggest-tags` | Student | Get tag suggestions for question |
| POST | `/analyze-difficulty` | Student | Predict difficulty of question |
| POST | `/recommend` | Student | Get personalized exam/question recommendations |
| POST | `/study-assistant` | Student | Ask study assistant a question |

---

### Search Module — `/api/v1/search`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/questions` | Public | Search questions (keyword / semantic) |
| GET | `/exams` | Public | Search exams |

**Query params:** `?q=keyword&tags=math,algebra&difficulty=hard&type=mcq&mode=semantic`

---

### Notification Module — `/api/v1/notifications`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Student | Get all notifications |
| PUT | `/:id/read` | Student | Mark as read |
| PUT | `/read-all` | Student | Mark all as read |

---

## 8. Frontend Modules

### Pages & Routes

| Route | Page | Auth Required |
|-------|------|---------------|
| `/` | Landing / Home | No |
| `/login` | Login | No |
| `/register` | Register | No |
| `/dashboard` | Student Dashboard | Student |
| `/questions` | Question Bank (browse) | No |
| `/questions/create` | Create Question | Student |
| `/questions/:id` | View Question | No |
| `/exams` | Exam List | No |
| `/exams/create` | Create Exam | Student |
| `/exams/:id` | Exam Detail | No |
| `/exams/:id/attend` | Attend Exam | Student |
| `/exams/:id/result/:attemptId` | Result Page | Student |
| `/leaderboard` | Global Leaderboard | No |
| `/leaderboard/exam/:id` | Per-Exam Leaderboard | No |
| `/profile/:userId` | Public Profile | No |
| `/profile/me` | Own Profile | Student |
| `/bookmarks` | Bookmarked Questions | Student |
| `/notifications` | Notifications | Student |
| `/admin/*` | Admin Dashboard | Admin |

---

### Key UI Components

**Exam Attend Page — critical behavior:**
- Timer counts down from `duration_minutes`
- Auto-submits when timer hits 0
- Questions displayed in order (randomized if `randomize_order = true`)
- No navigation away without confirmation

**Result Page:**
- Score, percentage, time taken
- Per-question breakdown: user answer vs correct answer
- AI-generated explanation shown per question
- Leaderboard position shown

---

## 9. AI Services

Each AI service is a standalone module in `ai-services/`. They are called by the backend's `aiService.js`, which acts as a gateway.

---

### 9.1 Question Generator

**Input:** Topic name OR paragraph text OR uploaded notes/PDF content
**Output:** Array of question objects (same shape as the question creation payload)
**Supported types:** MCQ, True/False, Descriptive
**How it works:** Sends structured prompt to LLM with question count, type, and difficulty instructions. Parses JSON response into question objects.

---

### 9.2 Exam Generator

**Input:** Topic, question count, difficulty distribution (e.g., 40% easy, 40% medium, 20% hard), duration
**Output:** Full exam object with questions selected from the question bank OR AI-generated questions
**Admin only**

---

### 9.3 Duplicate Detector

**Input:** New question text
**Output:** Boolean `is_duplicate`, confidence score, list of similar existing question IDs
**How it works:** Computes text embeddings for the new question and compares against stored embeddings using cosine similarity. Flags if similarity > threshold (e.g., 0.88).
**When called:** Automatically on every question creation before saving.

---

### 9.4 Difficulty Analyzer

**Input:** Question title + description + options
**Output:** `easy | medium | hard` with confidence score
**How it works:** LLM prompt that evaluates vocabulary complexity, number of steps required to solve, and ambiguity.

---

### 9.5 Explanation Generator

**Input:** Question object (title, description, options, correct answer)
**Output:** Plain-text explanation covering why the correct answer is correct and why each wrong option is wrong
**When called:** On demand (student clicks "Explain") or during question creation if no explanation is provided.

---

### 9.6 Tag Generator

**Input:** Question title + description
**Output:** Array of 3–7 relevant tags/topics
**When called:** Automatically on question creation if no tags are provided, or on demand.

---

### 9.7 Recommendation Engine

**Input:** User's exam history, accuracy per topic, bookmarks
**Output:** Ranked list of recommended exams and questions with reason strings
**How it works:** Builds a weak-topic profile from attempt history, then queries questions/exams matching those topics.

---

### 9.8 Study Assistant

**Input:** Student's natural language question
**Output:** Conversational text answer, may reference relevant questions from the question bank
**Context:** Can optionally receive a question ID to answer questions *about* a specific question.

---

### 9.9 Moderation Filter

**Input:** Comment text OR question title/description
**Output:** `{ is_toxic: boolean, is_spam: boolean, reason: string }`
**When called:** 
- Every new comment before saving
- Optionally on question creation
- Admin can trigger batch scan

---

### 9.10 Semantic Search

**Input:** Natural language query string
**Output:** Ranked list of question IDs
**How it works:** Embeds the query and performs nearest-neighbor search against stored question embeddings.

---

## 10. Feature Specifications

### 10.1 Question Creation Flow

```
Student fills question form
    → Frontend validates (required fields, option count for MCQ)
    → POST /api/v1/questions
    → Backend: authMiddleware verifies JWT
    → aiService.checkDuplicate() called
        → If duplicate detected: return warning (student can override)
    → aiService.suggestTags() called if no tags provided
    → aiService.analyzeDifficulty() called if difficulty not set
    → Save question + options + tags to DB
    → Return created question
```

---

### 10.2 Exam Attempt Flow

```
Student opens exam page
    → GET /api/v1/exams/:id (check if already attempted: first attempt matters)
    → POST /api/v1/exams/:id/attempt (creates attempt record, returns attempt_id)
    → Frontend starts countdown timer
    → Student answers questions
    → Student submits OR timer expires
    → POST /api/v1/exams/:id/submit
    → Backend: scoreExam() — compares answers to correct answers
    → Marks calculated, result saved to exam_attempts
    → If attempt_number == 1: insert into leaderboard table
    → Leaderboard ranks recomputed for that exam
    → Notifications sent to exam creator
    → Return result with score, breakdown, leaderboard rank
```

---

### 10.3 Leaderboard Ranking Logic

```
Ranking priority (in order):
  1. Higher score = better rank
  2. If scores are equal → lower time_taken_seconds = better rank
  3. If both equal → earlier submitted_at = better rank

Only first attempt (attempt_number = 1) is counted.
Global leaderboard aggregates across all exams:
  - Total score = sum of first-attempt scores across all exams
  - Tiebreaker = total questions answered correctly / total questions attempted (accuracy)
```

---

### 10.4 Comment & Reply System

```
Comments are self-referential:
  - parent_id = NULL → top-level comment on a question
  - parent_id = <comment_id> → reply to that comment

Max nesting depth: 1 (replies to replies not supported in v1)
Moderation:
  - Every new comment runs through aiService.moderationFilter()
  - Toxic/spam comments: saved with is_flagged = true, hidden from UI
  - Admin can review and permanently delete or unflag
```

---

## 11. Business Logic & Rules

| Rule | Details |
|------|---------|
| First attempt only for leaderboard | Only `attempt_number = 1` rows are inserted into `leaderboard` |
| Multiple attempts allowed | Students can retake exams, but only first attempt ranks |
| Question visibility | All questions are public by default (`is_public = true`) |
| Exam auto-submit | Frontend enforces timer; backend validates `time_taken_seconds ≤ duration_minutes * 60 + 30s grace` |
| Duplicate question gate | AI duplicate check runs on creation; student must confirm override if flagged |
| Soft rank display | Ranks are computed at query time with SQL `RANK()` window function over `leaderboard` table, ordered by score DESC, time ASC |
| Password security | Passwords hashed using bcrypt (rounds = 12) before storage; plaintext never stored |
| JWT expiry | Access token: 24h. Admin token: 8h |
| Comment moderation | AI flags toxic content before save; flagged content is hidden but not deleted until admin reviews |
| Like counter | `likes_count` on `questions` is a denormalized integer for read performance; updated atomically on like/unlike |

---

## 12. Data Flow Diagrams

### Register & Login Flow

```
[Client] → POST /auth/register → [authController]
    → validate input
    → check email uniqueness in DB
    → bcrypt.hash(password)
    → INSERT into users
    → return 201 + user object

[Client] → POST /auth/login → [authController]
    → find user by email
    → bcrypt.compare(password, hash)
    → jwt.sign({ id, role }, SECRET, { expiresIn: '24h' })
    → return 200 + { token, user }
```

### Protected Request Flow

```
[Client] → Any protected endpoint
    → authMiddleware.js extracts Bearer token
    → jwt.verify(token, SECRET)
    → attaches decoded user to req.user
    → roleMiddleware (if admin route): checks req.user.role === 'admin'
    → passes to controller
```

---

## 13. Security & Auth

- **JWT-based auth:** Stateless tokens. No session storage on server.
- **Role-based access control (RBAC):** `authMiddleware` verifies token; `roleMiddleware` checks role.
- **Password hashing:** bcrypt with salt rounds = 12.
- **Input validation:** All inputs validated server-side before DB queries (use express-validator or equivalent).
- **SQL injection prevention:** Use parameterized queries (no raw string interpolation).
- **CORS:** Configured to allow only frontend origin.
- **Rate limiting:** Apply to auth endpoints (`/register`, `/login`) — max 10 requests per minute per IP.
- **Admin route isolation:** All `/admin/*` frontend routes and `/api/v1/admin/*` backend routes are gated by role check.

---

## 14. Notification System

**Trigger events:**

| Event | Recipient | Message |
|-------|-----------|---------|
| New exam published | All students (or followers) | "New exam available: [Exam Title]" |
| New question created | Followers of that topic/tag | "New question tagged [Tag]" |
| Comment on your question | Question owner | "[User] commented on your question" |
| Reply to your comment | Comment author | "[User] replied to your comment" |
| Leaderboard rank change | Student | "You moved up to rank #X on [Exam]" |
| Admin announcement | All students | Custom message from admin |

**Delivery:** Initially polling-based (client polls `/api/v1/notifications` every 30s). Future: WebSocket push.

**Storage:** Notifications stored in `notifications` table. Marked read on user action.

---

## 15. Search System

**Two modes:**

| Mode | How | When to use |
|------|-----|-------------|
| Keyword | SQL `LIKE` / `FULLTEXT INDEX` on title, description, tags | Fast, default |
| Semantic | Embedding similarity via AI service | When `?mode=semantic` or when keyword returns < 3 results |

**Search filters:**
- `?q=` — search term
- `?tags=` — comma-separated tag names
- `?difficulty=easy|medium|hard`
- `?type=mcq|true_false|short_answer|descriptive`
- `?mode=keyword|semantic`

**Indexing strategy:**
- MySQL FULLTEXT index on `questions(title, description)`
- Separate embeddings store (can be a vector column in MySQL 9+ or external like Pinecone/Qdrant) for semantic search

---

## 16. Leaderboard System

### Per-Exam Leaderboard

- Populated when a student submits their **first attempt**
- Ranked by: score DESC → time_taken_seconds ASC → submitted_at ASC
- Displayed on the exam detail page and result page

### Global Leaderboard

- Aggregates first-attempt scores across all exams per student
- Columns shown: Rank, Name, Total Score, Exams Attended, Accuracy %
- Refreshed on every exam submission

### Student Profile Stats

| Stat | Source |
|------|--------|
| Global Rank | Computed from global leaderboard |
| Exams Attended | COUNT of distinct exam_ids in exam_attempts |
| Exams Created | COUNT of exams where user_id = student |
| Questions Created | COUNT of questions where user_id = student |
| Accuracy % | (total correct answers / total questions attempted) × 100 |

---

## 17. Future Scope

| Feature | Notes |
|---------|-------|
| Coding Questions | Support code execution via sandboxed runner (e.g., Judge0) |
| Real-time Notifications | Replace polling with WebSocket (Socket.io) |
| PDF/Notes Upload for AI | Allow students to upload PDFs; AI extracts text and generates questions |
| AI Personalized Learning Paths | Multi-week learning plans based on weak topics |
| Following System | Follow other students, see their activity |
| Teams / Group Exams | Collaborative exam taking |
| Mobile App | React Native version |
| Badges & Achievements | Gamification layer on top of leaderboard |
| Advanced Analytics | Per-question difficulty curve based on historical attempts |
| Multi-language Support | Questions in regional languages |

---

## 18. Glossary

| Term | Definition |
|------|-----------|
| **Attempt** | A single instance of a student taking an exam. Multiple attempts are allowed; only the first counts for the leaderboard. |
| **First Attempt** | The attempt record where `attempt_number = 1`. This is the only attempt recorded in the `leaderboard` table. |
| **Question Bank** | The collective set of all public questions on the platform, contributed by students and admins. |
| **Leaderboard** | A ranked list of students for a specific exam or globally, based on score and time. |
| **Tag** | A keyword label attached to a question (e.g., "algebra", "photosynthesis"). Used for search and recommendations. |
| **AI Module** | The backend gateway (`aiService.js`) that routes calls to specific AI service functions in `ai-services/`. |
| **Semantic Search** | Search using AI-generated vector embeddings to find conceptually similar questions, beyond keyword matching. |
| **Duplicate Detection** | AI feature that checks if a newly created question is semantically too similar to an existing question. |
| **Difficulty Analyzer** | AI feature that predicts whether a question is easy, medium, or hard based on its content. |
| **Study Assistant** | A conversational AI feature that answers students' learning questions, optionally grounded in the question bank. |
| **Moderation Filter** | AI feature that detects toxic language or spam in comments and questions before they are saved. |
| **RBAC** | Role-Based Access Control — the system by which `student` and `admin` roles have different permissions enforced by middleware. |
| **JWT** | JSON Web Token — a stateless authentication token signed by the server and sent with every protected API request. |
| **Denormalized Counter** | A pre-computed integer stored directly on a row (e.g., `likes_count` on questions) to avoid expensive COUNT queries on every read. |

---

*Document version: 1.0 | Project: QERA | Maintainer: QERA Dev Team*
*This document should be updated whenever a module, schema, or business rule changes.*
