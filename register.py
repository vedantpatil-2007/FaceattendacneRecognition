import cv2
import os
import sqlite3
import sys

# ==========================
# Get Student Details
# ==========================

if len(sys.argv) == 5:

    roll_no = sys.argv[1]
    student_name = sys.argv[2]
    department = sys.argv[3]
    year = sys.argv[4]

else:

    student_name = input("Enter Student Name: ").strip()
    roll_no = input("Enter Roll Number: ").strip()
    department = input("Enter Department: ").strip()
    year = input("Enter Year: ").strip()


# ==========================
# Create Student Folder
# ==========================

folder_name = f"{roll_no}_{student_name}"
save_path = os.path.join("dataset", folder_name)

os.makedirs(save_path, exist_ok=True)


# ==========================
# Load Face Detector
# ==========================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

camera = cv2.VideoCapture(0)

count = 0

print("\nLook at the camera...")
print("Capturing 50 face images...\n")


# ==========================
# Capture Images
# ==========================

while True:

    success, frame = camera.read()

    if not success:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )

    for (x, y, w, h) in faces:

        count += 1

        face = gray[y:y+h, x:x+w]

        filename = os.path.join(save_path, f"{count}.jpg")

        cv2.imwrite(filename, face)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(
            frame,
            f"Images: {count}/50",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    cv2.imshow("Register Student", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    if count >= 50:
        break


camera.release()
cv2.destroyAllWindows()


# ==========================
# Save Student to Database
# ==========================

connection = sqlite3.connect("database/attendance.db")
cursor = connection.cursor()

try:

    cursor.execute("""
        INSERT INTO students
        (roll_no, name, department, year)

        VALUES (?, ?, ?, ?)
    """, (
        roll_no,
        student_name,
        department,
        year
    ))

    connection.commit()

    print(f"\nStudent '{student_name}' registered successfully!")
    print(f"50 images saved in: {save_path}")
    print("Student saved into database successfully!")

except sqlite3.IntegrityError:

    print(f"\nRoll Number '{roll_no}' already exists!")

finally:

    connection.close()