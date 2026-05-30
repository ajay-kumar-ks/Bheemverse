ALTER TABLE questions ADD COLUMN image_url TEXT;
ALTER TABLE questions ADD COLUMN media_url TEXT;
ALTER TABLE questions ADD COLUMN attachment_url TEXT;
ALTER TABLE question_options ADD COLUMN image_url TEXT;
ALTER TABLE users ADD COLUMN preferred_topics TEXT NOT NULL DEFAULT '[]';
ALTER TABLE users ADD COLUMN learning_goals TEXT;
ALTER TABLE users ADD COLUMN notification_preferences TEXT NOT NULL DEFAULT '{"email":true,"in_app":true,"exam_reminders":true}';
