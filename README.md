<div align="center">
  <img src="static/images/logo.png" alt="StudyForge Logo" width="150" height="150" style="border-radius: 20px;">
  <h1>StudyForge</h1>
  <p>A spaced repetition study planner and custom quiz generator.</p>
</div>

## Live Demo
Currently, there is no public live demo available. The application is designed to be run locally.

## About
StudyForge is a lightweight study management application designed for students who want to organize their learning and test their knowledge. It was originally built as a CS50 final project to explore web development using Python and Flask. The scope is focused on essential study tools—specifically, tracking study sessions with a basic spaced repetition algorithm and generating simple multiple-choice quizzes to reinforce material.

## Features
* **User Accounts:** Register and log in to a personalized workspace.
* **Course & Topic Management:** Add your subjects and specific topics to track.
* **Study Session Logging:** Use the built-in Live Pomodoro Timer to automatically track your study duration, or log it manually, and rate your understanding.
* **Spaced Repetition Scheduling:** The app calculates and schedules the optimal date for you to review a topic based on your past understanding scores.
* **Custom Quizzes:** Create multiple-choice question banks and take randomized quizzes. Your quiz scores are automatically evaluated to update your Spaced Repetition interval!
* **Dashboard Analytics:** View a summary of your study time, average understanding, and recent quiz scores.
* **Resource Discovery:** Quickly access pre-generated Google, YouTube, and Wikipedia search links for your topics.

## Tech Stack
| Layer | Technology |
| :--- | :--- |
| Frontend | HTML5, CSS3, Vanilla JavaScript, Bootstrap 5 |
| Backend | Python, Flask, Gunicorn |
| Database | SQLite (local) / PostgreSQL (production) |
| Session Management | Flask-Session (Filesystem) |

## Architecture
The application follows a standard monolithic client-server architecture. The browser client interacts with a Flask web server, which handles all routing, user authentication, and business logic. The backend communicates directly with a local SQLite database (`database.db`) during development, or a managed PostgreSQL database in production, to store user profiles, courses, topics, study sessions, and quiz attempts. Session data is stored locally on the server's filesystem.

## Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/udarshcodes/ssa.git
   cd ssa
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5000`.

## Project Structure
```text
.
├── Procfile               # Gunicorn deployment configuration
├── app.py                 # Main Flask application entry point
├── schema.sql             # SQLite database schema definition
├── schema_postgres.sql    # PostgreSQL schema for production
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Global styles and spatial UI/glassmorphism design
│   ├── images/
│   │   ├── logo.png       # Application logo
│   │   ├── hero_bg.png    # Alternate background image
│   │   └── hero_bg_study.png # Homepage academic background image
│   └── js/
│       └── script.js      # Frontend logic for fetching dashboard analytics
└── templates/             # Jinja2 HTML templates
    ├── layout.html        # Base template with navbar and footer
    ├── index.html         # Homepage with Bento Grid layout
    ├── auth.html          # Consolidated login & register interface
    ├── reset_password.html# Password reset interface
    ├── planner.html       # Study planner and dashboard interface
    ├── quiz.html          # Quiz management interface
    ├── take_quiz.html     # Active quiz interface
    └── quiz_result.html   # Post-quiz results screen
```

## Deployment
StudyForge is configured for easy deployment on Render. Simply create a PostgreSQL instance, a Web Service linked to the repo, and set the `DATABASE_URL` and `SECRET_KEY` environment variables. Initialize the database using the provided `schema_postgres.sql`.

## Key Decisions & What I Learned
* **SQLite for Simplicity:** Chose SQLite as the database engine to keep the application lightweight and entirely self-contained, avoiding the overhead of running a separate database server.
* **Server-Side Rendering:** Used Jinja2 templates instead of a modern frontend framework like React. This reduced complexity for a project of this scope and allowed for faster iteration on the core spaced repetition logic.
* **Basic Spaced Repetition Algorithm:** Implemented a simplified version of the SuperMemo-2 algorithm. Balancing the math for the interval calculations was challenging but necessary to ensure the scheduling felt natural to the user.
* **Vanilla CSS Glassmorphism:** Chose to write custom CSS for the recent redesign rather than relying heavily on utility libraries, allowing for fine-grained control over the backdrop filters and spatial UI depth effects.
