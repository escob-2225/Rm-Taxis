from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.alerta import ConfiguracionAlerta
from services.alertas import procesar_alertas, asegurar_configuracion_alertas

alertas = Blueprint("alertas", __name__, url_prefix="/alertas")


@alertas.route("/")
@login_required
def configurar():
    asegurar_configuracion_alertas()
    configs = ConfiguracionAlerta.query.order_by(ConfiguracionAlerta.dias_antes.desc()).all()
    return render_template("alertas/configurar.html", configs=configs)


@alertas.route("/guardar", methods=["POST"])
@login_required
def guardar():
    configs = ConfiguracionAlerta.query.all()
    for cfg in configs:
        prefix = f"cfg_{cfg.id}_"
        cfg.activo = request.form.get(prefix + "activo") == "on"
        cfg.canal_sistema = request.form.get(prefix + "sistema") == "on"
        cfg.canal_correo = request.form.get(prefix + "correo") == "on"
        cfg.canal_whatsapp = request.form.get(prefix + "whatsapp") == "on"
        cfg.canal_sms = request.form.get(prefix + "sms") == "on"
    db.session.commit()
    flash("Configuración de alertas guardada", "success")
    return redirect(url_for("alertas.configurar"))


@alertas.route("/procesar", methods=["POST"])
@login_required
def procesar():
    creadas = procesar_alertas()
    flash(f"Proceso de alertas ejecutado. Nuevas notificaciones: {creadas}", "info")
    return redirect(url_for("alertas.configurar"))
