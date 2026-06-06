from app import create_app, db
from app.models.user import User
from app.models.trip import Trip
from app.models.vehicle import Vehicle

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Trip': Trip,
        'Vehicle': Vehicle
    }

if __name__ == '__main__':
    app.run(debug=True)