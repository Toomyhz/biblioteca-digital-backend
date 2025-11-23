FROM python:3.12-slim

WORKDIR /app

# Versión del instant client
ARG ORACLE_CLIENT_VERSION=21_12
ENV ORACLE_CLIENT_VERSION=${ORACLE_CLIENT_VERSION}

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        unzip \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Instalar Oracle Instant Client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/2112000/el9/instantclient-basic-linux.x64-21.12.0.0.0dbru.el9.zip -O oracle.zip \
    && unzip oracle.zip \
    && rm oracle.zip \
    && echo /app/instantclient_${ORACLE_CLIENT_VERSION} > /etc/ld.so.conf.d/oracle.conf \
    && ldconfig

ENV TNS_ADMIN=/app/wallet \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
