BEGIN TRANSACTION;

INSERT INTO users (name, email, password_hash, role, avatar_url, bio) VALUES
('Admin One', 'admin1@example.com', '$2b$12$CHAa65lgj8WVkfkG5Hlhw.CIu4OLUjcrsPDy33WU8ZJfv/lndDJ/m', 'admin', NULL, 'Platform administrator.'),
('Admin Two', 'admin2@example.com', '$2b$12$cQyWNezYmP5lxowZxHKtAOvf/u33nrf4lxpFzFfeBWJwUjCjHTfc6', 'admin', NULL, 'Platform administrator.'),
('Student One', 'student1@example.com', '$2b$12$11bOKrayPO0MU8hWGEnaseq92UjQ2Vi6Wl/x/8bHT.i6jxs1xKUEq', 'student', NULL, 'Aspiring exam taker.'),
('Student Two', 'student2@example.com', '$2b$12$VkvV2xaWD1cPLXefTBE4G.xOAsudlzQW1yHZmSCXbKU8xvGb0RwPu', 'student', NULL, 'Study group member.'),
('Student Three', 'student3@example.com', '$2b$12$1C/kChoXS.etM7uadBl5YO92MQtjnXDrdV37O8rf/inAgl2lNNPjW', 'student', NULL, 'Practice makes perfect.'),
('Student Four', 'student4@example.com', '$2b$12$SJHEmlBarwJUFHIoe0G9keznQX4.2Kxie.fnvG4qhWn6SvrGH0aKy', 'student', NULL, 'Question curator.'),
('Student Five', 'student5@example.com', '$2b$12$895zGPqMpwYOzizierSU5OmL.pcXi89n2G0cFG587Cy2sTtgkstKy', 'student', NULL, 'Exam builder.');

INSERT INTO tags (name) VALUES
('geography'),
('science'),
('math'),
('chemistry'),
('biology'),
('technology'),
('history'),
('general');

INSERT INTO questions (user_id, title, description, type, correct_answer, difficulty, explanation, is_public) VALUES
(3, 'What is the capital of France?', 'Choose the correct capital city for France.', 'mcq', 'Paris', 'easy', 'Paris is the capital city of France.', 1),
(3, 'Which element has atomic number 1?', 'Identify the chemical element with atomic number one.', 'mcq', 'Hydrogen', 'easy', 'Hydrogen has atomic number one.', 1),
(4, 'The earth orbits the sun.', 'Select true or false: the earth orbits the sun.', 'true_false', 'True', 'easy', 'The earth completes an orbit around the sun every year.', 1),
(4, 'Name the process by which plants make food.', 'Provide the name of the process plants use to convert light energy into food.', 'short_answer', 'Photosynthesis', 'medium', 'Plants use photosynthesis to convert light energy into chemical energy.', 1),
(5, 'Explain the importance of code version control.', 'Describe why version control systems are important for software development teams.', 'descriptive', 'Version control enables collaboration, auditing, and rollback of code changes.', 'medium', 'Version control lets teams collaborate safely, track history, and recover from mistakes.', 1),
(5, 'Which planet is known as the Red Planet?', 'Choose the planet commonly called the Red Planet.', 'mcq', 'Mars', 'easy', 'Mars is often called the Red Planet because of its reddish appearance.', 1),
(6, 'What is 12 multiplied by 8?', 'Select the product of 12 and 8.', 'mcq', '96', 'easy', '12 times 8 equals 96.', 1),
(6, 'Water freezes at 0 degrees Celsius.', 'Determine whether the statement about freezing point is true or false.', 'true_false', 'True', 'easy', 'Water freezes at 0°C under standard conditions.', 1),
(7, 'What is the chemical formula for table salt?', 'Provide the chemical formula for common table salt.', 'short_answer', 'NaCl', 'medium', 'Table salt is sodium chloride, written as NaCl.', 1),
(7, 'Describe the primary purpose of an API.', 'Explain in a few sentences what an API is used for.', 'descriptive', 'An API enables software components to communicate and exchange data.', 'medium', 'APIs allow applications to interact and share functionality through defined interfaces.', 1);

INSERT INTO question_options (question_id, option_text, option_order) VALUES
(1, 'Paris', 1),
(1, 'Berlin', 2),
(1, 'Rome', 3),
(1, 'Madrid', 4),
(2, 'Hydrogen', 1),
(2, 'Helium', 2),
(2, 'Oxygen', 3),
(2, 'Carbon', 4),
(6, 'Mars', 1),
(6, 'Venus', 2),
(6, 'Jupiter', 3),
(6, 'Saturn', 4),
(7, '96', 1),
(7, '88', 2),
(7, '104', 3),
(7, '108', 4);

INSERT INTO question_tags (question_id, tag_id) VALUES
(1, 1),
(1, 8),
(2, 2),
(2, 3),
(3, 2),
(3, 8),
(4, 2),
(4, 5),
(5, 6),
(5, 8),
(6, 2),
(6, 8),
(7, 3),
(7, 8),
(8, 2),
(8, 8),
(9, 2),
(9, 4),
(10, 6),
(10, 8);

INSERT INTO exams (user_id, title, description, duration_minutes, total_marks, is_public, randomize_order) VALUES
(4, 'General Knowledge Quiz', 'A short quiz covering general knowledge topics.', 15, 6, 1, 0),
(5, 'Science Review Exam', 'A science-focused exam with mixed question types.', 25, 12, 1, 0);

INSERT INTO exam_questions (exam_id, question_id, marks, question_order) VALUES
(1, 1, 2, 1),
(1, 3, 2, 2),
(1, 6, 2, 3),
(2, 2, 3, 1),
(2, 4, 3, 2),
(2, 8, 3, 3),
(2, 9, 3, 4);

INSERT INTO exam_attempts (exam_id, user_id, attempt_number, score, total_marks, time_taken_seconds, submitted_at, answers) VALUES
(1, 3, 1, 6, 6, 120, datetime('now'), '{"1":"Paris","3":"True","6":"Mars"}'),
(1, 4, 1, 4, 6, 180, datetime('now'), '{"1":"Berlin","3":"True","6":"Venus"}'),
(1, 3, 2, 5, 6, 210, datetime('now'), '{"1":"Paris","3":"True","6":"Mars"}');

INSERT INTO leaderboard (exam_id, user_id, attempt_id, score, time_taken_seconds, rank) VALUES
(1, 3, 1, 6, 120, 1),
(1, 4, 2, 4, 180, 2);

INSERT INTO bookmarks (user_id, question_id) VALUES
(3, 5),
(4, 1);

COMMIT;
