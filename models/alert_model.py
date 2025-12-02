from database.db import db

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    person_name = db.Column(db.String)
    location = db.Column(db.String)
    alert_time = db.Column(db.DateTime, default=db.func.current_timestamp())
