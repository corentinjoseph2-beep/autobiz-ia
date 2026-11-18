# Dockerfile pour hébergement cloud 24/7 du Webhook Stripe AutoBiz IA
# Compatible Render, Railway, Fly.io, Koyeb
FROM python:3.11-slim

# Empêche la mise en cache pyc et buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements
COPY modules/04_distribution_ventes/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copie de l'ensemble du projet
COPY . /app

# Exposition du port
EXPOSE 5000

# Commande de démarrage avec serveur WSGI Gunicorn haute performance
CMD ["gunicorn", "--chdir", "modules/04_distribution_ventes", "webhook_listener:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60"]
