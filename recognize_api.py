import cv2
import numpy as np
from attendance import mark_attendance

# Load trained model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/trainer.yml")

# Load labels
labels = {}

with open("trainer/labels.txt", "r") as f:
    for line in f:
        id, name = line.strip().split(":")
        labels[int(id)] = name

# Load face detector
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def recognize_face(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )

    result = "Unknown"

    for (x, y, w, h) in faces:

        face = gray[y:y+h, x:x+w]

        label, confidence = recognizer.predict(face)

        if confidence < 80:

            result = labels[label]

            mark_attendance(result)

            break

    return result