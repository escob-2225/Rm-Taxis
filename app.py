from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from extensions import db, bcrypt, login_manager

def create_app():

    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from routes.auth import auth
    from routes.vehiculos import vehiculos

    app.register_blueprint(auth)
    app.register_blueprint(vehiculos)

    return app


app = create_app()


from models.usuario import Usuario
from models.vehiculo import Vehiculo


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)