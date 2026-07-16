from extensions import db


class Vehiculo(db.Model):
    __tablename__ = "vehiculos"

    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30))
    numero_interno = db.Column(db.String(20), unique=True)
    estado = db.Column(db.String(20), default="Activo")

    documentos = db.relationship(
        "Documento",
        back_populates="vehiculo",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    asignaciones = db.relationship(
        "AsignacionConductor",
        back_populates="vehiculo",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    @property
    def conductor_actual(self):
        asignacion = self.asignaciones.filter_by(fecha_hasta=None).first()
        return asignacion.conductor if asignacion else None
