from extensions import db


class Conductor(db.Model):
    __tablename__ = "conductores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    cedula = db.Column(db.String(30), unique=True, nullable=False)
    telefono = db.Column(db.String(30))
    direccion = db.Column(db.String(200))
    licencia = db.Column(db.String(50), nullable=False)
    licencia_vencimiento = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default="Activo")
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    asignaciones = db.relationship(
        "AsignacionConductor",
        back_populates="conductor",
        lazy="dynamic",
    )
