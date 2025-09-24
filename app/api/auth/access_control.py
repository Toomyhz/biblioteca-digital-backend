# access_control.py
from functools import wraps
from flask import jsonify
from flask_login import current_user, login_required

def roles_required(*roles):
    def wrapper(view):
        @wraps(view)
        @login_required
        def inner(*args, **kwargs):
            if getattr(current_user, "rol", None) not in roles:
                return jsonify({"message": "Forbidden", "required": roles}), 403
            return view(*args, **kwargs)
        return inner 
    return wrapper