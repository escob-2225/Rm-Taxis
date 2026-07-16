from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.vehiculo import Vehiculo
from models.documento import Documento
from models.asignacion import AsignacionConductor

vehiculos = Blueprint("vehiculos", __name__, url_prefix="/vehiculos")


@vehiculos.route("/")
@login_required
def listar():
    lista = Vehiculo.query.order_by(Vehiculo.placa).all()
    return render_template("vehiculos/listar.html", vehiculos=lista)


@vehiculos.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        placa = request.form.get("placa", "").strip().upper()
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        anio = request.form.get("anio", type=int)
        color = request.form.get("color", "").strip() or None
        numero_interno = request.form.get("numero_interno", "").strip() or None
        estado = request.form.get("estado", "Activo")

        if not all([placa, marca, modelo, anio]):
            flash("Completa los campos obligatorios", "danger")
            return render_template("vehiculos/crear.html")

        if Vehiculo.query.filter_by(placa=placa).first():
            flash("Ya existe un vehículo con esa placa", "danger")
            return render_template("vehiculos/crear.html")

        vehiculo = Vehiculo(
            placa=placa,
            marca=marca,
            modelo=modelo,
            anio=anio,
            color=color,
            numero_interno=numero_interno,
            estado=estado,
        )
        db.session.add(vehiculo)
        db.session.commit()
        flash("Vehículo registrado", "success")
        return redirect(url_for("vehiculos.listar"))

    return render_template("vehiculos/crear.html")


@vehiculos.route("/<int:vehiculo_id>")
@login_required
def detalle(vehiculo_id):
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    documentos = vehiculo.documentos.order_by(Documento.fecha_vencimiento).all()
    historial = vehiculo.asignaciones.order_by(AsignacionConductor.fecha_desde.desc()).all()
    return render_template(
        "vehiculos/detalle.html",
        vehiculo=vehiculo,
        documentos=documentos,
        historial=historial,
    )


@vehiculos.route("/<int:vehiculo_id>/editar", methods=["GET", "POST"])
@login_required
def editar(vehiculo_id):
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)

    if request.method == "POST":
        placa = request.form.get("placa", "").strip().upper()
        otra = Vehiculo.query.filter(
            Vehiculo.placa == placa, Vehiculo.id != vehiculo.id
        ).first()
        if otra:
            flash("Ya existe un vehículo con esa placa", "danger")
            return render_template("vehiculos/editar.html", vehiculo=vehiculo)

        vehiculo.placa = placa
        vehiculo.marca = request.form.get("marca", "").strip()
        vehiculo.modelo = request.form.get("modelo", "").strip()
        vehiculo.anio = request.form.get("anio", type=int)
        vehiculo.color = request.form.get("color", "").strip() or None
        vehiculo.numero_interno = request.form.get("numero_interno", "").strip() or None
        vehiculo.estado = request.form.get("estado", "Activo")
        db.session.commit()
        flash("Vehículo actualizado", "success")
        return redirect(url_for("vehiculos.detalle", vehiculo_id=vehiculo.id))

    return render_template("vehiculos/editar.html", vehiculo=vehiculo)


@vehiculos.route("/<int:vehiculo_id>/eliminar", methods=["POST"])
@login_required
def eliminar(vehiculo_id):
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    db.session.delete(vehiculo)
    db.session.commit()
    flash("Vehículo eliminado", "info")
    return redirect(url_for("vehiculos.listar"))
