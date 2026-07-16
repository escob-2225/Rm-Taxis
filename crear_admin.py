from app import create_app, db, bcrypt
from models.usuario import Usuario

app = create_app()

with app.app_context():

    password = bcrypt.generate_password_hash("Admin123").decode("utf-8")

    admin = Usuario(
        nombre="Administrador",
        correo="admin@taxi.com",
        password=password,
        rol="Administrador"
    )

    db.session.add(admin)
    db.session.commit()

    print("Administrador creado correctamente.")