from database.db import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # New column for admin role

class MissingPerson(db.Model):
    __tablename__ = 'missing_persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)  
    contact_info = db.Column(db.String, nullable=False)  
    image_path = db.Column(db.String, nullable=False)
    embedding = db.Column(db.ARRAY(db.Float, dimensions=1)) 
    
    # Relationship with RecognizedFace
    recognized_faces = db.relationship('RecognizedFace', backref='missing_person')  # Use backref for automatic linkage

    # Relationship with Alert
    alerts = db.relationship("Alert", backref="missing_person")  # Use backref instead of back_populates

class RecognizedFace(db.Model):
    __tablename__ = 'recognized_faces'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('missing_persons.id'), nullable=False)  
    person_name = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Backref automatically establishes missing_person relationship

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('missing_persons.id'), nullable=False)  
    person_name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    alert_time = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Backref automatically establishes missing_person relationship
