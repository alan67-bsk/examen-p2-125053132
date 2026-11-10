FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cliente SSH para poder entrar al contenedor hadoop desde aqui.
# La ultima linea hace que acepte la huella del servidor la primera vez sin preguntar.
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client && \
    rm -rf /var/lib/apt/lists/* && \
    echo "StrictHostKeyChecking accept-new" > /etc/ssh/ssh_config.d/examen.conf

# Primero las dependencias para aprovechar la cache de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Despues el codigo de la aplicacion
COPY . /app
RUN chmod +x /app/entrypoint.sh

# Puerto donde escucha Flask dentro del contenedor
EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "app.py"]
