from flask import Blueprint

driver_bp = Blueprint('driver', __name__)

@driver_bp.context_processor
def inject_manifest():
    return {'manifest_url': '/static/manifest-driver.json'}

from app.driver import routes