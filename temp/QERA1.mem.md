# QERA.mem — Compressed Project Memory v1.1
> AI-powered exam+question platform. Stack: React+Tailwind / FastAPI+Python / MySQL / ai-services module. Auth: JWT stateless. All API: `/api/v1`. Source truth: QERA.md.

---
## ROLES
**Student** [self-register]: create/view/search/like/bookmark/comment/reply questions; create/publish/attend exams; view results+leaderboard+profiles; notifications; AI study assistant+explanations. CANNOT: admin dashboard, moderate others, generate platform exams.
**Admin** [login only]: manage users(view/suspend/delete); moderate questions/comments; manage all exams; generate AI/random exams platform-wide; handle reports; monitor activity; trigger batch AI moderation.

---
## STACK & ARCH
```
React+Tailwind SPA → REST JSON/HTTPS → FastAPI (Python, async)
  Routers(HTTP) → Services(logic) → Models(MySQL queries, SQLAlchemy Core / raw)
  ↓
MySQL(primary) + ai-services/(isolated LLM module, swappable)
```
- FastAPI serves async endpoints via `uvicorn` (ASGI)
- Pydantic v2 models for request/response validation (replaces express-validator)
- SQLAlchemy Core (no ORM) or raw `aiomysql` for async DB queries
- `python-jose` for JWT; `passlib[bcrypt]` for password hashing
- `slowapi` for rate limiting (replaces express-rate-limit)
- `python-multipart` for file uploads (PDF ingestion)
- Modules: Auth, Question, Exam, User, Leaderboard, AI, Notification, Search.

---
## FOLDER MAP
```
qera/
├── frontend/src/{assets,components/{common,question,exam,leaderboard,layout},pages/{auth,dashboard,exams,questions,leaderboard,profile,admin},hooks,context,services,utils,App.jsx}
├── backend/
│   ├── main.py                      # FastAPI app init, CORS, router registration
│   ├── config.py                    # Settings via pydantic-settings / .env
│   ├── database.py                  # DB connection pool (aiomysql/SQLAlchemy)
│   ├── dependencies.py              # Shared FastAPI Depends() — get_db, get_current_user
│   ├── routers/                     # auth.py question.py exam.py user.py leaderboard.py ai.py search.py notification.py
│   ├── services/                    # auth_service.py question_service.py exam_service.py … (business logic)
│   ├── models/                      # db/: auth_model.py question_model.py … (raw SQL queries)
│   │                                # schemas/: auth_schema.py question_schema.py … (Pydantic models)
│   ├── middlewares/                 # auth_middleware.py role_middleware.py error_handler.py
│   ├── utils/                       # jwt_utils.py hash_utils.py pagination.py
│   └── ai_gateway.py               # Gateway to ai-services/ (replaces aiService.js)
├── ai-services/{questionGenerator,examGenerator,duplicateDetector,difficultyAnalyzer,explanationGenerator,tagGenerator,recommendationEngine,studyAssistant,moderationFilter,semanticSearch}.py
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
> FastAPI routers use `APIRouter(prefix=..., tags=[...])`. Dependencies injected via `Depends()`.

**AUTH /auth**
- POST /register → public | {name,email,password} → 201+user
- POST /login → public | OAuth2PasswordRequestForm or JSON {email,password} → {access_token, token_type, user{id,name,role}}
- POST /admin/login → public | admin JWT(8h)
- GET /me → student | current user (Depends: get_current_user)
- POST /logout → student | client clears token (stateless; no server action needed)

**QUESTIONS /questions**
- GET / → public | paginated list
- GET /{id} → public | question+options
- POST / → student | create {title,description,type,options[],correct_answer,difficulty,explanation,tags[]}
- PUT /{id} → student(owner) | update
- DELETE /{id} → owner/admin
- POST /{id}/like → student | toggle
- POST /{id}/bookmark → student | toggle
- GET /{id}/comments → public
- POST /{id}/comments → student | add comment
- POST /{id}/comments/{cid}/reply → student | reply

**EXAMS /exams**
- GET / → public | list
- GET /{id} → public | detail+questions
- POST / → student | create exam
- PUT /{id} → owner/admin
- DELETE /{id} → owner/admin
- POST /{id}/attempt → student | start → returns attempt_id
- POST /{id}/submit → student | {attempt_id,time_taken_seconds,answers{q_id→answer}}
- GET /{id}/result/{attempt_id} → student
- GET /{id}/leaderboard → public
- POST /generate → admin | AI/random generation

**USERS /users**
- GET /{id}/profile → public
- PUT /me → student | update profile
- GET /me/bookmarks|exams|questions|notifications → student
- PUT /me/notifications/{id}/read → student

**LEADERBOARD /leaderboard**
- GET /global → public | all students ranked
- GET /exam/{exam_id} → public | per-exam

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
- PUT /{id}/read → student
- PUT /read-all → student

---
## AI SERVICES (all in ai-services/, gateway: backend/ai_gateway.py)

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
- Password: passlib bcrypt rounds=12; plaintext never stored
- JWT: student=24h(1440min), admin=8h(480min) — signed via python-jose HS256
- Comment moderation: flagged → is_flagged=true → hidden UI → admin reviews before delete
- likes_count: denormalized INT on questions; atomic update on like/unlike

---
## FLOWS

**Question Create:**
frontend validate → POST /questions (JWT) → checkDuplicate() → [warn if dup] → suggestTags() if none → analyzeDifficulty() if unset → INSERT question+options+tags → return

**Exam Attempt:**
GET /exams/{id} → POST /exams/{id}/attempt (create record, get attempt_id) → countdown timer → answer → submit|auto-submit → scoreExam() → save exam_attempts → if attempt_number==1: INSERT leaderboard → recompute ranks → notify exam creator → return result+rank

**Auth:**
register: validate(Pydantic)→unique email check→passlib.hash→INSERT→201
login: find by email→passlib.verify→jose.jwt.encode({sub:id,role},SECRET,HS256,exp)→{access_token,token_type,user}
protected: OAuth2PasswordBearer→jose.jwt.decode→req.state.user or Depends(get_current_user)→role check via Depends(require_role("admin"))

---
## FASTAPI-SPECIFIC PATTERNS
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="QERA API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# dependencies.py
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> UserOut:
    ...

def require_role(role: str):
    def checker(current_user: UserOut = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Forbidden")
    return Depends(checker)

# Example router (routers/question.py)
router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("/", response_model=QuestionOut, status_code=201)
async def create_question(payload: QuestionCreate, current_user=Depends(get_current_user), db=Depends(get_db)):
    return await question_service.create(payload, current_user.id, db)
```

