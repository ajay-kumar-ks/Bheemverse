# AI Features Implementation Plan for QERA

This document outlines a phase-by-phase plan for integrating advanced AI capabilities into the QERA project. It draws insights from the `FEATURE_GAP_ANALYSIS.md`, `QERA_implementation_plan.md`, and `MISSING_FEATURES.md` to prioritize and detail the implementation of AI-driven features, enhancing the learning and assessment experience.

---

## Phase 1: Foundational AI Services & Basic Integration
**Goal:** Establish the core AI service infrastructure and integrate initial AI-powered content analysis features into the backend and frontend.

### Sub-phase 1.1: Core AI Service Infrastructure
-   **P10.1 — `backend/ai_service.py` Gateway Enhancement**
    -   **Explanation:** Strengthen the central gateway module (`ai_service.py`) to reliably call various AI-services Python modules. Implement robust error handling (try/except) to ensure AI failures do not block core application functionality, returning safe defaults when AI services are unavailable.
    -   **Current Status:** Rule-based stubs exist; needs full implementation with actual AI service calls.
-   **LLM Integration Strategy (API vs. Local)**
    -   **Explanation:** Define the strategy for integrating Large Language Models (LLMs), whether through external APIs (e.g., OpenAI, Gemini) or by deploying smaller, optimized models locally/on-premises. This decision will impact performance, cost, and complexity.

### Sub-phase 1.2: Content Analysis AI (Backend)
-   **P10.4 — AI Difficulty Analyzer (`ai-services/difficulty_analyzer.py`)**
    -   **Explanation:** Develop an AI service that analyzes question content (title, description, options, correct answer) to predict its difficulty level (easy, medium, hard) with a confidence score. This will automate a crucial part of question creation.
    -   **Current Status:** Not implemented in `ai-services/`.
-   **P10.3 — AI Tag Generator (`ai-services/tag_generator.py`)**
    -   **Explanation:** Create an AI service that processes question title and description to suggest 3-7 relevant tag strings. This will improve content categorization and discoverability.
    -   **Current Status:** Not implemented in `ai-services/`.
-   **P10.2 — AI Duplicate Detector (`ai-services/duplicate_detector.py`)**
    -   **Explanation:** Implement an AI service that embeds question text and performs cosine similarity against existing questions in the database. It should return whether a question is a duplicate (e.g., confidence > 0.88) and provide IDs of similar questions to prevent redundant content.
    -   **Current Status:** Not implemented in `ai-services/`.
-   **P10.8 — AI Moderation Filter (`ai-services/moderation_filter.py`)**
    -   **Explanation:** Develop an AI service to analyze text content (comments, questions) for toxicity, spam, or inappropriate language. It should return a flag (`is_toxic`, `is_spam`) and a reason, enabling automated content moderation.
    -   **Current Status:** Not implemented in `ai-services/`; basic rule-based stub may exist in `question_service.py`.

### Sub-phase 1.3: Basic UI Integration for Content Analysis
-   **P17.4 — AI Tag/Difficulty Suggestions in `CreateQuestionPage`**
    -   **Explanation:** Enhance the `CreateQuestionPage.jsx` to display AI-suggested tags as clickable chips (allowing add/remove functionality) and show the AI-predicted difficulty as a badge, possibly with a confidence score tooltip. This gives immediate feedback to content creators.
    -   **Current Status:** Not Started.
-   **P17.5 — Duplicate Question Warning Modal**
    -   **Explanation:** Implement a modal that appears when a user attempts to create a question detected as a duplicate. It should display the confidence percentage, links to similar questions, and provide options to "Override & Submit" or "Cancel".
    -   **Current Status:** Not Started.

---

## Phase 2: AI-Powered Content Generation & Explanations
**Goal:** Enable AI to generate new questions, exams, and provide detailed explanations for answers.

### Sub-phase 2.1: Content Generation AI (Backend)
-   **P10.6 — AI Question Generator (`ai-services/question_generator.py`)**
    -   **Explanation:** Develop an AI service that can generate a list of question dictionaries (matching `QuestionCreate` schema) based on provided topics, text, or even PDF content. This will significantly speed up content creation for both admins and students.
    -   **Current Status:** Not implemented in `ai-services/`.
