from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(view):
    """Solo administradores activos."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("No tienes permiso para acceder a esta sección.", "danger")
            return redirect(url_for("auth.dashboard"))
        return view(*args, **kwargs)

    return wrapped
