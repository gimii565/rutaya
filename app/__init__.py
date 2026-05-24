from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'passenger.login'

    @app.context_processor
    def inject_google_maps_key():
        return dict(GOOGLE_MAPS_API_KEY=app.config['GOOGLE_MAPS_API_KEY'])

    from app.passenger import passenger as passenger_bp
    from app.driver import driver as driver_bp
    from app.admin import admin as admin_bp
    from app.api import api as api_bp

    app.register_blueprint(passenger_bp, url_prefix='/passenger')
    app.register_blueprint(driver_bp, url_prefix='/driver')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app