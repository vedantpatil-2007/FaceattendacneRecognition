import os
import shutil
import base64
import numpy as np
import cv2
import sqlite3
import subprocess
import sys

from recognize_api import recognize_face

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib import colors
from flask import Flask, render_template, redirect, request, flash, session, jsonify, send_file
from openpyxl import Workbook
from datetime import datetime

app = Flask(__name__)
app.secret_key = "face_attendance_secret"

camera_status = "Ready"
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["logged_in"] = True

            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template(
        "login.html",
        error=""
    )

# ==========================
# Dashboard
# ==========================
@app.route("/")
def home():

    if "logged_in" not in session:
     return redirect("/login")

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Today's Attendance
    today = datetime.now().strftime("%d-%m-%Y")

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date=?",
        (today,)
    )

    today_attendance = cursor.fetchone()[0]

    # Recent Attendance
    cursor.execute("""
        SELECT roll_no, name, date, time
        FROM attendance
        ORDER BY id DESC
        LIMIT 10
    """)

    recent_attendance = cursor.fetchall()

    connection.close()

    return render_template(
        "index.html",
        total_students=total_students,
        today_attendance=today_attendance,
        recent_attendance=recent_attendance,
        camera_status=camera_status
    )


# ==========================
# Students Page
# ==========================
@app.route("/students")
def students():

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT roll_no, name, department, year
        FROM students
        ORDER BY roll_no
    """)

    students = cursor.fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=students
    )
# ==========================
# Attendance Page
# ==========================
@app.route("/attendance")
def attendance():

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT roll_no, name, date, time
        FROM attendance
        ORDER BY id DESC
    """)

    attendance = cursor.fetchall()

    connection.close()

    return render_template(
        "attendance.html",
        attendance=attendance
    )
# ==========================
# Export Attendance to Excel
# ==========================
@app.route("/export-excel")
def export_excel():

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT roll_no, name, date, time
        FROM attendance
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    connection.close()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"

    sheet.append([
        "Roll No",
        "Name",
        "Date",
        "Time"
    ])

    for row in data:
        sheet.append(row)

    filename = "attendance_report.xlsx"

    workbook.save(filename)

    return send_file(
        filename,
        as_attachment=True
    )
# ==========================
# Export Attendance to PDF
# ==========================
@app.route("/export-pdf")
def export_pdf():

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT roll_no, name, date, time
        FROM attendance
        ORDER BY id DESC
    """)

    attendance = cursor.fetchall()

    connection.close()

    filename = "attendance_report.pdf"

    document = SimpleDocTemplate(filename)

    data = [
        ["Roll No", "Name", "Date", "Time"]
    ]

    for row in attendance:
        data.append(list(row))

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0,0), (-1,0), 12)

    ]))

    document.build([table])

    return send_file(
        filename,
        as_attachment=True
    )
# ==========================
# Add Student
# ==========================
@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        roll_no = request.form["roll_no"]
        student_name = request.form["student_name"]
        department = request.form["department"]
        year = request.form["year"]

        # Open webcam and capture face
        subprocess.run([
            sys.executable,
            "register.py",
            roll_no,
            student_name,
            department,
            year
        ])

        # Train model automatically
        subprocess.run([
            sys.executable,
            "train.py"
        ])

        flash("Student Added Successfully!", "success")

        return redirect("/students")

    return render_template("add_student.html")


# ==========================
# Edit Student
# ==========================
@app.route("/edit-student/<roll_no>", methods=["GET", "POST"])
def edit_student(roll_no):

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    if request.method == "POST":

        new_roll = request.form["roll_no"]
        student_name = request.form["student_name"]
        department = request.form["department"]
        year = request.form["year"]

        cursor.execute("""
            UPDATE students
            SET roll_no=?,
                name=?,
                department=?,
                year=?
            WHERE roll_no=?
        """, (
            new_roll,
            student_name,
            department,
            year,
            roll_no
        ))

        connection.commit()
        connection.close()

        flash("Student Updated Successfully!", "warning")

        return redirect("/students")

    cursor.execute("""
        SELECT roll_no, name, department, year
        FROM students
        WHERE roll_no=?
    """, (roll_no,))

    student = cursor.fetchone()

    connection.close()

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route("/delete-student/<roll_no>")
def delete_student(roll_no):

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    # Get student name
    cursor.execute(
        "SELECT name FROM students WHERE roll_no=?",
        (roll_no,)
    )

    student = cursor.fetchone()

    if student:

        student_name = student[0]

        folder_name = f"{roll_no}_{student_name}"

        folder_path = os.path.join("dataset", folder_name)

        # Delete dataset folder
        if os.path.exists(folder_path):

            shutil.rmtree(folder_path)

    # Delete from database
    cursor.execute(
        "DELETE FROM students WHERE roll_no=?",
        (roll_no,)
    )

    connection.commit()
    connection.close()

    # Retrain the model
    subprocess.run([
        sys.executable,
        "train.py"
    ])

    flash("Student Deleted Successfully!", "danger")

    return redirect("/students")

# ==========================
# Reports
# ==========================
@app.route("/reports")
def reports():

    if "logged_in" not in session:
        return redirect("/login")

    connection = sqlite3.connect("database/attendance.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    today = datetime.now().strftime("%d-%m-%Y")

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE date=?",
        (today,)
    )

    today_attendance = cursor.fetchone()[0]

    percentage = 0

    if total_students > 0:
        percentage = round(
            (today_attendance / total_students) * 100,
            2
        )

    connection.close()

    return render_template(
        "reports.html",
        total_students=total_students,
        today_attendance=today_attendance,
        percentage=percentage,
        today=today
    )
# ==========================
# Start Camera
# ==========================
@app.route("/start-camera")
def start_camera():

    global camera_status

    camera_status = "Running"

    return redirect("/camera")


# ==========================
# Camera Page
# ==========================
@app.route("/camera")
def camera():
    return render_template("camera.html")


@app.route("/recognize-frame", methods=["POST"])
def recognize_frame():

    data = request.get_json()

    image = data["image"]

    # Remove the Base64 header
    image = image.split(",")[1]

    # Decode Base64 to bytes
    image_bytes = base64.b64decode(image)

    # Convert bytes to NumPy array
    np_arr = np.frombuffer(image_bytes, np.uint8)

    # Convert to OpenCV image
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Run face recognition
    name = recognize_face(frame)

    return jsonify({
        "name": name
    })

# ==========================
# Logout
# ==========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ==========================
# Run Flask
# ==========================
if __name__ == "__main__":
    app.run(debug=True)