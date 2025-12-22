import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def gen_uuid():
    return str(uuid.uuid4())

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=gen_uuid, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    process_datetime = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), nullable=False)
    # Use integer foreign key to events.id for better relational integrity
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    s3_key = db.Column(db.String(1024), nullable=False)
    content_type = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship to access Event object and its uuid
    event = db.relationship('Event', backref=db.backref('photos', lazy=True))
