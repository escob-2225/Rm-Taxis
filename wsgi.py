"""Punto de entrada para Gunicorn / producción."""

from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app
from config import ProductionConfig

app = create_app(ProductionConfig)

# Necesario detrás de Nginx / HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
