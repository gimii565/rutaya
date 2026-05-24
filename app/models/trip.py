from app import db
from datetime import datetime

class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    origin = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), default='pending')
    # pending, accepted, in_progress, completed, cancelled
    fare = db.Column(db.Float, nullable=True)
    distance = db.Column(db.Float, nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<Trip {self.id} - {self.status}>'