from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from app import db
from app.admin import admin
from app.models.user import User
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from datetime import datetime

@admin.route('/')
@admin.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    total_passengers = User.query.filter_by(role='passenger').count()
    total_drivers = User.query.filter_by(role='driver').count()
    total_trips = Trip.query.count()
    active_trips = Trip.query.filter(
        Trip.status.in_(['pending', 'accepted', 'in_progress'])
    ).count()
    completed_trips = Trip.query.filter_by(status='completed').count()
    total_earnings = db.session.query(
        db.func.sum(Trip.fare)
    ).filter_by(status='completed').scalar() or 0
    pending_drivers = User.query.filter_by(role='driver', is_active=False).all()
    recent_trips = Trip.query.order_by(Trip.requested_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
        total_passengers=total_passengers,
        total_drivers=total_drivers,
        total_trips=total_trips,
        active_trips=active_trips,
        completed_trips=completed_trips,
        total_earnings=total_earnings,
        pending_drivers=pending_drivers,
        recent_trips=recent_trips
    )

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, role='admin').first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('admin/login.html')

@admin.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin.route('/users')
def users():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    passengers = User.query.filter_by(role='passenger').all()
    drivers = User.query.filter_by(role='driver').all()
    return render_template('admin/users.html',
        passengers=passengers,
        drivers=drivers
    )

@admin.route('/approve_driver/<int:driver_id>')
def approve_driver(driver_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    user = User.query.get_or_404(driver_id)
    vehicle = Vehicle.query.filter_by(driver_id=driver_id).first()
    user.is_active = True
    if vehicle:
        vehicle.is_approved = True
    db.session.commit()
    flash(f'Taxista {user.name} aprobado exitosamente.', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/reject_driver/<int:driver_id>')
def reject_driver(driver_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    user = User.query.get_or_404(driver_id)
    db.session.delete(user)
    db.session.commit()
    flash('Taxista rechazado y eliminado.', 'info')
    return redirect(url_for('admin.users'))

@admin.route('/trips')
def trips():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    all_trips = Trip.query.order_by(Trip.requested_at.desc()).all()
    return render_template('admin/trips.html', trips=all_trips)

@admin.route('/deactivate_user/<int:user_id>')
def deactivate_user(user_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    flash(f'Usuario {user.name} desactivado.', 'info')
    return redirect(url_for('admin.users'))
@admin.route('/reports')
def reports():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    from datetime import date, timedelta
    from sqlalchemy import func

    today = date.today()

    total_trips = Trip.query.count()
    total_earnings = db.session.query(func.sum(Trip.fare)).filter_by(status='completed').scalar() or 0
    total_users = User.query.filter(User.role != 'admin').count()
    avg_rating = db.session.query(func.avg(Trip.rating)).filter(Trip.rating != None).scalar() or 0

    # Viajes por día últimos 7 días
    trips_by_day = []
    earnings_by_day = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Trip.query.filter(
            func.date(Trip.requested_at) == day
        ).count()
        amount = db.session.query(func.sum(Trip.fare)).filter(
            func.date(Trip.requested_at) == day,
            Trip.status == 'completed'
        ).scalar() or 0
        trips_by_day.append({'date': day.strftime('%d/%m'), 'count': count})
        earnings_by_day.append({'date': day.strftime('%d/%m'), 'amount': round(float(amount), 2)})

    # Estados de viajes
    status_data = [
        {'label': 'Pendiente', 'count': Trip.query.filter_by(status='pending').count()},
        {'label': 'Aceptado', 'count': Trip.query.filter_by(status='accepted').count()},
        {'label': 'En camino', 'count': Trip.query.filter_by(status='in_progress').count()},
        {'label': 'Completado', 'count': Trip.query.filter_by(status='completed').count()},
        {'label': 'Cancelado', 'count': Trip.query.filter_by(status='cancelled').count()},
    ]

    # Distribución de usuarios
    users_data = [
        {'label': 'Pasajeros', 'count': User.query.filter_by(role='passenger').count()},
        {'label': 'Taxistas', 'count': User.query.filter_by(role='driver').count()},
        {'label': 'Admins', 'count': User.query.filter_by(role='admin').count()},
    ]

    # Top 5 taxistas
    drivers = User.query.filter_by(role='driver', is_active=True).all()
    top_drivers = []
    for driver in drivers:
        completed = Trip.query.filter_by(driver_id=driver.id, status='completed').all()
        if completed:
            total = sum(t.fare for t in completed if t.fare) or 0
            ratings = [t.rating for t in completed if t.rating]
            avg = sum(ratings) / len(ratings) if ratings else None
            top_drivers.append({
                'name': driver.name,
                'completed_trips': len(completed),
                'total_earnings': total,
                'avg_rating': avg
            })
    top_drivers.sort(key=lambda x: x['completed_trips'], reverse=True)
    top_drivers = top_drivers[:5]

    return render_template('admin/reports.html',
        total_trips=total_trips,
        total_earnings=total_earnings,
        total_users=total_users,
        avg_rating=avg_rating,
        trips_by_day=trips_by_day,
        earnings_by_day=earnings_by_day,
        status_data=status_data,
        users_data=users_data,
        top_drivers=top_drivers
    )
from app.models.fare import FareSettings

@admin.route('/fare', methods=['GET', 'POST'])
def fare_settings():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    fare = FareSettings.query.first()
    if request.method == 'POST':
        fare.base_fare = float(request.form.get('base_fare'))
        fare.min_km = float(request.form.get('min_km'))
        fare.price_per_km = float(request.form.get('price_per_km'))
        fare.extra_per_half_km = float(request.form.get('extra_per_half_km'))
        fare.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Tarifas actualizadas exitosamente.', 'success')
        return redirect(url_for('admin.fare_settings'))
    return render_template('admin/fare_settings.html', fare=fare)
from app.models.association import Association

@admin.route('/associations')
def associations():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    assocs = Association.query.all()
    result = []
    for assoc in assocs:
        from app.models.vehicle import Vehicle
        count = Vehicle.query.filter_by(association_name=assoc.abbreviation).count()
        assoc.driver_count = count
        result.append(assoc)
    return render_template('admin/associations.html', associations=result)

@admin.route('/associations/add', methods=['POST'])
def add_association():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    name = request.form.get('name')
    abbreviation = request.form.get('abbreviation')
    assoc = Association(name=name, abbreviation=abbreviation)
    db.session.add(assoc)
    db.session.commit()
    flash(f'Asociación {abbreviation} agregada exitosamente.', 'success')
    return redirect(url_for('admin.associations'))

@admin.route('/associations/edit', methods=['POST'])
def edit_association():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    assoc_id = request.form.get('assoc_id')
    assoc = Association.query.get_or_404(assoc_id)
    assoc.name = request.form.get('name')
    assoc.abbreviation = request.form.get('abbreviation')
    db.session.commit()
    flash('Asociación actualizada exitosamente.', 'success')
    return redirect(url_for('admin.associations'))

@admin.route('/associations/toggle/<int:assoc_id>')
def toggle_association(assoc_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('admin.login'))
    assoc = Association.query.get_or_404(assoc_id)
    assoc.is_active = not assoc.is_active
    db.session.commit()
    flash(f'Asociación {"activada" if assoc.is_active else "desactivada"}.', 'info')
    return redirect(url_for('admin.associations'))