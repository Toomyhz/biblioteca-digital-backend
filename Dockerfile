    # 1. Usar una imagen base oficial de Python
    FROM python:3.12-slim

    # Directorio de trabajo
    WORKDIR /app

    # 2. Instalar dependencias de sistema (añadimos wget y unzip)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        unzip \
        && rm -rf /var/lib/apt/lists/*

    # 3. --- INSTALAR ORACLE INSTANT CLIENT ---
    RUN wget https://download.oracle.com/otn_software/linux/instantclient/2112000/el9/instantclient-basic-linux.x64-21.12.0.0.0dbru.el9.zip -O oracle.zip && \
        unzip oracle.zip && \
        rm oracle.zip && \
        echo /app/instantclient_${ORACLE_CLIENT_VERSION} > /etc/ld.so.conf.d/oracle.conf && \
        ldconfig
    ENV TNS_ADMIN=/app/wallet
    # ------------------------------------

    # 4. COPIAR e instalar requirements
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # 5. Copiar resto del code
    COPY . .

    # 6. Exponer puerto
    EXPOSE 8000

    # 7. Comando de inicio (Correcto para tu run.py)
    CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]