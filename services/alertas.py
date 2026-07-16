from datetime import date

from flask import current_app

from extensions import db
from models.alerta import AlertaEnviada, ConfiguracionAlerta
from models.documento import Documento
from models.notificacion import Notificacion
from models.usuario import Usuario


DEFAULT_ALERTAS = (30, 15, 7, 1)


def asegurar_configuracion_alertas():
    existentes = {c.dias_antes for c in ConfiguracionAlerta.query.all()}
    for dias in DEFAULT_ALERTAS:
        if dias not in existentes:
            db.session.add(
                ConfiguracionAlerta(
                    dias_antes=dias,
                    canal_sistema=True,
                    canal_correo=False,
                    canal_whatsapp=False,
                    canal_sms=False,
                    activo=True,
                )
            )
    db.session.commit()


def _enviar_correo(destinatarios, asunto, cuerpo):
    server = current_app.config.get("MAIL_SERVER")
    if not server or not destinatarios:
        return False, "Correo no configurado"

    try:
        from flask_mail import Message

        mail = current_app.extensions.get("mail")
        if mail is None:
            return False, "Flask-Mail no inicializado"

        msg = Message(
            subject=asunto,
            recipients=destinatarios,
            body=cuerpo,
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
        )
        mail.send(msg)
        return True, "Enviado"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _registrar_envio(documento_id, dias_antes, canal, detalle):
    db.session.add(
        AlertaEnviada(
            documento_id=documento_id,
            dias_antes=dias_antes,
            canal=canal,
            fecha_envio=date.today(),
            detalle=(detalle or "")[:255],
        )
    )


def _ya_enviada(documento_id, dias_antes, canal):
    return (
        AlertaEnviada.query.filter_by(
            documento_id=documento_id,
            dias_antes=dias_antes,
            canal=canal,
        ).first()
        is not None
    )


def procesar_alertas():
    """Genera una alerta por umbral (30/15/7/1) cuando el documento entra en esa ventana."""
    asegurar_configuracion_alertas()
    configs = ConfiguracionAlerta.query.filter_by(activo=True).all()
    if not configs:
        return 0

    documentos = Documento.query.all()
    creadas = 0
    correos_admin = [
        u.correo for u in Usuario.query.filter_by(rol="Administrador").all() if u.correo
    ]

    for doc in documentos:
        dias = doc.dias_restantes
        if dias < 0:
            # Aviso único de vencido vía sistema
            if not _ya_enviada(doc.id, 0, "sistema"):
                placa = doc.vehiculo.placa if doc.vehiculo else "?"
                db.session.add(
                    Notificacion(
                        titulo=f"Documento vencido: {doc.tipo}",
                        mensaje=(
                            f"El vehículo {placa} tiene el {doc.tipo} vencido "
                            f"desde {doc.fecha_vencimiento.strftime('%d/%m/%Y')}."
                        ),
                        vehiculo_id=doc.vehiculo_id,
                        documento_id=doc.id,
                    )
                )
                _registrar_envio(doc.id, 0, "sistema", "vencido")
                creadas += 1
            continue

        for cfg in configs:
            if dias > cfg.dias_antes:
                continue

            placa = doc.vehiculo.placa if doc.vehiculo else "?"
            titulo = f"Documento próximo a vencer: {doc.tipo}"
            mensaje = (
                f"El vehículo {placa} tiene el {doc.tipo} próximo a vencer "
                f"en {dias} día(s) ({doc.fecha_vencimiento.strftime('%d/%m/%Y')})."
            )

            if cfg.canal_sistema and not _ya_enviada(doc.id, cfg.dias_antes, "sistema"):
                db.session.add(
                    Notificacion(
                        titulo=titulo,
                        mensaje=mensaje,
                        vehiculo_id=doc.vehiculo_id,
                        documento_id=doc.id,
                    )
                )
                _registrar_envio(doc.id, cfg.dias_antes, "sistema", "ok")
                creadas += 1

            if cfg.canal_correo and not _ya_enviada(doc.id, cfg.dias_antes, "correo"):
                ok, detalle = _enviar_correo(correos_admin, titulo, mensaje)
                _registrar_envio(doc.id, cfg.dias_antes, "correo", detalle)
                if ok:
                    creadas += 1

            if cfg.canal_whatsapp and not _ya_enviada(doc.id, cfg.dias_antes, "whatsapp"):
                _registrar_envio(
                    doc.id,
                    cfg.dias_antes,
                    "whatsapp",
                    "Pendiente de integración WhatsApp",
                )

            if cfg.canal_sms and not _ya_enviada(doc.id, cfg.dias_antes, "sms"):
                _registrar_envio(
                    doc.id,
                    cfg.dias_antes,
                    "sms",
                    "Pendiente de integración SMS",
                )

    db.session.commit()
    return creadas