---
## SECURITY
- JWT stateless; no server sessions
- RBAC: `Depends(get_current_user)` + `Depends(require_role("admin"))`
- passlib bcrypt rounds=12
- Pydantic v2 server-side validation on all request bodies and query params
- Parameterized queries via SQLAlchemy Core / aiomysql execute(); no raw string interpolation
- CORS: frontend origin only (CORSMiddleware)
- Rate limit auth endpoints: 10 req/min/IP via slowapi
- All /admin/* routes gated by require_role("admin") dependency (frontend + backend)
- HTTPS enforced in production (uvicorn behind nginx/reverse proxy)

---
## NOTIFICATIONS
Triggers → recipient: new_exam→all students; new_question→topic followers; comment on Q→Q owner; reply→comment author; rank change→student; admin announcement→all.
Delivery: polling /notifications every 30s. Future: WebSocket via FastAPI `websockets` support.
Storage: notifications table. Mark read on action.

---
## SEARCH
Keyword (default): MySQL FULLTEXT on questions(title,description) + tags filter.
Semantic (mode=semantic or fallback): embedding nearest-neighbor via semanticSearch.py; store: MySQL9+ vector col or Pinecone/Qdrant.
Filters: ?q= | ?tags= | ?difficulty=easy|medium|hard | ?type=mcq|true_false|short_answer|descriptive | ?mode=keyword|semantic

---
## FRONTEND ROUTES
/ landing | /login /register (public) | /dashboard (S) | /questions (pub) | /questions/create (S) | /questions/:id (pub) | /exams (pub) | /exams/create (S) | /exams/:id (pub) | /exams/:id/attend (S) | /exams/:id/result/:aid (S) | /leaderboard (pub) | /leaderboard/exam/:id (pub) | /profile/:uid (pub) | /profile/me (S) | /bookmarks (S) | /notifications (S) | /admin/* (A)

UI rules: exam attend→timer auto-submit→no nav without confirm; result page→score+breakdown+AI explanation+rank.

---
## PROFILE STATS
Global Rank | Exams Attended (COUNT distinct exam_ids) | Exams Created | Questions Created | Accuracy % = (correct/total attempted)×100

---
## KEY PYTHON DEPENDENCIES
```
fastapi>=0.111
uvicorn[standard]>=0.29
pydantic>=2.7
pydantic-settings>=2.2
python-jose[cryptography]>=3.3
passlib[bcrypt]>=1.7
aiomysql>=0.2          # async MySQL driver
SQLAlchemy>=2.0        # Core only, no ORM
python-multipart>=0.0.9
slowapi>=0.1.9
httpx>=0.27            # async HTTP for AI service calls
```

---
## FUTURE SCOPE
Coding questions (Judge0 sandbox) | WebSocket notifications (FastAPI native) | PDF upload→AI question gen | AI learning paths | Following system | Group exams | React Native app | Badges/achievements | Advanced per-question analytics | Multi-language questions

---
## GLOSSARY (compressed)
Attempt=one exam sitting; First Attempt=attempt_number=1, only one in leaderboard; Question Bank=all public questions; Tag=keyword label on question; AI Module=ai_gateway.py gateway; Semantic Search=embedding similarity beyond keywords; RBAC=role-based Depends() injection; JWT=stateless signed token (python-jose); Denormalized Counter=pre-computed col to avoid COUNT queries; Pydantic Schema=request/response validation model; Router=FastAPI APIRouter (replaces Express router); Service=business logic layer; Depends()=FastAPI dependency injection system.
