from app import db
from datetime import datetime

class FareSettings(db.Model):
    __tablename__ = 'fare_settings'

    id = db.Column(db.Integer, primary_key=True)
    base_fare = db.Column(db.Float, nullable=False, default=6.0)
    price_per_km = db.Column(db.Float, nullable=False, default=2.0)
    min_km = db.Column(db.Float, nullable=False, default=3.0)
    extra_per_half_km = db.Column(db.Float, nullable=False, default=1.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def calculate_fare(self, distance_km):
        if distance_km <= self.min_km:
            return self.base_fare
        extra_km = distance_km - self.min_km
        extra_halves = extra_km / 0.5
        return round(self.base_fare + (extra_halves * self.extra_per_half_km), 2)

    def __repr__(self):
        return f'<FareSettings base={self.base_fare}>'