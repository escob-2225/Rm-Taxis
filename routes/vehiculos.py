from flask import Blueprint, render_template

vehiculos = Blueprint(
    "vehiculos",
    __name__,
    url_prefix="/vehiculos"
)

@vehiculos.route("/")
def listar():

    return render_template("vehiculos/listar.html")