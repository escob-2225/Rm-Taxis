from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.conductor import Conductor
from models.vehiculo import Vehiculo
from models.asignacion import AsignacionConductor

conductores = Blueprint("conductores", __name__, url_prefix="/conductores")


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@conductores.route("/")
@login_required
def listar():
    lista = Conductor.query.order_by(Conductor.nombre).all()
    return render_template("conductores/listar.html", conductores=lista)


@conductores.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        cedula = request.form.get("cedula", "").strip()
        if Conductor.query.filter_by(cedula=cedula).first():
            flash("Ya existe un conductor con esa cédula", "danger")
            return render_template("conductores/form.html", conductor=None)

        conductor = Conductor(
            nombre=request.form.get("nombre", "").strip(),
            cedula=cedula,
            telefono=request.form.get("telefono", "").strip() or None,
            direccion=request.form.get("direccion", "").strip() or None,
            licencia=request.form.get("licencia", "").strip(),
            licencia_vencimiento=_parse_date(request.form["licencia_vencimiento"]),
            estado=request.form.get("estado", "Activo"),
        )
        db.session.add(conductor)
        db.session.commit()
        flash("Conductor registrado", "success")
        return redirect(url_for("conductores.listar"))

    return render_template("conductores/form.html", conductor=None)


@conductores.route("/<int:conductor_id>")
@login_required
def detalle(conductor_id):
    conductor = Conductor.query.get_or_404(conductor_id)
    historial = (
        AsignacionConductor.query.filter_by(conductor_id=conductor.id)
        .order_by(AsignacionConductor.fecha_desde.desc())
        .all()
    )
    return render_template(
        "conductores/detalle.html",
        conductor=conductor,
        historial=historial,
    )


@conductores.route("/<int:conductor_id>/editar", methods=["GET", "POST"])
@login_required
def editar(conductor_id):
    conductor = Conductor.query.get_or_404(conductor_id)

    if request.method == "POST":
        cedula = request.form.get("cedula", "").strip()
        otra = Conductor.query.filter(
            Conductor.cedula == cedula, Conductor.id != conductor.id
        ).first()
        if otra:
            flash("Ya existe un conductor con esa cédula", "danger")
            return render_template("conductores/form.html", conductor=conductor)

        conductor.nombre = request.form.get("nombre", "").strip()
        conductor.cedula = cedula
        conductor.telefono = request.form.get("telefono", "").strip() or None
        conductor.direccion = request.form.get("direccion", "").strip() or None
        conductor.licencia = request.form.get("licencia", "").strip()
        conductor.licencia_vencimiento = _parse_date(request.form["licencia_vencimiento"])
        conductor.estado = request.form.get("estado", "Activo")
        db.session.commit()
        flash("Conductor actualizado", "success")
        return redirect(url_for("conductores.detalle", conductor_id=conductor.id))

    return render_template("conductores/form.html", conductor=conductor)


@conductores.route("/asignar", methods=["GET", "POST"])
@login_required
def asignar():
    vehiculos = Vehiculo.query.filter_by(estado="Activo").order_by(Vehiculo.placa).all()
    lista_conductores = (
        Conductor.query.filter_by(estado="Activo").order_by(Conductor.nombre).all()
    )
    vehiculo_pre = request.args.get("vehiculo_id", type=int)

    if request.method == "POST":
        vehiculo_id = request.form.get("vehiculo_id", type=int)
        conductor_id = request.form.get("conductor_id", type=int)
        fecha_desde = _parse_date(request.form.get("fecha_desde") or date.today().isoformat())

        vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
        Conductor.query.get_or_404(conductor_id)

        # Cerrar asignación actual del vehículo
        actual = AsignacionConductor.query.filter_by(
            vehiculo_id=vehiculo.id, fecha_hasta=None
        ).first()
        if actual:
            if actual.conductor_id == conductor_id:
                flash("Ese conductor ya está asignado a este vehículo", "warning")
                return redirect(url_for("vehiculos.detalle", vehiculo_id=vehiculo.id))
            actual.fecha_hasta = fecha_desde

        nueva = AsignacionConductor(
            vehiculo_id=vehiculo.id,
            conductor_id=conductor_id,
            fecha_desde=fecha_desde,
            fecha_hasta=None,
        )
        db.session.add(nueva)
        db.session.commit()
        flash("Conductor asignado. El historial se conservó.", "success")
        return redirect(url_for("vehiculos.detalle", vehiculo_id=vehiculo.id))

    return render_template(
        "conductores/asignar.html",
        vehiculos=vehiculos,
        conductores=lista_conductores,
        vehiculo_pre=vehiculo_pre,
        hoy=date.today().isoformat(),
    )


@conductores.route("/historial")
@login_required
def historial():
    asignaciones = AsignacionConductor.query.order_by(
        AsignacionConductor.fecha_desde.desc()
    ).all()
    return render_template("conductores/historial.html", asignaciones=asignaciones)
