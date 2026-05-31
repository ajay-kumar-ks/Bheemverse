-- Gamification, badges, and comment enhancements

CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    icon_url TEXT,
    criteria_type TEXT NOT NULL,
    criteria_value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS user_badges (
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    unlocked_at DATETIME NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comment_votes (
    user_id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    vote_type INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id, comment_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE
);

ALTER TABLE comments ADD COLUMN upvotes_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE comments ADD COLUMN is_helpful INTEGER NOT NULL DEFAULT 0;

INSERT OR IGNORE INTO badges (name, description, icon_url, criteria_type, criteria_value) VALUES 
('First Milestone', 'Completed your first exam!', '🏆', 'exams_completed', 1),
('Rising Star', 'Completed 5 exams.', '⭐', 'exams_completed', 5),
('Contributor', 'Created your first question.', '✍️', 'questions_created', 1),
('Top Scorer', 'Achieved a score of 90+ on any exam.', '🎯', 'score_threshold', 90);
