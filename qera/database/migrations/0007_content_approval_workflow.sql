-- Phase 5: Content Approval Workflow
-- Add pending approvals tracking for user-submitted questions and exams

CREATE TABLE IF NOT EXISTS pending_approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content_type TEXT NOT NULL CHECK (content_type IN ('question', 'exam')),
  content_id INTEGER NOT NULL,
  submitted_by INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  admin_id INTEGER,
  admin_notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  reviewed_at DATETIME,
  FOREIGN KEY (submitted_by) REFERENCES users(id),
  FOREIGN KEY (admin_id) REFERENCES users(id),
  UNIQUE(content_type, content_id)
);

CREATE INDEX IF NOT EXISTS idx_pending_approvals_status ON pending_approvals(status);
CREATE INDEX IF NOT EXISTS idx_pending_approvals_content_type ON pending_approvals(content_type);
CREATE INDEX IF NOT EXISTS idx_pending_approvals_created_at ON pending_approvals(created_at);

-- Add approval_required flag to questions and exams
ALTER TABLE questions ADD COLUMN requires_approval INTEGER DEFAULT 0;
ALTER TABLE exams ADD COLUMN requires_approval INTEGER DEFAULT 0;
