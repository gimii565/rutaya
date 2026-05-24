from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.location import Location
from app.models.trip import Trip
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/location/update', methods=['POST'])
def update_location():
    if not current_user.is_authenticated:
        return jsonify({'error': 'No autenticado'}), 401
    data = request.get_json()
    lat = data.get('latitude')
    lng = data.get('longitude')
    if not lat or not lng:
        return jsonify({'error': 'Datos incompletos'}), 400
    location = Location.query.filter_by(user_id=current_user.id).first()
    if location:
        location.latitude = lat
        location.longitude = lng
        location.updated_at = datetime.utcnow()
    else:
        location = Location(
            user_id=current_user.id,
            latitude=lat,
            longitude=lng
        )
        db.session.add(location)
    db.session.commit()
    return jsonify({'success': True})

@api.route('/location/driver/<int:trip_id>')
def get_driver_location(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if not trip.driver_id:
        return jsonify({'found': False})
    location = Location.query.filter_by(user_id=trip.driver_id).first()
    if not location:
        return jsonify({'found': False})
    return jsonify({
        'found': True,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'name': trip.driver.name
    })

@api.route('/location/passenger/<int:trip_id>')
def get_passenger_location(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    location = Location.query.filter_by(user_id=trip.passenger_id).first()
    if not location:
        return jsonify({'found': False})
    return jsonify({
        'found': True,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'name': trip.passenger.name,
        'origin': trip.origin,
        'destination': trip.destination
    })

@api.route('/trips/pending')
def get_pending_trips():
    if not current_user.is_authenticated or current_user.role != 'driver':
        return jsonify({'error': 'No autorizado'}), 401
    trips = Trip.query.filter_by(status='pending').all()
    result = []
    for trip in trips:
        location = Location.query.filter_by(user_id=trip.passenger_id).first()
        result.append({
            'id': trip.id,
            'passenger': trip.passenger.name,
            'origin': trip.origin,
            'destination': trip.destination,
            'latitude': location.latitude if location else None,
            'longitude': location.longitude if location else None
        })
    return jsonify(result)
from app.models.message import Message

@api.route('/messages/<int:trip_id>')
def get_messages(trip_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'No autenticado'}), 401
    messages = Message.query.filter_by(trip_id=trip_id).order_by(Message.sent_at.asc()).all()
    result = []
    for msg in messages:
        result.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.name,
            'content': msg.content,
            'sent_at': msg.sent_at.strftime('%H:%M'),
            'is_mine': msg.sender_id == current_user.id
        })
    return jsonify(result)

@api.route('/messages/send', methods=['POST'])
def send_message():
    if not current_user.is_authenticated:
        return jsonify({'error': 'No autenticado'}), 401
    data = request.get_json()
    trip_id = data.get('trip_id')
    content = data.get('content')
    if not trip_id or not content:
        return jsonify({'error': 'Datos incompletos'}), 400
    message = Message(
        trip_id=trip_id,
        sender_id=current_user.id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({'success': True, 'message_id': message.id})