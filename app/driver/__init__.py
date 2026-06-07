from flask import Blueprint

driver = Blueprint('driver', __name__)

@driver.context_processor
def inject_manifest():
    return {'manifest_url': '/static/manifest-driver.json'}

from app.driver import routes