-   **P10.7 — AI Exam Generator (`ai-services/exam_generator.py`)**
    -   **Explanation:** Create an AI service (admin-only) that generates a full exam object, including questions, based on parameters like topic, desired question count, difficulty distribution, and duration. This streamlines exam creation for instructors.
    -   **Current Status:** Not implemented in `ai-services/`.
-   **P10.5 — AI Explanation Generator (`ai-services/explanation_generator.py`)**
    -   **Explanation:** Implement an AI service that takes a question, its options, and the correct answer, then generates a comprehensive plain-text explanation string. This provides instant learning feedback for users.
    -   **Current Status:** Not implemented in `ai-services/`.

### Sub-phase 2.2: UI for AI-Generated Content & Explanations
-   **P16.4 — Admin AI Exam Generation UI (Extension to existing)**
    -   **Explanation:** Enhance the existing `admin/ExamManagementPage.jsx` to fully integrate with the AI Exam Generator. Provide a form where admins can input topic, count, difficulty distribution, and duration to generate new exams.
    -   **Current Status:** Form exists for `POST /exams/generate` but AI backend is not fully implemented.
-   **P17.2 — Student AI Question Generator Page (`AIQuestionGeneratorPage.jsx`)**
    -   **Explanation:** Develop a student-facing page where users can input topics or paste text, select question count, type, and difficulty, and then generate a preview of questions. Users should be able to edit individual questions before bulk-saving them to their question bank.
    -   **Current Status:** Not Started.
-   **P13.2 — AI Explanation Display in `QuestionDetailPage` and `ExamResultPage` (Extension to existing)**
    -   **Explanation:** Fully implement the expandable AI explanation panel in `QuestionDetailPage.jsx` and `ExamResultPage.jsx` to call `POST /ai/explain` and render the generated explanation text. This provides immediate, detailed feedback.
    -   **Current Status:** Panel exists, but `POST /ai/explain` backend is a stub.

---

## Phase 3: Personalized Learning & Advanced AI Interactions
**Goal:** Leverage AI for personalized learning paths, recommendations, and conversational tutoring.

### Sub-phase 3.1: Personalized Learning AI (Backend)
-   **P10.9 — AI Recommendation Engine (`ai-services/recommendation_engine.py`)**
    -   **Explanation:** Build an AI service that analyzes user attempt history, bookmarks, and performance data to generate a ranked list of recommended exams and questions with accompanying reason strings. This drives personalized learning.
    -   **Current Status:** Not implemented in `ai-services/`.
-   **P10.10 — AI Semantic Search Backend (`ai-services/semantic_search.py`)**
    -   **Explanation:** Implement an embedding-based semantic search backend that processes user queries and performs nearest-neighbor searches against question embeddings to return a ranked list of relevant `question_id`s. This will provide more intuitive search results than keyword matching.
    -   **Current Status:** Not implemented in `ai-services/`; current semantic search is a NULL stub.

### Sub-phase 3.2: Interactive AI & Recommendations (Frontend)
-   **P17.1 — Study Assistant Chat UI (`StudyAssistantPage.jsx`)**
    -   **Explanation:** Develop a chat-style UI where users can ask natural language questions (optionally linked to specific questions in the bank). This UI will send `POST /ai/study-assistant` requests and display conversational replies, maintaining message history within the session.
    -   **Current Status:** Not Started.
-   **P17.3 — Recommendations Panel on Dashboard (`RecommendationsPanel.jsx`)**
    -   **Explanation:** Create a component for the `DashboardPage.jsx` that calls `POST /ai/recommend` on load and displays a ranked list of recommended exams and questions, along with the reasons for the recommendations. This guides users to relevant content.
    -   **Current Status:** Not Started.
-   **P13.1 — Semantic Search Integration in `QuestionsPage` (Extension to existing)**
    -   **Explanation:** Fully integrate the AI Semantic Search into the `QuestionsPage.jsx`, allowing users to toggle between keyword and semantic search modes. The frontend should call the new semantic search backend when selected.
    -   **Current Status:** Toggle exists, but backend is a NULL stub.
