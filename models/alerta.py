from extensions import db


class ConfiguracionAlerta(db.Model):
    __tablename__ = "configuracion_alertas"

    id = db.Column(db.Integer, primary_key=True)
    dias_antes = db.Column(db.Integer, nullable=False, unique=True)
    canal_correo = db.Column(db.Boolean, default=False)
    canal_whatsapp = db.Column(db.Boolean, default=False)
    canal_sms = db.Column(db.Boolean, default=False)
    canal_sistema = db.Column(db.Boolean, default=True)
    activo = db.Column(db.Boolean, default=True)


class AlertaEnviada(db.Model):
    """Evita duplicar la misma alerta (documento + umbral + canal + día)."""

    __tablename__ = "alertas_enviadas"
    __table_args__ = (
        db.UniqueConstraint(
            "documento_id",
            "dias_antes",
            "canal",
            "fecha_envio",
            name="uq_alerta_unica",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey("documentos.id"), nullable=False)
    dias_antes = db.Column(db.Integer, nullable=False)
    canal = db.Column(db.String(20), nullable=False)
    fecha_envio = db.Column(db.Date, nullable=False)
    detalle = db.Column(db.String(255))

    documento = db.relationship("Documento")
