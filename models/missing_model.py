from database.db import db

class MissingPerson(db.Model):
    __tablename__='missing_persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact_info = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
