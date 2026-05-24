from app import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    plate = db.Column(db.String(20), unique=True, nullable=False)
    color = db.Column(db.String(30), nullable=False)
    soat = db.Column(db.String(100), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)
    mototaxi_card = db.Column(db.String(50), nullable=True)
    association_name = db.Column(db.String(100), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Vehicle {self.plate}>'