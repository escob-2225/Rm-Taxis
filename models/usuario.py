from extensions import db
from flask_login import UserMixin


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default="Empleado")
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        """Flask-Login: usuarios inactivos no pueden iniciar sesión."""
        return bool(self.activo)

    @property
    def is_admin(self):
        return (self.rol or "").strip().lower() == "administrador"
