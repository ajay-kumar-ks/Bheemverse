ALTER TABLE exams ADD COLUMN randomize_options INTEGER NOT NULL DEFAULT 0;
ALTER TABLE exams ADD COLUMN secure_mode INTEGER NOT NULL DEFAULT 0;
ALTER TABLE exam_attempts ADD COLUMN status TEXT NOT NULL DEFAULT 'in_progress';
ALTER TABLE exam_attempts ADD COLUMN started_at TEXT NOT NULL DEFAULT (datetime('now'));
ALTER TABLE exam_attempts ADD COLUMN last_saved_at TEXT NOT NULL DEFAULT (datetime('now'));
ALTER TABLE exam_attempts ADD COLUMN question_order TEXT NOT NULL DEFAULT '[]';
