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
    ENV ORACLE_CLIENT_VERSION=21_14
    RUN wget https://download.oracle.com/otn_software/linux/instantclient/${ORACLE_CLIENT_VERSION}/instantclient-basiclite-linux.x64-${ORACLE_CLIENT_VERSION}.0.0.0dbru.zip -O oracle.zip && \
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