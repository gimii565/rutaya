from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    paternal_lastname = db.Column(db.String(50), nullable=True)
    maternal_lastname = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_available = db.Column(db.Boolean, default=False)
    profile_photo = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trips_as_passenger = db.relationship('Trip', foreign_keys='Trip.passenger_id', backref='passenger', lazy=True)
    trips_as_driver = db.relationship('Trip', foreign_keys='Trip.driver_id', backref='driver', lazy=True)
    vehicle = db.relationship('Vehicle', backref='driver', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.email} - {self.role}>'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))