# AI Features Implementation — Google AI Studio (Gemini)

**Provider:** Google AI Studio | **SDK:** `google-generativeai>=0.8.0`
**Auth:** `GOOGLE_AI_STUDIO_API_KEY` in `backend/.env`

---

## Prerequisites (Do First)

- [x] Add `google-generativeai>=0.8.0` to `backend/requirements.txt`
- [x] Add `GOOGLE_AI_STUDIO_API_KEY: str | None = Field(None, env="GOOGLE_AI_STUDIO_API_KEY")` to `backend/config.py`
- [x] Add the actual key to `backend/.env`

---

## Phase 1: Upgrade Existing AI Stubs ✅

Replace the 5 placeholder functions in `backend/services/ai_service.py` with real Gemini calls. This phase has **no new endpoints** — it makes existing features intelligent.

### 1.1 — Duplicate Detection (`check_duplicate`) ✅

**What it does today:** Exact-match SQL on title/description. Near-duplicates slip through.
**What Gemini adds:** Understands meaning — catches reworded duplicates.

**Implementation:**
- Fetch existing question titles from DB.
- Send `[title, description]` + list of existing titles to Gemini.
- Prompt it to return JSON: `{is_duplicate, similar_ids[], confidence, reason}`.
- **Model:** `gemini-2.0-flash`
- **Fallback:** If API call fails or key missing → fall back to SQL exact-match.
- **Integration:** Called inside `create_question()` in `question_service.py`. If duplicate found, attach warning to response — do not block creation.

### 1.2 — Tag Suggestions (`suggest_tags`) ✅

**What it does today:** Hardcoded keyword rules — only recognizes "math", "science", "history", "general".
**What Gemini adds:** Generates relevant, domain-specific tags from question content.

**Implementation:**
- Send `[title, description]` to Gemini.
- Prompt to return 1–5 tags as `list[str]`.
- **Model:** `gemini-2.0-flash`
- **Fallback:** Keyword-based rules if API fails.
- **Integration:** Called inside `create_question()`. Tags set only if user didn't provide any.

### 1.3 — Difficulty Analysis (`analyze_difficulty`) ✅

**What it does today:** Scans for words "easy"/"hard"/"difficult" in text. Defaults to `medium`.
**What Gemini adds:** Evaluates conceptual complexity, not just word matching.

**Implementation:**
- Send `[title, description]` to Gemini.
- Prompt to return: `{difficulty: "easy"|"medium"|"hard", confidence: 0.0–1.0, reasoning: str}`.
- **Model:** `gemini-2.0-flash`
- **Fallback:** Keyword scan if API fails. Default `medium` if nothing matched.
- **Integration:** Called inside `create_question()` when user leaves difficulty unset.

### 1.4 — Content Moderation (`moderation_filter`) ✅

**What it does today:** Returns `{is_toxic: false, is_spam: false}` for everything — no filtering.
**What Gemini adds:** Detects toxic, spam, hate speech, NSFW, and self-harm content.

