
from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Management System</title>
    <style>
        body {
            font-family: Arial;
            background: #eef2ff;
            margin: 0;
            padding: 30px;
        }
        .container {
            max-width: 900px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 12px;
        }
        h1 { color: #3730a3; }
        input, button {
            padding: 10px;
            margin: 5px 0;
            border-radius: 6px;
            border: 1px solid #ccc;
        }
        button {
            background: #4f46e5;
            color: white;
            cursor: pointer;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th { background: #e0e7ff; }
        a { color: #4338ca; }
        .delete { color: #dc2626; }
    </style>
</head>
<body>
<div class="container">
    <h1>Student Management System 🎓</h1>
    <p>Add and manage student records easily!</p>

    <h2>Add Student</h2>
    <form action="/add" method="POST">
        <input name="name" placeholder="Student Name" required>
        <input name="department" placeholder="Department" required>
        <input name="email" type="email" placeholder="Email" required>
        <button type="submit">Add Student</button>
    </form>

    <h2>Search Students</h2>
    <form action="/" method="GET">
        <input name="search" placeholder="Search name or department"
               value="{{ search }}">
        <button type="submit">Search</button>
        <a href="/">Show All</a>
    </form>

    <h2>Student Records</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Department</th>
            <th>Email</th>
            <th>Actions</th>
        </tr>
        {% for student in students %}
        <tr>
            <td>{{ student['id'] }}</td>
            <td>{{ student['name'] }}</td>
            <td>{{ student['department'] }}</td>
            <td>{{ student['email'] }}</td>
            <td>
                <a href="/edit/{{ student['id'] }}">Edit</a> |
                <a class="delete"
                   href="/delete/{{ student['id'] }}"
                   onclick="return confirm('Delete this student?')">
                   Delete
                </a>
            </td>
        </tr>
        {% endfor %}
    </table>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    search = request.args.get("search", "").strip()
    conn = get_db()

    if search:
        students = conn.execute(
            """SELECT * FROM students
            WHERE name LIKE ? OR department LIKE ?
            ORDER BY id DESC""",
            (f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return render_template_string(
        HTML, students=students, search=search
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form["name"].strip()
    department = request.form["department"].strip()
    email = request.form["email"].strip()

    if name and department and email:
        conn = get_db()
        conn.execute(
            "INSERT INTO students (name, department, email) VALUES (?, ?, ?)",
            (name, department, email)
        )
        conn.commit()
        conn.close()

    return redirect("/")


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db()

    if request.method == "POST":
        name = request.form["name"].strip()
        department = request.form["department"].strip()
        email = request.form["email"].strip()

        if name and department and email:
            conn.execute(
                """UPDATE students
                SET name=?, department=?, email=?
                WHERE id=?""",
                (name, department, email, student_id)
            )
            conn.commit()

        conn.close()
        return redirect("/")

    student = conn.execute(
        "SELECT * FROM students WHERE id=?", (student_id,)
    ).fetchone()
    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template_string("""
        <h1>Edit Student</h1>
        <form method="POST">
            <p>Name: <input name="name"
                value="{{ student['name'] }}" required></p>
            <p>Department: <input name="department"
                value="{{ student['department'] }}" required></p>
            <p>Email: <input name="email" type="email"
                value="{{ student['email'] }}" required></p>
            <button type="submit">Save Changes</button>
            <a href="/">Cancel</a>
        </form>
    """, student=student)


@app.route("/delete/<int:student_id>")
def delete_student(student_id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    get_db().close()
    app.run(host="0.0.0.0", port=5000, debug=True)
