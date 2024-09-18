from flask import Blueprint

user_bp = Blueprint('user', __name__)
admin_bp = Blueprint('admin', __name__)
emt_bp = Blueprint('emt', __name__)

from . import user_routes, admin_routes, emt_routes
