# QERA.mem — Compressed Project Memory v1.0
> AI-powered exam+question platform. Stack: React+Tailwind / Node+Express MVC / MySQL / ai-services module. Auth: JWT stateless. All API: `/api/v1`. Source truth: QERA.md.

---
## ROLES
**Student** [self-register]: create/view/search/like/bookmark/comment/reply questions; create/publish/attend exams; view results+leaderboard+profiles; notifications; AI study assistant+explanations. CANNOT: admin dashboard, moderate others, generate platform exams.
**Admin** [login only]: manage users(view/suspend/delete); moderate questions/comments; manage all exams; generate AI/random exams platform-wide; handle reports; monitor activity; trigger batch AI moderation.

---
## STACK & ARCH
```
React+Tailwind SPA → REST JSON/HTTPS → Node+Express (MVC)
  Controllers(HTTP) → Services(logic) → Models(MySQL queries, no ORM)
  ↓
MySQL(primary) + ai-services/(isolated LLM module, swappable)
```
Modules: Auth, Question, Exam, User, Leaderboard, AI, Notification, Search.

---
## FOLDER MAP
```
qera/
├── frontend/src/{assets,components/{common,question,exam,leaderboard,layout},pages/{auth,dashboard,exams,questions,leaderboard,profile,admin},hooks,context,services,utils,App.jsx}
├── backend/src/{config,controllers,services,models,routes,middlewares/{authMiddleware,roleMiddleware,errorHandler},utils,app.js} + server.js
├── ai-services/{questionGenerator,examGenerator,duplicateDetector,difficultyAnalyzer,explanationGenerator,tagGenerator,recommendationEngine,studyAssistant,moderationFilter,semanticSearch}.js
├── database/{schema.sql,seeds/,migrations/}
├── docs/{QERA.md,api-reference.md,ai-agent-guide.md}
└── README.md
```

---
## DATABASE SCHEMA
**ER:** users → questions → question_options; questions → comments(self-ref replies); questions → bookmarks; questions ↔ tags(via question_tags); questions ↔ exams(via exam_questions); exams → exam_attempts → leaderboard; users → notifications.

**users**: id PK | name VARCHAR(100) | email VARCHAR(150) UNIQUE | password_hash VARCHAR(255) bcrypt | role ENUM(student,admin) def:student | avatar_url | bio | created_at | updated_at

**questions**: id PK | user_id FK | title VARCHAR(255) | description TEXT | type ENUM(mcq,true_false,short_answer,descriptive) | correct_answer TEXT | difficulty ENUM(easy,medium,hard) AI-predicted | explanation TEXT | is_public BOOL def:true | likes_count INT denormalized | timestamps

**question_options**: id PK | question_id FK | option_text TEXT | option_order INT(1-4)

**tags**: id PK | name VARCHAR(100) UNIQUE  
**question_tags**: question_id FK | tag_id FK

**exams**: id PK | user_id FK | title | description | duration_minutes INT | total_marks INT | is_public BOOL | randomize_order BOOL | timestamps

**exam_questions**: id PK | exam_id FK | question_id FK | marks INT | question_order INT

**exam_attempts**: id PK | exam_id FK | user_id FK | attempt_number INT(1=first) | score INT | total_marks INT(snapshot) | time_taken_seconds INT | submitted_at DATETIME | answers JSON(q_id→answer)

**leaderboard**: id PK | exam_id FK | user_id FK | attempt_id FK(first only) | score INT | time_taken_seconds INT | rank INT(dynamic/cached)

**bookmarks**: user_id FK | question_id FK | created_at

**comments**: id PK | question_id FK | user_id FK | parent_id FK→comments(NULL=top,set=reply) | content TEXT | is_flagged BOOL | created_at

**notifications**: id PK | user_id FK(recipient) | type VARCHAR(50) | message TEXT | reference_id INT | reference_type VARCHAR(50) | is_read BOOL def:false | created_at

