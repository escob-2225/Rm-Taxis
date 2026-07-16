from datetime import date

from flask import current_app

from extensions import db

TIPOS_DOCUMENTO = [
    "SOAT",
    "Revisión Técnico-Mecánica",
    "Tarjeta de Operación",
    "Licencia de Tránsito",
    "Seguro contractual",
    "Seguro extracontractual",
    "Otro",
]


class Documento(db.Model):
    __tablename__ = "documentos"

    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"), nullable=False)
    tipo = db.Column(db.String(80), nullable=False)
    fecha_expedicion = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    archivo = db.Column(db.String(255))
    observaciones = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    vehiculo = db.relationship("Vehiculo", back_populates="documentos")

    @property
    def dias_restantes(self):
        return (self.fecha_vencimiento - date.today()).days

    @property
    def estado(self):
        dias = self.dias_restantes
        umbral = current_app.config.get("DIAS_PROXIMO_VENCER", 30)

        if dias < 0:
            return "Vencido"
        if dias <= umbral:
            return "Próximo a vencer"
        return "Vigente"

    @property
    def estado_badge(self):
        return {
            "Vigente": "success",
            "Próximo a vencer": "warning",
            "Vencido": "danger",
        }.get(self.estado, "secondary")
