ALTER TABLE exam_attempts ADD COLUMN started_at TEXT;
UPDATE exam_attempts SET started_at = COALESCE(started_at, submitted_at, datetime('now'));

ALTER TABLE exam_attempts ADD COLUMN last_saved_at TEXT;
UPDATE exam_attempts SET last_saved_at = COALESCE(last_saved_at, started_at, submitted_at, datetime('now'));

ALTER TABLE exam_attempts ADD COLUMN question_order TEXT;
UPDATE exam_attempts SET question_order = COALESCE(question_order, '[]');
