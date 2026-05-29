# QERA New Feature Implementation Plan

## Purpose
This plan defines a phased rollout of the best non-AI enhancements for QERA. It focuses on features that add practical value, improve user experience, and align with the current architecture without depending on AI integration.

## Goals
- Strengthen exam and question workflows
- Improve learning analytics and progress tracking
- Add richer content and import/export capabilities
- Enhance social, gamification, and admin tools
- Prepare the app for production readiness

## Phase 1: Core learning experience improvements

### 1.1 Persist exam attempt state and resume support
- Backend:
  - ✅ Extend `exam_attempts` with fields for `question_order`, `status`, `started_at`, `last_saved_at`, and `answers`.
  - ✅ Save partial attempt state whenever the user answers a question or refreshes the exam page.
  - ✅ Add `GET /api/v1/exams/{exam_id}/attempt/latest` to retrieve the current in-progress attempt.
  - ✅ Add `PATCH /api/v1/exams/attempt/{attempt_id}` to save progress without submitting.
- Frontend:
  - ✅ Keep exam answers in component state and persist to backend on answer changes.
  - ✅ Add a resume flow for in-progress attempts on the exam detail page.
  - ✅ Restore timer, selected answers, and current question order when the user returns.
- Acceptance criteria:
  - ✅ Refreshing during an exam does not lose entered answers.
  - ✅ Users can resume in-progress exams from the same place.
  - ✅ Timer continues from remaining time, and no duplicate attempt is created.

### 1.2 Improve question like/bookmark state and author attribution
- Backend:
  - ✅ Return `liked` and `bookmarked` state on question list and detail endpoints when the user is authenticated.
  - ✅ Enforce one-like-per-user at the database and service level.
- Frontend:
  - ✅ Use API-provided `liked`/`bookmarked` flags instead of temporary local state.
  - ✅ Update list and detail pages so liked/bookmarked buttons reflect saved state after refresh.
  - ✅ Show `By {author_name}` consistently in question cards and detail pages.
- Acceptance criteria:
  - ✅ Logged-in users see correct liked/bookmarked status after page reloads.
  - ✅ Question author names appear in every question view.
  - ✅ Like count does not increase on repeated requests from the same user.

### 1.3 Add enhanced exam mode and timer behavior
- Backend:
  - ✅ Add exam configuration fields: `randomize_order`, `randomize_options`, and `secure_mode`.
  - ✅ Apply question order randomization when creating an attempt and persist that order.
  - ✅ Auto-submit attempts when the timer reaches zero and mark the attempt complete.
- Frontend:
  - ✅ Expose secure exam mode and randomization settings in exam creation UI.
  - ✅ Display a persistent countdown timer during exam attendance.
  - ✅ Show an explicit warning when secure mode is enabled.
- Acceptance criteria:
  - ✅ Exam creator can enable randomization and secure mode.
  - ✅ Questions are shuffled for each attempt when enabled.
  - ✅ Attempt auto-submits exactly when time expires.

### 1.4 Bulk import/export for questions and exams
- Backend:
  - ✅ Add admin endpoint `POST /api/v1/exams/import` for JSON exam imports.
  - ✅ Add endpoint `GET /api/v1/exams/export` to download exam data as JSON.
  - ⚠️ CSV support is not implemented yet.
- Frontend:
  - ✅ Add import/export controls on the exam listing page for JSON files.
  - ⚠️ No dedicated preview workflow has been added yet.
- Acceptance criteria:
  - ✅ Admins can import exam JSON files and refresh the exam list.
  - ✅ Exam exports are downloadable as JSON.
  - ⚠️ CSV import/export is still pending.

## Phase 2: Learning analytics and user progress

### 2.1 Progress dashboard
- Add charts for score history, accuracy by difficulty, and exam completion trends
- Display recent exam results and question mastery summaries
- Add progress cards on dashboard: total exams, average score, streaks, and review due

### 2.2 Weak-topic review and practice
- Track incorrect answers by topic or tag
- Create a "Review mistakes" list for questions answered incorrectly
- Add UI to filter questions by past performance and weak areas

### 2.3 Personalized recommendations (non-AI)
- Add rule-based recommendations using bookmarks and performance
- Show sections like "Practice again", "Recommended questions", and "Recommended exams"
- Use tags, past incorrect attempts, and question difficulty to suggest content

## Phase 3: Rich content and usability

### 3.1 Media-rich questions and attachments
- Add support for image URLs or uploaded images in questions and options
- Add optional file or media attachments for questions and exam content
- Extend question schema and frontend form to accept image/media fields

### 3.2 Profile and user settings improvements
- Add avatar upload or profile picture via URL
- Add user bio, preferred topics, and learning goals
- Add profile settings page for notification preferences and display options

### 3.3 Responsive and polished UI
- Improve mobile responsiveness for question list, exam pages, and dashboard
- Add loading states, error messages, and empty-state screens
- Add better accessible labels, keyboard navigation, and focus handling

## Phase 4: Social, gamification, and community

### 4.1 Achievements and badges
- Add achievement badges for milestones: first exam, streaks, top scorer, question creator
- Add badge display on user profile and dashboard
- Add badges table and unlock criteria

### 4.2 Comments and interaction improvements
- Add public question discussion threads per question
- Allow users to upvote comments and mark helpful replies
- Add comment sorting (newest, most helpful)

### 4.3 Notification and activity feed
- Add richer notification types with action links
- Implement activity feed on dashboard: exam submissions, bookmarks, comments, achievements
- Allow users to mark all notifications read

## Phase 5: Admin and operational tooling

### 5.1 Admin reporting dashboards
- Add analytics for active users, questions created, exams taken, and flagged content
- Create admin charts for average score, exam participation, and content moderation volume

### 5.2 Content approval and review workflows
- Add admin queue for user-submitted questions and exams
- Add approve/reject actions and history audit log
- Add admin review page for flagged questions/comments with review notes

### 5.3 Deployment and production readiness
- Add Docker configuration for backend and frontend
- Add environment-based configuration and secrets support
- Add logging, error tracking, and health-check endpoints
- Add CI workflow for tests and linting

## Suggested milestone schedule

1. **Sprint 1**
   - Persist exam attempts
   - Improve liked/bookmark states
   - Add exam auto-submit and setting options
   - Add CSV/JSON import/export

2. **Sprint 2**
   - Build dashboard analytics and progress charts
   - Add review mistakes feature
   - Add rule-based recommendations

3. **Sprint 3**
   - Support media-rich questions
   - Improve profile settings and mobile UI
   - Add badges and achievement system

4. **Sprint 4**
   - Add admin reports and approval queues
   - Add production Docker and deployment documentation
   - Polish accessibility and error handling

## Notes
- This plan deliberately skips AI-dependent features.
- It focuses on closest-fit, practical product enhancements for an exam preparation platform.
- Each phase preserves the current FastAPI + SQLite backend and React frontend architecture.
