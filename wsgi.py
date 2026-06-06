from app import create_app, db
from app.models.user import User
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.location import Location
from app.models.message import Message
from app.models.fare import FareSettings
from app.models.association import Association

app = create_app()

with app.app_context():
    db.create_all()
    
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            name='Administrador',
            email='admin@rutaya.com',
            phone='00000000',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    fare = FareSettings.query.first()
    if not fare:
        fare = FareSettings(base_fare=6.0, price_per_km=2.0, min_km=3.0, extra_per_half_km=1.0)
        db.session.add(fare)
        db.session.commit()

    if Association.query.count() == 0:
        for name, abbr in [
            ('Asociación de Mototaxistas del Beni', 'ASOMOBI'),
            ('Asociación de Mototaxistas Trinidad', 'AMOT'),
            ('Sindicato de Mototaxistas', 'SINTRAMOT'),
            ('Asociación de Mototaxistas', 'ASMOT'),
            ('Federación de Mototaxistas', 'FEDEMOT'),
        ]:
            db.session.add(Association(name=name, abbreviation=abbr))
        db.session.commit()

if __name__ == '__main__':
    app.run()