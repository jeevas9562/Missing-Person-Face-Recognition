import face_recognition
import numpy as np
import cv2
from database.db import db
from database.models import MissingPerson, RecognizedFace
from datetime import datetime

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (500, 500))  # Resize to standard dimensions
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    
    # Apply histogram equalization to improve contrast
    equalized = cv2.equalizeHist(gray)
    
    # Convert back to RGB (face_recognition requires RGB format)
    processed_image = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
    
    return processed_image

def recognize_face(image_path):
    processed_image = preprocess_image(image_path)
    unknown_encodings = face_recognition.face_encodings(processed_image, model="large")  # Use 'large' model for accuracy
    face_locations = face_recognition.face_locations(processed_image, model="cnn")  # CNN model for better detection

    if len(unknown_encodings) == 0:
        return {"message": "No face detected"}

    # Fetch missing persons from the database
    missing_persons = MissingPerson.query.all()
    
    if not missing_persons:
        return {"message": "No missing persons in the database"}

    known_encodings = [np.array(person.embedding) for person in missing_persons]
    known_names = [person.name for person in missing_persons]

    results = []
    threshold = 0.4  # Stricter threshold to prevent false matches

    for (top, right, bottom, left), unknown_encoding in zip(face_locations, unknown_encodings):
        distances = face_recognition.face_distance(known_encodings, unknown_encoding)
        best_match_index = np.argmin(distances) if len(distances) > 0 else None
        
        if best_match_index is not None and distances[best_match_index] < threshold:
            matched_person = missing_persons[best_match_index]
            results.append({"name": matched_person.name, "status": "Matched", "confidence": round(1 - distances[best_match_index], 2)})
            
            # Save the recognized face in the database
            recognized_face = RecognizedFace(
                person_id=matched_person.id,
                person_name=matched_person.name,
                image_path=image_path,
                timestamp=datetime.utcnow()
            )
            db.session.add(recognized_face)
            db.session.commit()
        else:
            results.append({"name": "Unknown", "status": "Not Matched"})

    return results
