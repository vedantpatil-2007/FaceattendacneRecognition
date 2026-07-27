import sqlite3
import os

# Create database folder if it doesn't exist
os.makedirs("database", exist_ok=True)

# Database path
DB_PATH = "database/attendance.db"

# Connect to database
connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()

# -------------------------
# STUDENTS TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    roll_no TEXT UNIQUE,

    name TEXT,

    department TEXT,

    year TEXT

)
""")

# -------------------------
# ATTENDANCE TABLE
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    roll_no TEXT,

    name TEXT,

    date TEXT,

    time TEXT

)
""")

connection.commit()

connection.close()

print("Database Created Successfully!")
connection = sqlite3.connect("database/attendance.db")
cursor = connection.cursor()

print("\nStudents Table:")
cursor.execute("SELECT * FROM students")
for row in cursor.fetchall():
    print(row)

print("\nAttendance Table:")
cursor.execute("SELECT * FROM attendance")
for row in cursor.fetchall():
    print(row)

connection.close()