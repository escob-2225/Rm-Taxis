from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import bcrypt, db
from models.usuario import Usuario
from models.vehiculo import Vehiculo
from models.documento import Documento
from models.conductor import Conductor
from models.notificacion import Notificacion
from services.alertas import procesar_alertas

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        correo = (request.form.get("correo") or "").strip().lower()
        password = request.form.get("password") or ""

        usuario = Usuario.query.filter(db.func.lower(Usuario.correo) == correo).first()

        password_ok = False
        if usuario and usuario.password:
            try:
                password_ok = bcrypt.check_password_hash(usuario.password, password)
            except ValueError:
                password_ok = False

        if usuario and password_ok:
            if not usuario.id:
                flash("Usuario inválido en base de datos. Ejecuta crear_admin.py", "danger")
                return redirect(url_for("auth.login"))

            if not usuario.activo:
                flash("Tu cuenta está desactivada. Contacta al administrador.", "danger")
                return redirect(url_for("auth.login"))

            login_user(usuario, remember=True)
            flash(f"Bienvenido, {usuario.nombre}", "success")
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("auth.dashboard"))

        flash("Correo o contraseña incorrectos", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))


@auth.route("/dashboard")
@login_required
def dashboard():
    procesar_alertas()

    total_vehiculos = Vehiculo.query.count()
    activos = Vehiculo.query.filter_by(estado="Activo").count()
    total_conductores = Conductor.query.count()
    docs = Documento.query.all()

    vigentes = sum(1 for d in docs if d.estado == "Vigente")
    proximos = sum(1 for d in docs if d.estado == "Próximo a vencer")
    vencidos = sum(1 for d in docs if d.estado == "Vencido")

    alertas_docs = sorted(
        [d for d in docs if d.estado in ("Próximo a vencer", "Vencido")],
        key=lambda d: d.fecha_vencimiento,
    )[:10]

    notificaciones = (
        Notificacion.query.filter_by(leida=False)
        .order_by(Notificacion.creado_en.desc())
        .limit(8)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_vehiculos=total_vehiculos,
        activos=activos,
        total_conductores=total_conductores,
        vigentes=vigentes,
        proximos=proximos,
        vencidos=vencidos,
        alertas_docs=alertas_docs,
        notificaciones=notificaciones,
    )
