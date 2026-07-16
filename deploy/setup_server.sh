#!/usr/bin/env bash
# Instalación de Rm Taxis en Ubuntu (Oracle Cloud Always Free - ARM o x86)
# Uso (como usuario ubuntu):
#   curl -fsSL ... | bash
#   o: bash setup_server.sh

set -euo pipefail

APP_DIR="/var/www/rmtaxis"
REPO_URL="${REPO_URL:-https://github.com/escob-2225/Rm-Taxis.git}"
DOMAIN_OR_IP="${DOMAIN_OR_IP:-}"

echo "==> Actualizando sistema..."
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

echo "==> Instalando paquetes..."
sudo apt-get install -y \
  python3 python3-venv python3-pip \
  nginx git ufw \
  mysql-server \
  build-essential pkg-config

echo "==> Configurando MySQL..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS taxi_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'rmtaxis'@'localhost' IDENTIFIED BY 'CambiaEstaPassword123!';"
sudo mysql -e "GRANT ALL PRIVILEGES ON taxi_manager.* TO 'rmtaxis'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "==> Clonando / actualizando proyecto..."
sudo mkdir -p /var/www
if [ ! -d "$APP_DIR/.git" ]; then
  sudo git clone "$REPO_URL" "$APP_DIR"
else
  sudo git -C "$APP_DIR" pull
fi
sudo chown -R ubuntu:ubuntu "$APP_DIR"

cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f .env ]; then
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  cat > .env <<EOF
SECRET_KEY=${SECRET}
DATABASE_URL=mysql+pymysql://rmtaxis:CambiaEstaPassword123!@localhost/taxi_manager
EOF
  echo "==> Archivo .env creado. Cambia la contraseña de MySQL cuando puedas."
fi

mkdir -p uploads/documentos
python crear_admin.py || true

echo "==> Configurando Gunicorn (systemd)..."
sudo cp deploy/rmtaxis.service /etc/systemd/system/rmtaxis.service
# Ajustar usuario ubuntu en vez de www-data en Always Free sencillo
sudo sed -i 's/User=www-data/User=ubuntu/' /etc/systemd/system/rmtaxis.service
sudo sed -i 's/Group=www-data/Group=ubuntu/' /etc/systemd/system/rmtaxis.service
sudo systemctl daemon-reload
sudo systemctl enable rmtaxis
sudo systemctl restart rmtaxis

echo "==> Configurando Nginx..."
SERVER_NAME="${DOMAIN_OR_IP:-_}"
sudo tee /etc/nginx/sites-available/rmtaxis >/dev/null <<EOF
server {
    listen 80;
    server_name ${SERVER_NAME};

    client_max_body_size 12M;

    location /static/ {
        alias ${APP_DIR}/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/rmtaxis /etc/nginx/sites-enabled/rmtaxis
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "==> Abriendo firewall del sistema (UFW)..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo ""
echo "============================================"
echo " Instalación base completada"
echo "============================================"
echo "1) En Oracle Cloud abre el puerto 80 (Security List / NSG)."
echo "2) Entra a: http://TU_IP_PUBLICA"
echo "3) Login: admin@taxi.com / Admin123"
echo "4) Cambia esa contraseña en Mi cuenta."
echo "5) Cambia también la password de MySQL en .env"
echo "============================================"
