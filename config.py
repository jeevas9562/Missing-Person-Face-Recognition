import os

DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/facenet_face_recognition")
