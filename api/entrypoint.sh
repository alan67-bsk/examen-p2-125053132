#!/bin/sh
# Se ejecuta cada vez que arranca el contenedor api, antes de Flask
set -e

# La api genera su propio par de llaves la primera vez que arranca.
# La llave privada nunca sale de este contenedor; solo la publica se copia al
# volumen compartido /llaves, que es donde la lee el sshd del contenedor hadoop.
if [ ! -f /root/.ssh/id_rsa ]; then
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh
    ssh-keygen -t rsa -P '' -f /root/.ssh/id_rsa -q
fi
cp /root/.ssh/id_rsa.pub /llaves/api.pub
chmod 644 /llaves/api.pub

# Sigue con el CMD del Dockerfile (python app.py)
exec "$@"
