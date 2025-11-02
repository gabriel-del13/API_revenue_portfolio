FROM python:3.11-slim

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python almacene en búfer stdout y stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación
COPY . .

# Crea el directorio para archivos estáticos
RUN mkdir -p /app/staticfiles

# Expone el puerto
EXPOSE 8000

# Script de inicio: collectstatic, migraciones y luego gunicorn + creación de superusuario
CMD python manage.py collectstatic --no-input && \
    python manage.py migrate && \
    python create_superuser.py && \
    gunicorn API_revenue_portfolio.wsgi:application --bind 0.0.0.0:8000 --workers 2