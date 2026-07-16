from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db, bcrypt
from models.usuario import Usuario
from utils.decorators import admin_required

usuarios = Blueprint("usuarios", __name__, url_prefix="/usuarios")

ROLES = ("Administrador", "Empleado")


@usuarios.route("/")
@login_required
@admin_required
def listar():
    lista = Usuario.query.order_by(Usuario.nombre).all()
    return render_template("usuarios/listar.html", usuarios=lista)


@usuarios.route("/crear", methods=["GET", "POST"])
@login_required
@admin_required
def crear():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        correo = (request.form.get("correo") or "").strip().lower()
        password = request.form.get("password") or ""
        password2 = request.form.get("password2") or ""
        rol = request.form.get("rol") or "Empleado"
        activo = request.form.get("activo") == "on"

        if not nombre or not correo or not password:
            flash("Nombre, correo y contraseña son obligatorios.", "danger")
            return render_template("usuarios/form.html", usuario=None, roles=ROLES)

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return render_template("usuarios/form.html", usuario=None, roles=ROLES)

        if password != password2:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("usuarios/form.html", usuario=None, roles=ROLES)

        if rol not in ROLES:
            rol = "Empleado"

        if Usuario.query.filter(db.func.lower(Usuario.correo) == correo).first():
            flash("Ya existe un usuario con ese correo.", "danger")
            return render_template("usuarios/form.html", usuario=None, roles=ROLES)

        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
            rol=rol,
            activo=activo,
        )
        db.session.add(usuario)
        db.session.commit()
        flash(f"Usuario {nombre} creado correctamente.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/form.html", usuario=None, roles=ROLES)


@usuarios.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        correo = (request.form.get("correo") or "").strip().lower()
        rol = request.form.get("rol") or "Empleado"
        activo = request.form.get("activo") == "on"
        nueva_password = request.form.get("password") or ""
        password2 = request.form.get("password2") or ""

        if not nombre or not correo:
            flash("Nombre y correo son obligatorios.", "danger")
            return render_template("usuarios/form.html", usuario=usuario, roles=ROLES)

        if rol not in ROLES:
            rol = "Empleado"

        # No permitir desactivarse o quitarse el rol admin a sí mismo
        if usuario.id == current_user.id:
            activo = True
            rol = "Administrador"

        otra = Usuario.query.filter(
            db.func.lower(Usuario.correo) == correo,
            Usuario.id != usuario.id,
        ).first()
        if otra:
            flash("Ya existe un usuario con ese correo.", "danger")
            return render_template("usuarios/form.html", usuario=usuario, roles=ROLES)

        # Evitar dejar la empresa sin administradores activos
        if usuario.is_admin and (rol != "Administrador" or not activo):
            otros_admins = Usuario.query.filter(
                Usuario.rol == "Administrador",
                Usuario.activo.is_(True),
                Usuario.id != usuario.id,
            ).count()
            if otros_admins == 0:
                flash(
                    "Debe existir al menos un administrador activo.",
                    "danger",
                )
                return render_template("usuarios/form.html", usuario=usuario, roles=ROLES)

        if nueva_password:
            if len(nueva_password) < 6:
                flash("La contraseña debe tener al menos 6 caracteres.", "danger")
                return render_template("usuarios/form.html", usuario=usuario, roles=ROLES)
            if nueva_password != password2:
                flash("Las contraseñas no coinciden.", "danger")
                return render_template("usuarios/form.html", usuario=usuario, roles=ROLES)
            usuario.password = bcrypt.generate_password_hash(nueva_password).decode(
                "utf-8"
            )

        usuario.nombre = nombre
        usuario.correo = correo
        usuario.rol = rol
        usuario.activo = activo
        db.session.commit()
        flash("Usuario actualizado.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/form.html", usuario=usuario, roles=ROLES)


@usuarios.route("/mi-cuenta", methods=["GET", "POST"])
@login_required
def mi_cuenta():
    """Cambio de contraseña del usuario autenticado."""
    if request.method == "POST":
        actual = request.form.get("password_actual") or ""
        nueva = request.form.get("password_nueva") or ""
        nueva2 = request.form.get("password_nueva2") or ""

        if not bcrypt.check_password_hash(current_user.password, actual):
            flash("La contraseña actual no es correcta.", "danger")
            return render_template("usuarios/mi_cuenta.html")

        if len(nueva) < 6:
            flash("La nueva contraseña debe tener al menos 6 caracteres.", "danger")
            return render_template("usuarios/mi_cuenta.html")

        if nueva != nueva2:
            flash("Las contraseñas nuevas no coinciden.", "danger")
            return render_template("usuarios/mi_cuenta.html")

        current_user.password = bcrypt.generate_password_hash(nueva).decode("utf-8")
        db.session.commit()
        flash("Contraseña actualizada correctamente.", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("usuarios/mi_cuenta.html")
