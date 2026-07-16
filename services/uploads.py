import os
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_document_file(file_storage):
    """Guarda un archivo de documento y retorna el nombre relativo almacenado."""
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        raise ValueError("Formato no permitido. Usa PDF, PNG, JPG o WEBP.")

    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)

    original = secure_filename(file_storage.filename)
    name, ext = os.path.splitext(original)
    filename = f"{name}_{uuid4().hex[:8]}{ext.lower()}"
    path = os.path.join(folder, filename)
    file_storage.save(path)
    return filename


def delete_document_file(filename: str | None):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        os.remove(path)
