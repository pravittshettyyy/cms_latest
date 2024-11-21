import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = 'secret_key'  # Required for session management

# Configurations for file uploads
UPLOAD_FOLDER = 'uploads'
os.makedirs(os.path.join(UPLOAD_FOLDER, 'assignments'), exist_ok=True)  # For assignment submissions
os.makedirs(os.path.join(UPLOAD_FOLDER, 'lessons'), exist_ok=True)  # For lessons
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mock data
assignments = []  # Stores uploaded assignments
submissions = []  # Stores student submissions

# User credentials
USER_CREDENTIALS = {
    "teacher": "1",
    "student": "2"
}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    # Authenticate user
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        session['username'] = username
        if username == "teacher":
            return redirect(url_for('teacher_dashboard'))
        elif username == "student":
            return redirect(url_for('student_dashboard'))
    return "Invalid credentials! <a href='/'>Go back</a>"

@app.route("/teacher_dashboard")
def teacher_dashboard():
    if 'username' in session and session['username'] == "teacher":
        return render_template("teacher_dashboard.html")
    return redirect(url_for('index'))

@app.route("/student_dashboard")
def student_dashboard():
    if 'username' in session and session['username'] == "student":
        return render_template("student_dashboard.html")
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/upload_lesson", methods=["GET", "POST"])
def upload_lesson():
    if 'username' in session and session['username'] == "teacher":
        if request.method == "POST":
            title = request.form['title']
            file = request.files['file']
            
            if file and file.filename.endswith('.pdf'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'lessons', file.filename)
                file.save(filepath)
                return redirect(url_for('teacher_dashboard'))
            else:
                return "Only PDF files are allowed!", 400

        return render_template("upload_lesson.html")
    return redirect(url_for('index'))

@app.route("/upload_assignment", methods=["GET", "POST"])
def upload_assignment():
    if 'username' in session and session['username'] == "teacher":
        if request.method == "POST":
            title = request.form['title']
            description = request.form['description']
            due_date = request.form['due_date']
            
            assignments.append({
                "id": len(assignments) + 1,
                "title": title,
                "description": description,
                "due_date": due_date
            })
            return redirect(url_for('teacher_dashboard'))

        return render_template("upload_assignment.html")
    return redirect(url_for('index'))

@app.route("/lessons")
def view_lessons():
    if 'username' in session and session['username'] == "student":
        lesson_files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'lessons'))
        lessons = [
            {"title": os.path.splitext(f)[0], "url": url_for('serve_lesson', filename=f)} for f in lesson_files
        ]
        return render_template("lessons.html", lessons=lessons)
    return redirect(url_for('index'))

@app.route("/uploads/lessons/<filename>")
def serve_lesson(filename):
    if 'username' in session and session['username'] == "student":
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'lessons'), filename)
    return redirect(url_for('index'))



@app.route("/student_assignments")
def student_assignments():
    if 'username' in session and session['username'] == "student":
        return render_template("student_assignments.html", assignments=assignments)
    return redirect(url_for('index'))

@app.route("/submit_assignment", methods=["POST"])
def submit_assignment():
    if 'username' in session and session['username'] == "student":
        assignment_id = request.form['assignment_id']
        file = request.files['file']
        
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'assignments', file.filename)
            file.save(filepath)
            submissions.append({
                "assignment_id": int(assignment_id),
                "file": file.filename
            })
            return "Submission successful! <a href='/student_dashboard'>Go back</a>"
        return "Submission failed. No file uploaded!", 400
    return redirect(url_for('index'))

@app.route("/view_submissions")
def view_submissions():
    if 'username' in session and session['username'] == "teacher":
        # Create a list of submissions with assignment titles
        submissions_with_titles = [
            {
                "assignment_title": next(
                    (assignment["title"] for assignment in assignments if assignment["id"] == submission["assignment_id"]),
                    "Unknown Assignment"
                ),
                "file": submission["file"]
            }
            for submission in submissions
        ]
        return render_template("view_submissions.html", submissions=submissions_with_titles)
    return redirect(url_for('index'))

@app.route("/uploads/assignments/<filename>")
def download_submission(filename):
    if 'username' in session and session['username'] == "teacher":
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), filename)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
