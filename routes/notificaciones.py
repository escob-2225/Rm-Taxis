from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.notificacion import Notificacion

notificaciones = Blueprint("notificaciones", __name__, url_prefix="/notificaciones")


@notificaciones.route("/<int:notificacion_id>/leer", methods=["POST"])
@login_required
def marcar_leida(notificacion_id):
    n = Notificacion.query.get_or_404(notificacion_id)
    n.leida = True
    db.session.commit()
    return redirect(url_for("auth.dashboard"))


@notificaciones.route("/leer-todas", methods=["POST"])
@login_required
def marcar_todas():
    Notificacion.query.filter_by(leida=False).update({Notificacion.leida: True})
    db.session.commit()
    flash("Notificaciones marcadas como leídas", "success")
    return redirect(url_for("auth.dashboard"))
