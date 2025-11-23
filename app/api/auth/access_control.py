from functools import wraps
from flask import jsonify
from flask_login import current_user, login_required


def roles_required(*roles):
    def wrapper(view):
        @wraps(view)
        @login_required
        def inner(*args, **kwargs):
            # Defensa extra: si por alguna razón login_required no bloquea,
            # verificamos igualmente que haya usuario autenticado.
            if not current_user.is_authenticated:
                return jsonify({"message": "Unauthorized"}), 401

            # Si no se especifican roles, actúa como un simple @login_required
            if not roles:
                return view(*args, **kwargs)

            user_role = getattr(current_user, "rol", getattr(current_user, "role", None))

            if user_role not in roles:
                return jsonify({"message": "Forbidden", "required": list(roles)}), 403

            return view(*args, **kwargs)

        return inner

    return wrapper