---
## API ENDPOINTS (prefix: /api/v1 | protected: Bearer JWT)

**AUTH /auth**
- POST /register → public | {name,email,password} → 201+user
- POST /login → public | {email,password} → {token,user{id,name,role}}
- POST /admin/login → public | admin JWT(8h)
- GET /me → student | current user
- POST /logout → student | client clears token

**QUESTIONS /questions**
- GET / → public | paginated list
- GET /:id → public | question+options
- POST / → student | create {title,description,type,options[],correct_answer,difficulty,explanation,tags[]}
- PUT /:id → student(owner) | update
- DELETE /:id → owner/admin
- POST /:id/like → student | toggle
- POST /:id/bookmark → student | toggle
- GET /:id/comments → public
- POST /:id/comments → student | add comment
- POST /:id/comments/:cid/reply → student | reply

**EXAMS /exams**
- GET / → public | list
- GET /:id → public | detail+questions
- POST / → student | create exam
- PUT /:id → owner/admin
- DELETE /:id → owner/admin
- POST /:id/attempt → student | start → returns attempt_id
- POST /:id/submit → student | {attempt_id,time_taken_seconds,answers{q_id→answer}}
- GET /:id/result/:attemptId → student
- GET /:id/leaderboard → public
- POST /generate → admin | AI/random generation

**USERS /users**
- GET /:id/profile → public
- PUT /me → student | update profile
- GET /me/bookmarks|exams|questions|notifications → student
- PUT /me/notifications/:id/read → student

**LEADERBOARD /leaderboard**
- GET /global → public | all students ranked
- GET /exam/:examId → public | per-exam

**AI /ai**
- POST /generate-questions → student | {topic|text|pdf_content, count, type, difficulty}
- POST /generate-exam → admin | {topic, count, difficulty_dist, duration}
- POST /explain → student | question object → explanation
- POST /check-duplicate → student | question text → {is_duplicate, confidence, similar_ids[]}
- POST /suggest-tags → student | question text → tags[]
- POST /analyze-difficulty → student | question → easy|medium|hard + confidence
- POST /recommend → student | user history → ranked exams+questions
- POST /study-assistant → student | {question, optional:question_id} → answer

**SEARCH /search**
- GET /questions → public | ?q=&tags=&difficulty=&type=&mode=keyword|semantic
- GET /exams → public | ?q=

**NOTIFICATIONS /notifications**
- GET / → student | all
- PUT /:id/read → student
- PUT /read-all → student

---
## AI SERVICES (all in ai-services/, gateway: backend/aiService.js)

| Service | Input | Output | Trigger |
|---|---|---|---|
| questionGenerator | topic/text/PDF | question[] (full payload shape) | on demand, student |
| examGenerator | topic+count+difficulty_dist+duration | full exam object | admin only |
| duplicateDetector | question text | {is_duplicate,confidence,similar_ids} | auto on every create; cosine sim >0.88 |
| difficultyAnalyzer | title+desc+options | easy/medium/hard + confidence | auto on create if unset |
| explanationGenerator | question+options+answer | plain-text explanation | on demand or auto if blank |
| tagGenerator | title+desc | 3-7 tags | auto on create if no tags |
| recommendationEngine | attempt history+accuracy+bookmarks | ranked exams+questions+reasons | on demand |
| studyAssistant | NL question + optional q_id | conversational answer | on demand |
| moderationFilter | comment/question text | {is_toxic,is_spam,reason} | auto every comment; optional on question create |
| semanticSearch | NL query | ranked question_id[] | when mode=semantic or keyword returns <3 results |

