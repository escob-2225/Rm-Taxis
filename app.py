from flask import Flask
from flask_mail import Mail
from sqlalchemy import text, inspect

from extensions import db, bcrypt, login_manager
from config import Config

mail = Mail()


def _asegurar_columna_activo():
    """Añade la columna activo si la tabla usuarios ya existía sin ella."""
    inspector = inspect(db.engine)
    if "usuarios" not in inspector.get_table_names():
        return
    columnas = {c["name"] for c in inspector.get_columns("usuarios")}
    if "activo" not in columnas:
        db.session.execute(
            text(
                "ALTER TABLE usuarios ADD COLUMN activo TINYINT(1) NOT NULL DEFAULT 1"
            )
        )
        db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from routes.auth import auth
    from routes.vehiculos import vehiculos
    from routes.documentos import documentos
    from routes.conductores import conductores
    from routes.alertas import alertas
    from routes.notificaciones import notificaciones
    from routes.usuarios import usuarios

    app.register_blueprint(auth)
    app.register_blueprint(vehiculos)
    app.register_blueprint(documentos)
    app.register_blueprint(conductores)
    app.register_blueprint(alertas)
    app.register_blueprint(notificaciones)
    app.register_blueprint(usuarios)

    from models import (  # noqa: F401
        Usuario,
        Vehiculo,
        Documento,
        Conductor,
        AsignacionConductor,
        ConfiguracionAlerta,
        AlertaEnviada,
        Notificacion,
    )

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None or user_id == "":
            return None
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return None
        if uid <= 0:
            return None
        user = db.session.get(Usuario, uid)
        if user is None or not user.activo:
            return None
        return user

    with app.app_context():
        import os

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        db.create_all()
        _asegurar_columna_activo()
        from services.alertas import asegurar_configuracion_alertas

        asegurar_configuracion_alertas()

    return app


app = create_app()


if __name__ == "__main__":
    import os

    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="127.0.0.1", port=5000, debug=debug)
