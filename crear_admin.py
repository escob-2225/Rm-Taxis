from app import create_app
from extensions import db, bcrypt
from models.usuario import Usuario

app = create_app()

with app.app_context():
    correo = "admin@taxi.com"
    password_plano = "Admin123"

    admin = Usuario.query.filter_by(correo=correo).first()
    password = bcrypt.generate_password_hash(password_plano).decode("utf-8")

    if admin:
        admin.password = password
        admin.nombre = "Administrador"
        admin.rol = "Administrador"
        db.session.commit()
        print(f"Administrador actualizado (id={admin.id}).")
    else:
        admin = Usuario(
            nombre="Administrador",
            correo=correo,
            password=password,
            rol="Administrador",
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Administrador creado (id={admin.id}).")

    print(f"Correo: {correo}")
    print(f"Contraseña: {password_plano}")