---
## BUSINESS RULES
- Leaderboard: only attempt_number=1 counts; multiple retakes allowed
- Rank order: score DESC → time_taken_seconds ASC → submitted_at ASC
- Global rank: sum of first-attempt scores; tiebreak by accuracy %
- Questions: is_public=true default
- Exam auto-submit: backend validates time_taken_seconds ≤ duration_minutes×60 + 30s grace
- Duplicate gate: AI runs before save; student can override warning
- Rank SQL: RANK() window fn over leaderboard ORDER BY score DESC, time ASC
- Password: bcrypt rounds=12; plaintext never stored
- JWT: student=24h, admin=8h
- Comment moderation: flagged → is_flagged=true → hidden UI → admin reviews before delete
- likes_count: denormalized INT on questions; atomic update on like/unlike

---
## FLOWS

**Question Create:**
frontend validate → POST /questions (JWT) → checkDuplicate() → [warn if dup] → suggestTags() if none → analyzeDifficulty() if unset → INSERT question+options+tags → return

**Exam Attempt:**
GET /exams/:id → POST /exams/:id/attempt (create record, get attempt_id) → countdown timer → answer → submit|auto-submit → scoreExam() → save exam_attempts → if attempt_number==1: INSERT leaderboard → recompute ranks → notify exam creator → return result+rank

**Auth:**
register: validate→unique email→bcrypt.hash→INSERT→201
login: find by email→bcrypt.compare→jwt.sign({id,role},SECRET,24h)→{token,user}
protected: extractBearer→jwt.verify→req.user→roleMiddleware if admin route

---
## SECURITY
- JWT stateless; no server sessions
- RBAC: authMiddleware(verify) + roleMiddleware(role===admin)
- bcrypt rounds=12
- express-validator server-side on all inputs
- Parameterized queries; no raw string interpolation
- CORS: frontend origin only
- Rate limit auth endpoints: 10 req/min/IP
- All /admin/* routes gated by role check (frontend + backend)

---
## NOTIFICATIONS
Triggers → recipient: new_exam→all students; new_question→topic followers; comment on Q→Q owner; reply→comment author; rank change→student; admin announcement→all.
Delivery: polling /notifications every 30s. Future: WebSocket.
Storage: notifications table. Mark read on action.

---
## SEARCH
Keyword (default): MySQL FULLTEXT on questions(title,description) + tags filter.
Semantic (mode=semantic or fallback): embedding nearest-neighbor via semanticSearch.js; store: MySQL9+ vector col or Pinecone/Qdrant.
Filters: ?q= | ?tags= | ?difficulty=easy|medium|hard | ?type=mcq|true_false|short_answer|descriptive | ?mode=keyword|semantic

---
## FRONTEND ROUTES
/ landing | /login /register (public) | /dashboard (S) | /questions (pub) | /questions/create (S) | /questions/:id (pub) | /exams (pub) | /exams/create (S) | /exams/:id (pub) | /exams/:id/attend (S) | /exams/:id/result/:aid (S) | /leaderboard (pub) | /leaderboard/exam/:id (pub) | /profile/:uid (pub) | /profile/me (S) | /bookmarks (S) | /notifications (S) | /admin/* (A)

UI rules: exam attend→timer auto-submit→no nav without confirm; result page→score+breakdown+AI explanation+rank.

---
## PROFILE STATS
Global Rank | Exams Attended (COUNT distinct exam_ids) | Exams Created | Questions Created | Accuracy % = (correct/total attempted)×100

---
## FUTURE SCOPE
Coding questions (Judge0 sandbox) | WebSocket notifications (Socket.io) | PDF upload→AI question gen | AI learning paths | Following system | Group exams | React Native app | Badges/achievements | Advanced per-question analytics | Multi-language questions

---
## GLOSSARY (compressed)
Attempt=one exam sitting; First Attempt=attempt_number=1, only one in leaderboard; Question Bank=all public questions; Tag=keyword label on question; AI Module=aiService.js gateway; Semantic Search=embedding similarity beyond keywords; RBAC=role-based middleware; JWT=stateless signed token; Denormalized Counter=pre-computed col to avoid COUNT queries.
