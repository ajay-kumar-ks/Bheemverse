-- Achievements and Badges
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    icon_url TEXT,
    criteria_type TEXT NOT NULL, -- 'exams_completed', 'questions_created', 'score_threshold'
    criteria_value INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS user_badges (
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (badge_id) REFERENCES badges(id)
);

-- Comment Upvotes
CREATE TABLE IF NOT EXISTS comment_votes (
    user_id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    vote_type INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, comment_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (comment_id) REFERENCES comments(id)
);

-- Add social tracking to existing comments table
ALTER TABLE comments ADD COLUMN upvotes_count INTEGER DEFAULT 0;
ALTER TABLE comments ADD COLUMN is_helpful BOOLEAN DEFAULT 0;

-- Default Badges Seed
INSERT OR IGNORE INTO badges (name, description, icon_url, criteria_type, criteria_value) VALUES 
('First Milestone', 'Completed your first exam!', '🏆', 'exams_completed', 1),
('Rising Star', 'Completed 5 exams.', '⭐', 'exams_completed', 5),
('Contributor', 'Created your first question.', '✍️', 'questions_created', 1),
('Top Scorer', 'Achieved a score of 90+ on any exam.', '🎯', 'score_threshold', 90);