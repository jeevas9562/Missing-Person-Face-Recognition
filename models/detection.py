import cv2
import os

def detect_faces(image_path):
    img = cv2.imread(image_path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Draw rectangles on detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Save detected faces
    detected_image_path = os.path.join('static/uploads/', 'detected_' + os.path.basename(image_path))
    cv2.imwrite(detected_image_path, img)

    return {
        "message": "Face detection complete",
        "image_path": detected_image_path,
        "faces_detected": len(faces)
    }
