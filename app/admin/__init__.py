from flask import Blueprint

admin = Blueprint('admin', __name__)

@admin.context_processor
def inject_manifest():
    return {'manifest_url': '/static/manifest-admin.json'}

from app.admin import routes