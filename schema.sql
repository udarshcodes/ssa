
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    last_reviewed DATE,
    next_review DATE,
    repetitions INTEGER DEFAULT 0,
    ease_factor REAL DEFAULT 2.5,
    interval_days INTEGER DEFAULT 0,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);


CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER,
    duration_minutes INTEGER NOT NULL,
    understanding INTEGER,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(topic_id) REFERENCES topics(id)
);


CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT,
    option_d TEXT,
    correct_option TEXT NOT NULL,
    FOREIGN KEY(topic_id) REFERENCES topics(id)
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER,                    
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(topic_id) REFERENCES topics(id)
);
