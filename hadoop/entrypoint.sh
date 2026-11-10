#!/bin/bash
# Se ejecuta cada vez que arranca el contenedor hadoop, antes del servidor SSH
set -e

# El volumen de salida lo tiene que poder escribir el usuario hadoop
chown hadoop:hadoop /data/output

# Llaves del usuario hadoop para entrar sin contraseña (ssh localhost).
# Se generan al arrancar y no en el Dockerfile para que la llave privada
# no se quede guardada dentro de la imagen.
if [ ! -f /home/hadoop/.ssh/id_rsa ]; then
    su hadoop -c "ssh-keygen -t rsa -P '' -f /home/hadoop/.ssh/id_rsa -q"
    su hadoop -c "cat /home/hadoop/.ssh/id_rsa.pub >> /home/hadoop/.ssh/authorized_keys"
    su hadoop -c "chmod 600 /home/hadoop/.ssh/authorized_keys"
fi

# Sigue con el CMD del Dockerfile (sshd)
exec "$@"