**Implementation:**
- Send the text (title/description/comment/bio) to Gemini.
- Prompt to return: `{is_toxic, is_spam, reason, categories[]}`.
- **Model:** `gemini-2.0-flash`
- **Fallback:** Fail-open — if API down, allow all content through (don't block users on AI outage).
- **Integration points:**
  - Question creation → moderate `title` + `description`
  - Comment creation → moderate `content`
  - Profile updates → moderate `bio` + `display_name`

### 1.5 — Semantic Search (`semantic_search`) ✅

**What it does today:** Returns `None` — feature is stubbed.
**What Gemini adds:** Finds questions by meaning, not just keyword match.

**Implementation:**
- User types natural language query (e.g., "problems about gravity and orbits").
- Backend sends query + list of question titles/descriptions from DB to Gemini.
- Gemini ranks by relevance and returns question IDs + scores.
- **Model:** `gemini-2.0-flash`
- **Fallback:** If AI fails → normal FTS5 keyword search takes over.
- **Integration:** Called from search router when user toggles "AI Search".

---

## Phase 2: AI Content Generation

New endpoints to generate questions, exams, and explanations using Gemini.

### 2.1 — Generate Single Question ✅

**Endpoint:** `POST /api/v1/ai/generate-question`
**Who uses it:** Admins creating question banks, users suggesting questions.

**Request:**
```json
{
  "topic": "World War II",
  "type": "mcq",
  "difficulty": "medium",
  "count": 3
}
```

**Response:** Array of full `QuestionCreate` objects (title, description, options, correct_answer, explanation, tags, difficulty).

**Implementation:**
- Send topic + type + difficulty + count to Gemini.
- Prompt with strict JSON schema matching `QuestionCreate`.
- **Model:** `gemini-2.0-pro` (higher quality needed for generation)
- **Fallback:** Return `503` with message "AI generation unavailable — please create manually".
- **Frontend:** Add "Generate with AI" button on `CreateQuestionPage.jsx` and admin question management.

### 2.2 — Generate Full Exam ✅
  
**Endpoint:** `POST /api/v1/ai/generate-exam`
**Who uses it:** Admins creating exams.

**Request:**
```json
{
  "topic": "Physics — Mechanics",
  "question_count": 10,
  "difficulty_mix": { "easy": 3, "medium": 5, "hard": 2 },
  "types": ["mcq", "true_false"]
}
```

**Response:** Exam object with embedded array of generated questions.

**Implementation:**
- Send exam spec to Gemini in one call.
- Gemini returns exam `{title, description, questions[]}`.
- Backend inserts exam + questions into DB in a transaction.
- **Model:** `gemini-2.0-pro`
- **Fallback:** Return error + let admin create manually.
- **Frontend:** Add "AI Generate" tab in `CreateExamPage.jsx`.

### 2.3 — AI Answer Explanation

**Endpoint:** `POST /api/v1/ai/explain`
**Who uses it:** Students reviewing exam results or browsing questions.

**Request:**
```json
{
  "question_id": 42,
  "user_answer": "Paris",
  "is_correct": false
}
```

**Response:**
```json
{
  "explanation": "The correct answer is Berlin because...",
  "key_concept": "European capitals post-WWII",
  "suggestion": "Review the chapter on Cold War geography"
}
```

**Implementation:**
- Send question text, correct answer, and user's answer to Gemini.
- Ask for: why answer is right/wrong, key concept, study suggestion.
- **Model:** `gemini-2.0-flash`
- **Fallback:** Show "Explanation not available".
- **Frontend integration:**
  - `ExamResultPage.jsx` — after each question result
  - `QuestionDetailPage.jsx` — "Ask AI to explain" button

---

## Phase 3: AI Personalization

Endpoints that use user's history to give smart recommendations and study plans.

### 3.1 — Personalized Recommendations

**Endpoint:** `GET /api/v1/ai/recommendations`
**Who uses it:** Students on the dashboard.

**Response:**
```json
{
  "recommendations": [
    { "question_id": 55, "reason": "You struggled with similar thermodynamics problems" },
    { "question_id": 102, "reason": "This topic appeared in your last 3 weak areas" }
  ]
}
```

**Implementation:**
- Backend fetches user's attempt history (correct/incorrect), bookmarks, and weak topics from DB.
- Sends this profile to Gemini with available question pool.
- Gemini picks 5–10 questions the user should practice next, with one-line reasons.
- **Model:** `gemini-2.0-flash`
- **Fallback:** If AI fails → return most popular/trending questions.
- **Frontend:** "Recommended for You" section on `DashboardPage.jsx`.

### 3.2 — Smart Study Plan

**Endpoint:** `POST /api/v1/ai/study-plan`
**Who uses it:** Students who want a structured learning path.

**Request:**
```json
{
  "goal": "Master organic chemistry nomenclature",
  "days_available": 7,
  "hours_per_day": 1.5
}
```

**Response:**
```json
{
  "plan": [
    { "day": 1, "topic": "Alkanes basics", "question_count": 15, "focus": "Naming straight-chain alkanes" },
    { "day": 2, "topic": "Branched alkanes", "question_count": 20, "focus": "Identifying parent chains" }
  ]
}
```

**Implementation:**
- Send user's goal + time constraints + weak topics from DB to Gemini.
- Gemini returns day-by-day breakdown with topics and question counts.
- **Model:** `gemini-2.0-flash`
- **Fallback:** Error — no meaningful fallback for a generated study plan.
- **Frontend:** New section or modal on `DashboardPage.jsx`.

---

## Phase 4: Conversational AI Tutor (Future)

### 4.1 — Chat with AI Tutor

**Endpoint:** `POST /api/v1/ai/chat`
**Who uses it:** Any logged-in user.

**Request:**
```json
{
  "message": "Can you explain Newton's third law with an example?",
  "context": { "current_topic": "Physics", "recent_question_ids": [12, 45] }
}
```

**Response:**
```json
{
  "reply": "Newton's third law states... For example, when you sit on a chair...",
  "follow_up_suggestions": ["Want a practice question?", "Should I explain the math behind it?"]
}
```

**Implementation:**
- Send user message + recent context to Gemini.
- Gemini responds conversationally with follow-up suggestions.
- Store conversation history in DB for context continuity.
- **Model:** `gemini-2.0-flash`
- **Fallback:** "AI tutor is currently unavailable."
- **Frontend:** Floating chat widget or dedicated `/tutor` page.

### 4.2 — Chat Safeguards

- Rate limit: max 20 messages/user/hour via `slowapi`.
- Token budget: track per-user token usage, cap at 50K tokens/day.
- All chat messages run through `moderation_filter` before reaching Gemini and before displaying to user.
- Store conversation history in `ai_conversations` + `ai_messages` tables.

---

## Resilience Rules (Apply to All Phases)

| Rule | Detail |
|---|---|
| Timeout | 10 seconds on all Gemini calls |
| Key missing | All functions degrade to fallback — app works as if AI doesn't exist |
| AI error | Log the error → use fallback from the function's table above |
| Rate limit | `slowapi` decorators on all AI endpoints |
| Key security | API key never leaves the backend — no frontend exposure |

---

## Summary: Files Changed by Phase

| Phase | Files |
|---|---|
| **Prereqs** | `requirements.txt`, `config.py`, `.env` |
| **Phase 1** | `services/ai_service.py` (5 functions rewritten) |
| **Phase 2** | `routers/ai_router.py` (new), `schemas/ai_schema.py` (new), `pages/admin/`, `pages/questions/CreateQuestionPage.jsx`, `pages/exams/CreateExamPage.jsx`, `pages/exams/ExamResultPage.jsx`, `pages/questions/QuestionDetailPage.jsx` |
| **Phase 3** | `routers/ai_router.py` (add 2 endpoints), `pages/dashboard/DashboardPage.jsx` |
| **Phase 4** | `routers/ai_router.py` (add chat endpoint), new DB migration for conversation tables, new frontend chat widget |
