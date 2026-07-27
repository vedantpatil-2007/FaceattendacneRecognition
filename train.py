import os
import cv2
import numpy as np

# Create LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []

label_ids = {}
current_id = 0

dataset_path = "dataset"

# Read all student folders
for folder in os.listdir(dataset_path):

    folder_path = os.path.join(dataset_path, folder)

    if not os.path.isdir(folder_path):
        continue

    label_ids[current_id] = folder

    for image_name in os.listdir(folder_path):

        image_path = os.path.join(folder_path, image_name)

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        faces.append(image)
        labels.append(current_id)

    current_id += 1

labels = np.array(labels)

# Train model
recognizer.train(faces, labels)

# Save model
recognizer.save("trainer/trainer.yml")

print("\nTraining Completed Successfully!")
print(f"Students Trained: {len(label_ids)}")

# Save label mapping
with open("trainer/labels.txt", "w") as f:
    for id, name in label_ids.items():
        f.write(f"{id}:{name}\n")