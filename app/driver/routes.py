from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.driver import driver
from app.driver.forms import RegisterForm, LoginForm, AvailabilityForm
from app.models.user import User
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from datetime import datetime

@driver.route('/')
@driver.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    form = AvailabilityForm()
    pending_trips = Trip.query.filter_by(status='pending').all() if current_user.is_available else []
    active_trip = Trip.query.filter_by(
        driver_id=current_user.id
    ).filter(
        Trip.status.in_(['accepted', 'in_progress'])
    ).first()
    total_trips = Trip.query.filter_by(
        driver_id=current_user.id,
        status='completed'
    ).count()
    total_earnings = db.session.query(
        db.func.sum(Trip.fare)
    ).filter_by(
        driver_id=current_user.id,
        status='completed'
    ).scalar() or 0
    return render_template('driver/dashboard.html',
        form=form,
        pending_trips=pending_trips,
        active_trip=active_trip,
        total_trips=total_trips,
        total_earnings=total_earnings
    )

@driver.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.role == 'driver':
        return redirect(url_for('driver.dashboard'))
    from app.models.association import Association
    form = RegisterForm()
    associations = Association.query.filter_by(is_active=True).all()
    form.association_name.choices = [('', 'Selecciona tu asociación')] + [
        (a.abbreviation, f'{a.abbreviation} - {a.name}') for a in associations
    ]
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Ya existe una cuenta con ese correo.', 'danger')
            return redirect(url_for('driver.register'))
        user = User(
            name=form.name.data,
            paternal_lastname=form.paternal_lastname.data,
            maternal_lastname=form.maternal_lastname.data,
            email=form.email.data,
            phone=form.phone.data,
            role='driver',
            is_active=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        vehicle = Vehicle(
            driver_id=user.id,
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            plate=form.plate.data,
            color=form.color.data,
            license_number='N/A',
            mototaxi_card=form.mototaxi_card.data,
            association_name=form.association_name.data,
            is_approved=False
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Registro exitoso. Espera la aprobación del administrador.', 'success')
        return redirect(url_for('driver.login'))
    return render_template('driver/register.html', form=form, associations=associations)

@driver.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'driver':
        return redirect(url_for('driver.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='driver').first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Tu cuenta aún no ha sido aprobada por el administrador.', 'warning')
                return redirect(url_for('driver.login'))
            login_user(user)
            return redirect(url_for('driver.dashboard'))
        flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('driver/login.html', form=form)

@driver.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('driver.login'))

@driver.route('/accept/<int:trip_id>')
def accept_trip(trip_id):
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    trip = Trip.query.get_or_404(trip_id)
    if trip.status != 'pending':
        flash('Este viaje ya no está disponible.', 'warning')
        return redirect(url_for('driver.dashboard'))
    trip.driver_id = current_user.id
    trip.status = 'accepted'
    trip.accepted_at = datetime.utcnow()
    db.session.commit()
    flash('Viaje aceptado exitosamente.', 'success')
    return redirect(url_for('driver.dashboard'))

@driver.route('/start/<int:trip_id>')
def start_trip(trip_id):
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    trip = Trip.query.get_or_404(trip_id)
    if trip.driver_id != current_user.id:
        flash('No tienes permiso para iniciar este viaje.', 'danger')
        return redirect(url_for('driver.dashboard'))
    trip.status = 'in_progress'
    db.session.commit()
    flash('Viaje iniciado.', 'success')
    return redirect(url_for('driver.dashboard'))

@driver.route('/complete/<int:trip_id>')
def complete_trip(trip_id):
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    trip = Trip.query.get_or_404(trip_id)
    if trip.driver_id != current_user.id:
        flash('No tienes permiso para completar este viaje.', 'danger')
        return redirect(url_for('driver.dashboard'))
    trip.status = 'completed'
    trip.completed_at = datetime.utcnow()
    from app.models.fare import FareSettings
    fare_settings = FareSettings.query.first()
    distance = trip.distance or 2
    if fare_settings:
        trip.fare = fare_settings.calculate_fare(distance)
    else:
        trip.fare = round(10 + distance * 3.5, 2)
    db.session.commit()
    flash('Viaje completado exitosamente.', 'success')
    return redirect(url_for('driver.dashboard'))

@driver.route('/trips')
def trips():
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    all_trips = Trip.query.filter_by(
        driver_id=current_user.id
    ).order_by(Trip.requested_at.desc()).all()
    return render_template('driver/trips.html', trips=all_trips)
@driver.route('/earnings')
def earnings():
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    from datetime import date, timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    trips = Trip.query.filter_by(
        driver_id=current_user.id,
        status='completed'
    ).order_by(Trip.requested_at.desc()).all()

    total_earnings = sum(t.fare for t in trips if t.fare) or 0
    total_trips = len(trips)

    today_earnings = sum(
        t.fare for t in trips
        if t.fare and t.requested_at.date() == today
    ) or 0

    week_earnings = sum(
        t.fare for t in trips
        if t.fare and t.requested_at.date() >= week_start
    ) or 0

    month_earnings = sum(
        t.fare for t in trips
        if t.fare and t.requested_at.date() >= month_start
    ) or 0

    return render_template('driver/earnings.html',
        trips=trips,
        total_earnings=total_earnings,
        total_trips=total_trips,
        today_earnings=today_earnings,
        week_earnings=week_earnings,
        month_earnings=month_earnings
    )
@driver.route('/chat/<int:trip_id>')
def chat(trip_id):
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    trip = Trip.query.get_or_404(trip_id)
    if trip.driver_id != current_user.id:
        return redirect(url_for('driver.dashboard'))
    return render_template('driver/chat.html', trip=trip)
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@driver.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated or current_user.role != 'driver':
        return redirect(url_for('driver.login'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            current_user.name = request.form.get('name')
            current_user.paternal_lastname = request.form.get('paternal_lastname')
            current_user.maternal_lastname = request.form.get('maternal_lastname')
            current_user.email = request.form.get('email')
            current_user.phone = request.form.get('phone')
            if 'profile_photo' in request.files:
                photo = request.files['profile_photo']
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(f"driver_{current_user.id}_{photo.filename}")
                    upload_folder = os.path.join('app', 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    photo.save(os.path.join(upload_folder, filename))
                    current_user.profile_photo = filename
            db.session.commit()
            flash('Perfil actualizado exitosamente.', 'success')
        elif action == 'toggle_availability':
            current_user.is_available = not current_user.is_available
            db.session.commit()
            status = 'disponible' if current_user.is_available else 'no disponible'
            flash(f'Ahora estás {status}.', 'info')
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
        return redirect(url_for('driver.profile'))
    return render_template('driver/profile.html')