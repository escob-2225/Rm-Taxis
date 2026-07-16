from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    current_app,
)
from flask_login import login_required

from extensions import db
from models.documento import Documento, TIPOS_DOCUMENTO
from models.vehiculo import Vehiculo
from services.uploads import save_document_file, delete_document_file

documentos = Blueprint("documentos", __name__, url_prefix="/documentos")


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


@documentos.route("/")
@login_required
def listar():
    estado_filtro = request.args.get("estado")
    docs = Documento.query.order_by(Documento.fecha_vencimiento).all()
    if estado_filtro:
        docs = [d for d in docs if d.estado == estado_filtro]
    return render_template(
        "documentos/listar.html",
        documentos=docs,
        estado_filtro=estado_filtro,
    )


@documentos.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    vehiculos = Vehiculo.query.order_by(Vehiculo.placa).all()
    vehiculo_pre = request.args.get("vehiculo_id", type=int)

    if request.method == "POST":
        try:
            vehiculo_id = request.form.get("vehiculo_id", type=int)
            tipo = request.form.get("tipo", "").strip()
            fecha_expedicion = _parse_date(request.form["fecha_expedicion"])
            fecha_vencimiento = _parse_date(request.form["fecha_vencimiento"])
            observaciones = request.form.get("observaciones", "").strip() or None
            archivo = None

            if "archivo" in request.files:
                archivo = save_document_file(request.files["archivo"])

            if fecha_vencimiento < fecha_expedicion:
                flash("La fecha de vencimiento no puede ser anterior a la expedición", "danger")
                return render_template(
                    "documentos/form.html",
                    documento=None,
                    vehiculos=vehiculos,
                    tipos=TIPOS_DOCUMENTO,
                    vehiculo_pre=vehiculo_id,
                )

            doc = Documento(
                vehiculo_id=vehiculo_id,
                tipo=tipo,
                fecha_expedicion=fecha_expedicion,
                fecha_vencimiento=fecha_vencimiento,
                archivo=archivo,
                observaciones=observaciones,
            )
            db.session.add(doc)
            db.session.commit()
            flash("Documento registrado", "success")
            return redirect(url_for("vehiculos.detalle", vehiculo_id=vehiculo_id))
        except ValueError as exc:
            flash(str(exc), "danger")
        except Exception:  # noqa: BLE001
            flash("Error al guardar el documento. Revisa los datos.", "danger")

    return render_template(
        "documentos/form.html",
        documento=None,
        vehiculos=vehiculos,
        tipos=TIPOS_DOCUMENTO,
        vehiculo_pre=vehiculo_pre,
    )


@documentos.route("/<int:documento_id>/editar", methods=["GET", "POST"])
@login_required
def editar(documento_id):
    documento = Documento.query.get_or_404(documento_id)
    vehiculos = Vehiculo.query.order_by(Vehiculo.placa).all()

    if request.method == "POST":
        try:
            documento.vehiculo_id = request.form.get("vehiculo_id", type=int)
            documento.tipo = request.form.get("tipo", "").strip()
            documento.fecha_expedicion = _parse_date(request.form["fecha_expedicion"])
            documento.fecha_vencimiento = _parse_date(request.form["fecha_vencimiento"])
            documento.observaciones = request.form.get("observaciones", "").strip() or None

            if "archivo" in request.files and request.files["archivo"].filename:
                nuevo = save_document_file(request.files["archivo"])
                delete_document_file(documento.archivo)
                documento.archivo = nuevo

            db.session.commit()
            flash("Documento actualizado", "success")
            return redirect(
                url_for("vehiculos.detalle", vehiculo_id=documento.vehiculo_id)
            )
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "documentos/form.html",
        documento=documento,
        vehiculos=vehiculos,
        tipos=TIPOS_DOCUMENTO,
        vehiculo_pre=documento.vehiculo_id,
    )


@documentos.route("/<int:documento_id>/eliminar", methods=["POST"])
@login_required
def eliminar(documento_id):
    documento = Documento.query.get_or_404(documento_id)
    vehiculo_id = documento.vehiculo_id
    delete_document_file(documento.archivo)
    db.session.delete(documento)
    db.session.commit()
    flash("Documento eliminado", "info")
    return redirect(url_for("vehiculos.detalle", vehiculo_id=vehiculo_id))


@documentos.route("/archivo/<path:filename>")
@login_required
def archivo(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
