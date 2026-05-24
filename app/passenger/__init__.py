from flask import Blueprint

passenger = Blueprint('passenger', __name__)

from app.passenger import routes