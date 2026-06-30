import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime, timedelta


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.environ.get("SECRET_KEY", "fallback_dev_key")
Session(app)

db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

db = SQL(db_url if db_url else "sqlite:///database.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show homepage"""
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Must provide username")
            return render_template("auth.html", active_tab="register")
        if not password:
            flash("Must provide password")
            return render_template("auth.html", active_tab="register")
        if password != confirmation:
            flash("Passwords do not match")
            return render_template("auth.html", active_tab="register")

        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            flash("Username already exists")
            return render_template("auth.html", active_tab="register")

        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed_password)

        flash("Registered successfully!")
        return redirect("/login")

    else:
        return render_template("auth.html", active_tab="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username")
            return render_template("auth.html", active_tab="login")
        if not password:
            flash("Must provide password")
            return render_template("auth.html", active_tab="login")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password")
            return render_template("auth.html", active_tab="login")

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        flash("Logged in successfully!")
        return redirect("/")

    else:
        return render_template("auth.html", active_tab="login")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    """Reset user password"""
    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not username or not new_password or not confirmation:
            flash("Must provide username and new password details")
            return render_template("reset_password.html")
        
        if new_password != confirmation:
            flash("Passwords do not match")
            return render_template("reset_password.html")

        # Verify username exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1:
            flash("Username not found")
            return render_template("reset_password.html")

        hashed_password = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE username = ?", hashed_password, username)

        flash("Password reset successfully! You can now log in.")
        return redirect("/login")
    else:
        return render_template("reset_password.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")


