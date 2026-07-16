from extensions import db


class AsignacionConductor(db.Model):
    __tablename__ = "asignaciones_conductor"

    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey("vehiculos.id"), nullable=False)
    conductor_id = db.Column(db.Integer, db.ForeignKey("conductores.id"), nullable=False)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date)  # None = asignación actual
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    vehiculo = db.relationship("Vehiculo", back_populates="asignaciones")
    conductor = db.relationship("Conductor", back_populates="asignaciones")

    @property
    def activa(self):
        return self.fecha_hasta is None
