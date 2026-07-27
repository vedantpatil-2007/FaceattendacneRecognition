import csv
import os
import sqlite3
from datetime import datetime

ATTENDANCE_FILE = "attendance/attendance.csv"


def mark_attendance(student_info):

    # Create attendance folder
    os.makedirs("attendance", exist_ok=True)

    # Create CSV if it doesn't exist
    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Roll No", "Name", "Date", "Time"])

    roll, name = student_info.split("_", 1)

    today = datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.now().strftime("%H:%M:%S")

    already_marked = False

    with open(ATTENDANCE_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            if len(row) >= 4:
                if row[0] == roll and row[2] == today:
                    already_marked = True
                    break

    if not already_marked:

        # Save to CSV
        with open(ATTENDANCE_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([roll, name, today, current_time])

        # Save to SQLite
        connection = sqlite3.connect("database/attendance.db")
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO attendance
            (roll_no, name, date, time)
            VALUES (?, ?, ?, ?)
            """,
            (roll, name, today, current_time),
        )

        connection.commit()
        connection.close()

        print(f"Attendance Marked: {name}")

    else:
        print(f"{name} already marked today.")