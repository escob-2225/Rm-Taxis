from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required

from extensions import bcrypt
from models.usuario import Usuario

auth = Blueprint("auth", __name__)

@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and bcrypt.check_password_hash(usuario.password, password):

            login_user(usuario)

            return redirect(url_for("auth.dashboard"))

        flash("Correo o contraseña incorrectos", "danger")

    return render_template("login.html")


from flask_login import login_required

@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")