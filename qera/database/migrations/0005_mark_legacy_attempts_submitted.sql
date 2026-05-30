UPDATE exam_attempts
SET status = 'submitted'
WHERE status = 'in_progress'
  AND COALESCE(question_order, '[]') = '[]';
