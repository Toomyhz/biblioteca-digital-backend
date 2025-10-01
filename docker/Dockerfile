# IMAGEN A UTILIZAR
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# COPIAR e instalar requirements primero (mejora la cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar resto del code
COPY . .

# Exponer puerto (Lo que escuchara Gunicorn)
EXPOSE 8000

# Comando de inicio (modo producción con Gunicorn)
CMD ["gunicorn","-w","4","-b","0.0.0.0:8000","app:app"]