@app.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    """Manage study planner"""
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_course":
            course_name = request.form.get("course_name")
            if not course_name:
                flash("Course name cannot be empty", "danger")
                return redirect("/planner")
            db.execute("INSERT INTO courses (user_id, name) VALUES (?, ?)", user_id, course_name)
            flash("Course added successfully!", "success")
            return redirect("/planner")

        elif action == "add_topic":
            course_id = request.form.get("course_id")
            topic_name = request.form.get("topic_name")
            if not course_id or not topic_name:
                flash("Missing course or topic name", "danger")
                return redirect("/planner")

            db.execute("INSERT INTO topics (course_id, name, last_reviewed, next_review, repetitions, ease_factor, interval_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       course_id, topic_name, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'), 0, 2.5, 0)
            flash("Topic added successfully!", "success")
            return redirect("/planner")

        elif action == "log_session":
            topic_id = request.form.get("topic_id")
            duration_minutes = request.form.get("duration_minutes")
            understanding = request.form.get("understanding")
            notes = request.form.get("notes")

            if not topic_id or not duration_minutes or not understanding:
                flash("Missing session details", "danger")
                return redirect("/planner")

            try:
                duration_minutes = int(duration_minutes)
                understanding = int(understanding)
                if not (1 <= understanding <= 5):
                    raise ValueError("Understanding must be between 1 and 5")
            except ValueError as e:
                flash(f"Invalid duration or understanding: {e}", "danger")
                return redirect("/planner")

            db.execute(
                "INSERT INTO study_sessions (user_id, topic_id, duration_minutes, understanding, notes) VALUES (?, ?, ?, ?, ?)",
                user_id, topic_id, duration_minutes, understanding, notes
            )

            topic_data = db.execute(
                "SELECT repetitions, ease_factor, interval_days FROM topics WHERE id = ?", topic_id)
            if not topic_data:
                flash("Topic not found for session logging.", "danger")
                return redirect("/planner")

            current_reps = topic_data[0]["repetitions"]
            current_ease = topic_data[0]["ease_factor"]
            current_interval = topic_data[0]["interval_days"]

            new_ease = current_ease + (0.1 - (5 - understanding) *
                                       (0.08 + (5 - understanding) * 0.02))
            if new_ease < 1.3:
                new_ease = 1.3

            new_interval = 0
            if understanding < 3:
                new_reps = 0
                new_interval = 0
            else:
                new_reps = current_reps + 1
                if new_reps == 1:
                    new_interval = 1
                elif new_reps == 2:
                    new_interval = 6
                else:
                    new_interval = round(current_interval * new_ease)

            if new_interval < 0:
                new_interval = 0

            # Determine next review date
            if new_interval == 0:
                next_review_date = datetime.now()
            else:
                next_review_date = datetime.now() + timedelta(days=new_interval)

            db.execute("UPDATE topics SET last_reviewed = ?, next_review = ?, repetitions = ?, ease_factor = ?, interval_days = ? WHERE id = ?",
                       datetime.now().strftime('%Y-%m-%d'),
                       next_review_date.strftime('%Y-%m-%d'),
                       new_reps,
                       new_ease,
                       new_interval,
                       topic_id)

            flash("Study session logged!", "success")
            return redirect("/planner")

        elif action == "delete_course":
            course_id = request.form.get("course_id")
            if not course_id:
                flash("Missing course ID to delete", "danger")
                return redirect("/planner")

            db.execute(
                "DELETE FROM study_sessions WHERE topic_id IN (SELECT id FROM topics WHERE course_id = ?)", course_id)
            db.execute(
                "DELETE FROM quiz_attempts WHERE topic_id IN (SELECT id FROM topics WHERE course_id = ?)", course_id)
            db.execute(
                "DELETE FROM questions WHERE topic_id IN (SELECT id FROM topics WHERE course_id = ?)", course_id)
            db.execute("DELETE FROM topics WHERE course_id = ?", course_id)
            db.execute("DELETE FROM courses WHERE id = ? AND user_id = ?", course_id, user_id)
            flash("Course and all associated data deleted!", "success")
            return redirect("/planner")

        elif action == "delete_topic":
            topic_id = request.form.get("topic_id")
            if not topic_id:
                flash("Missing topic ID to delete", "danger")
                return redirect("/planner")

            db.execute("DELETE FROM study_sessions WHERE topic_id = ?", topic_id)
            db.execute("DELETE FROM quiz_attempts WHERE topic_id = ?", topic_id)
            db.execute("DELETE FROM questions WHERE topic_id = ?", topic_id)
            db.execute("DELETE FROM topics WHERE id = ?", topic_id)
            flash("Topic and all associated data deleted!", "success")
            return redirect("/planner")

        else:
            flash("Invalid action", "danger")
            return redirect("/planner")

    else:  # GET request
        courses = db.execute("SELECT * FROM courses WHERE user_id = ?", user_id)
        for course in courses:

            course["topics"] = db.execute(
                "SELECT * FROM topics WHERE course_id = ? ORDER BY next_review ASC, name ASC", course["id"])

        all_topics = db.execute(
            "SELECT t.id, t.name, c.name AS course_name FROM topics t JOIN courses c ON t.course_id = c.id WHERE c.user_id = ? ORDER BY c.name, t.name", user_id)

        today = datetime.now().strftime('%Y-%m-%d')
        topics_due_for_review = db.execute(
            "SELECT t.name, c.name AS course_name, t.next_review FROM topics t JOIN courses c ON t.course_id = c.id WHERE c.user_id = ? AND t.next_review <= ? ORDER BY t.next_review ASC LIMIT 5",
            user_id, today
        )

        all_topics_for_suggestions = db.execute(
            "SELECT t.name, c.name AS course_name FROM topics t JOIN courses c ON t.course_id = c.id WHERE c.user_id = ? ORDER BY c.name, t.name", user_id)

        return render_template("planner.html",
                               courses=courses,
                               all_topics=all_topics,
                               topics_due_for_review=topics_due_for_review,
                               all_topics_for_suggestions=all_topics_for_suggestions)


@app.route("/api/study_dashboard_data")
@login_required
def study_dashboard_data():
    user_id = session["user_id"]

    study_time_per_topic = db.execute(
        "SELECT t.name AS topic_name, SUM(ss.duration_minutes) AS total_minutes "
        "FROM study_sessions ss JOIN topics t ON ss.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        "WHERE c.user_id = ? GROUP BY t.name ORDER BY total_minutes DESC",
        user_id
    )

    avg_understanding_per_topic = db.execute(
        "SELECT t.name AS topic_name, AVG(ss.understanding) AS avg_understanding "
        "FROM study_sessions ss JOIN topics t ON ss.topic_id = t.id JOIN courses c ON t.course_id = c.id "
        # Ascending means lower understanding first
        "WHERE c.user_id = ? GROUP BY t.name ORDER BY avg_understanding ASC",
        user_id
    )

    recent_quiz_scores = db.execute(
        "SELECT qa.score, qa.total_questions, t.name AS topic_name, qa.attempt_date "
        "FROM quiz_attempts qa LEFT JOIN topics t ON qa.topic_id = t.id "
        "WHERE qa.user_id = ? ORDER BY qa.attempt_date DESC LIMIT 5",
        user_id
    )

    return jsonify({
        "study_time_per_topic": study_time_per_topic,
        "avg_understanding_per_topic": avg_understanding_per_topic,
        "recent_quiz_scores": recent_quiz_scores
    })


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """Generate and take quizzes"""
    user_id = session["user_id"]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_question":
            topic_id = request.form.get("topic_id")
            question_text = request.form.get("question_text")
            option_a = request.form.get("option_a")
            option_b = request.form.get("option_b")
            option_c = request.form.get("option_c")
            option_d = request.form.get("option_d")
            correct_option = request.form.get("correct_option")

            if not all([topic_id, question_text, option_a, option_b, correct_option]):
                flash(
                    "Missing question details (Topic, Question, Option A, Option B, Correct Option are required)", "danger")
                return redirect("/quiz")

            db.execute(
                "INSERT INTO questions (topic_id, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
                topic_id, question_text, option_a, option_b, option_c if option_c else None, option_d if option_d else None, correct_option
            )
            flash("Question added successfully!", "success")
            return redirect("/quiz")

        elif action == "start_quiz":
            selected_topic_id = request.form.get("quiz_topic_id")
            questions = []
            if selected_topic_id and selected_topic_id != "all":
                questions = db.execute(
                    "SELECT * FROM questions WHERE topic_id = ? ORDER BY RANDOM() LIMIT 5", selected_topic_id)
            else:
                questions = db.execute(
                    "SELECT q.* FROM questions q JOIN topics t ON q.topic_id = t.id JOIN courses c ON t.course_id = c.id WHERE c.user_id = ? ORDER BY RANDOM() LIMIT 10", user_id)

            if not questions:
                flash("No questions available for selected topic or generally. Add some questions first!", "warning")
                return redirect("/quiz")

            session["current_quiz_questions"] = questions
            session["current_quiz_topic_id"] = selected_topic_id if selected_topic_id != "all" else None

            return render_template("take_quiz.html", questions=questions)

        elif action == "submit_quiz":
            if "current_quiz_questions" not in session:
                flash("No active quiz to submit.", "danger")
                return redirect("/quiz")

            questions = session["current_quiz_questions"]
            quiz_topic_id = session["current_quiz_topic_id"]
            score = 0
            total_questions = len(questions)

            for question in questions:
                user_answer = request.form.get(f"question_{question['id']}")
                if user_answer and user_answer == question["correct_option"]:
                    score += 1

            db.execute("INSERT INTO quiz_attempts (user_id, topic_id, score, total_questions) VALUES (?, ?, ?, ?)",
                       user_id, quiz_topic_id, score, total_questions)

            updated_spaced_repetition = False
            if quiz_topic_id:
                percentage = score / total_questions
                if percentage >= 0.9:
                    understanding = 5
                elif percentage >= 0.8:
                    understanding = 4
                elif percentage >= 0.6:
                    understanding = 3
                elif percentage >= 0.4:
                    understanding = 2
                else:
                    understanding = 1
                
                # Auto log a study session (duration 5 minutes)
                db.execute(
                    "INSERT INTO study_sessions (user_id, topic_id, duration_minutes, understanding, notes) VALUES (?, ?, ?, ?, ?)",
                    user_id, quiz_topic_id, 5, understanding, "Automated Quiz Review"
                )

                # SM-2 Logic
                topic_data = db.execute("SELECT repetitions, ease_factor, interval_days FROM topics WHERE id = ?", quiz_topic_id)
                if topic_data:
                    current_reps = topic_data[0]["repetitions"]
                    current_ease = topic_data[0]["ease_factor"]
                    current_interval = topic_data[0]["interval_days"]

                    new_ease = current_ease + (0.1 - (5 - understanding) * (0.08 + (5 - understanding) * 0.02))
                    if new_ease < 1.3:
                        new_ease = 1.3

                    new_interval = 0
                    if understanding < 3:
                        new_reps = 0
                        new_interval = 0
                    else:
                        new_reps = current_reps + 1
                        if new_reps == 1:
                            new_interval = 1
                        elif new_reps == 2:
                            new_interval = 6
                        else:
                            new_interval = round(current_interval * new_ease)

                    if new_interval < 0:
                        new_interval = 0

                    if new_interval == 0:
                        next_review_date = datetime.now()
                    else:
                        next_review_date = datetime.now() + timedelta(days=new_interval)

                    db.execute("UPDATE topics SET last_reviewed = ?, next_review = ?, repetitions = ?, ease_factor = ?, interval_days = ? WHERE id = ?",
                               datetime.now().strftime('%Y-%m-%d'),
                               next_review_date.strftime('%Y-%m-%d'),
                               new_reps,
                               new_ease,
                               new_interval,
                               quiz_topic_id)
                    updated_spaced_repetition = True

            session.pop("current_quiz_questions", None)
            session.pop("current_quiz_topic_id", None)

            return render_template("quiz_result.html", score=score, total_questions=total_questions, updated_spaced_repetition=updated_spaced_repetition)

    else:
        topics = db.execute(
            "SELECT t.id, t.name, c.name AS course_name FROM topics t JOIN courses c ON t.course_id = c.id WHERE c.user_id = ? ORDER BY c.name, t.name", user_id)
        quiz_attempts = db.execute(
            "SELECT qa.*, t.name AS topic_name FROM quiz_attempts qa LEFT JOIN topics t ON qa.topic_id = t.id WHERE qa.user_id = ? ORDER BY qa.attempt_date DESC LIMIT 10", user_id)
        return render_template("quiz.html", topics=topics, quiz_attempts=quiz_attempts)


@app.route("/api/check_username")
def check_username():
    """Check if a username is available"""
    username = request.args.get("username")
    if not username:
        return jsonify({"available": False})
    
    rows = db.execute("SELECT id FROM users WHERE username = ?", username)
    if rows:
        return jsonify({"available": False})
    else:
        return jsonify({"available": True})


if __name__ == "__main__":
    app.run(debug=True)
