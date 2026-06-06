from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.passenger import passenger
from app.passenger.forms import RegisterForm, LoginForm, RequestTripForm
from app.models.user import User
from app.models.trip import Trip
from datetime import datetime

@passenger.route('/')
@passenger.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated or current_user.role != 'passenger':
        return redirect(url_for('passenger.login'))
    active_trip = Trip.query.filter_by(
        passenger_id=current_user.id
    ).filter(
        Trip.status.in_(['pending', 'accepted', 'in_progress'])
    ).first()
    return render_template('passenger/dashboard.html', active_trip=active_trip)

@passenger.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'passenger':
            return redirect(url_for('passenger.dashboard'))
        else:
            logout_user()
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Ya existe una cuenta con ese correo.', 'danger')
            return redirect(url_for('passenger.register'))
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            role='passenger'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
        return redirect(url_for('passenger.login'))
    return render_template('passenger/register.html', form=form)

@passenger.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'passenger':
        return redirect(url_for('passenger.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='passenger').first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('passenger.dashboard'))
        flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('passenger/login.html', form=form)

@passenger.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('passenger.login'))

@passenger.route('/request', methods=['GET', 'POST'])
def request_trip():
    if not current_user.is_authenticated or current_user.role != 'passenger':
        return redirect(url_for('passenger.login'))
    form = RequestTripForm()
    if form.validate_on_submit():
        trip = Trip(
            passenger_id=current_user.id,
            origin=form.origin.data,
            destination=form.destination.data,
            status='pending'
        )
        db.session.add(trip)
        db.session.commit()
        flash('Taxi solicitado exitosamente. Espera un conductor.', 'success')
        return redirect(url_for('passenger.dashboard'))
    return render_template('passenger/request_trip.html', form=form)

@passenger.route('/history')
def history():
    if not current_user.is_authenticated or current_user.role != 'passenger':
        return redirect(url_for('passenger.login'))
    trips = Trip.query.filter_by(passenger_id=current_user.id).order_by(Trip.requested_at.desc()).all()
    return render_template('passenger/history.html', trips=trips)
@passenger.route('/rate/<int:trip_id>', methods=['GET', 'POST'])
def rate_trip(trip_id):
    if not current_user.is_authenticated or current_user.role != 'passenger':
        return redirect(url_for('passenger.login'))
    trip = Trip.query.get_or_404(trip_id)
    if trip.passenger_id != current_user.id:
        return redirect(url_for('passenger.dashboard'))
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        if rating:
            trip.rating = int(rating)
            trip.comment = comment
            db.session.commit()
            flash('¡Gracias por tu calificación!', 'success')
        return redirect(url_for('passenger.dashboard'))
    return render_template('passenger/rate_trip.html', trip=trip)

@passenger.route('/cancel/<int:trip_id>')
def cancel_trip(trip_id):
    if not current_user.is_authenticated or current_user.role != 'passenger':
        return redirect(url_for('passenger.login'))
    trip = Trip.query.get_or_404(trip_id)
    if trip.passenger_id != current_user.id:
        flash('No tienes permiso para cancelar este viaje.', 'danger')
        return redirect(url_for('passenger.dashboard'))
    if trip.status in ['pending', 'accepted']:
        trip.status = 'cancelled'
        db.session.commit()
        flash('Viaje cancelado.', 'info')
    return redirect(url_for('passenger.dashboard'))
@passenger.route('/chat/<int:trip_id>')
def chat(trip_id):
    if not current_user.is_authenticated or current_user.role != 'passenger':
        return redirect(url_for('passenger.login'))
    trip = Trip.query.get_or_404(trip_id)
    if trip.passenger_id != current_user.id:
        return redirect(url_for('passenger.dashboard'))
    return render_template('passenger/chat.html', trip=trip)
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@passenger.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated or current_user.role != 'passenger':
        return redirect(url_for('passenger.login'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            current_user.name = request.form.get('name')
            current_user.email = request.form.get('email')
            current_user.phone = request.form.get('phone')
            if 'profile_photo' in request.files:
                photo = request.files['profile_photo']
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(f"user_{current_user.id}_{photo.filename}")
                    upload_folder = os.path.join('app', 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    photo.save(os.path.join(upload_folder, filename))
                    current_user.profile_photo = filename
            db.session.commit()
            flash('Perfil actualizado exitosamente.', 'success')
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            if not current_user.check_password(current_password):
                flash('La contraseña actual es incorrecta.', 'danger')
            elif new_password != confirm_password:
                flash('Las contraseñas nuevas no coinciden.', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Contraseña cambiada exitosamente.', 'success')
        return redirect(url_for('passenger.profile'))
    return render_template('passenger/profile.html')