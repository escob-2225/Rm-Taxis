from extensions import db


class Notificacion(db.Model):
    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    mensaje = db.Column(db.String(500), nullable=False)
    leida = db.Column(db.Boolean, default=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"))
    documento_id = db.Column(db.Integer, db.ForeignKey("documentos.id"))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    vehiculo = db.relationship("Vehiculo")
    documento = db.relationship("Documento")
