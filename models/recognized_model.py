from database.db import db

class RecognizedFace(db.Model):
    __tablename__ = 'recognized_faces'
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String)
    image_path = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
