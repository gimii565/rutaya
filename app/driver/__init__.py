from flask import Blueprint

driver = Blueprint('driver', __name__)

from app.driver import routes