# Hadoop 3.3.6 en modo standalone sobre Debian 12 (lo mismo que hicimos en clase,
# pero ya automatizado en una imagen)
FROM debian:bookworm-slim

ARG HADOOP_VERSION=3.3.6

# Java (Hadoop esta hecho en Java), Python 3 para el mapper y el reducer,
# servidor y cliente SSH, y wget para descargar Hadoop.
# El mkdir es porque la imagen slim no trae la carpeta de manuales y el
# instalador de Java la ocupa para crear sus enlaces.
RUN mkdir -p /usr/share/man/man1 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jdk-headless \
        python3 \
        openssh-server \
        openssh-client \
        wget \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# La carpeta de Java cambia segun el procesador: termina en arm64 en mi Mac M1
# y en amd64 en una Intel. Con este enlace JAVA_HOME es igual en cualquier maquina.
RUN ln -s /usr/lib/jvm/java-17-openjdk-$(dpkg --print-architecture) /usr/lib/jvm/java-17

ENV JAVA_HOME=/usr/lib/jvm/java-17
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Usuario hadoop. No se le pone contraseña: solo se puede entrar con llave SSH
RUN useradd -m -s /bin/bash hadoop && \
    mkdir -p /home/hadoop/.ssh /data/input /data/output /run/sshd && \
    chmod 700 /home/hadoop/.ssh && \
    chown -R hadoop:hadoop /home/hadoop/.ssh /data/output

# Descarga de Hadoop en /opt. Primero intenta el servidor que usamos en clase y si
# no responde usa el archivo historico de Apache. Al final se borra el .tar.gz y la
# documentacion para que la imagen pese menos.
RUN (wget --progress=dot:giga -O /tmp/hadoop.tar.gz \
        https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz || \
     wget --progress=dot:giga -O /tmp/hadoop.tar.gz \
        https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz) && \
    tar -xzf /tmp/hadoop.tar.gz -C /opt && \
    rm /tmp/hadoop.tar.gz && \
    ln -s /opt/hadoop-${HADOOP_VERSION} /opt/hadoop && \
    rm -rf /opt/hadoop/share/doc && \
    chown -R hadoop:hadoop /opt/hadoop-${HADOOP_VERSION}

# Las variables ENV no llegan a las sesiones que entran por SSH, por eso tambien
# se guardan en /etc/profile.d (se carga cada vez que alguien inicia sesion)
RUN echo "export JAVA_HOME=$JAVA_HOME" > /etc/profile.d/hadoop.sh && \
    echo "export HADOOP_HOME=$HADOOP_HOME" >> /etc/profile.d/hadoop.sh && \
    echo "export HADOOP_CONF_DIR=$HADOOP_CONF_DIR" >> /etc/profile.d/hadoop.sh && \
    echo "export PATH=\$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin" >> /etc/profile.d/hadoop.sh

# Configuracion de SSH:
#  - servidor: nada de contraseñas ni root, solo llaves. Ademas de authorized_keys
#    acepta la llave publica que el contenedor api deja en el volumen /llaves
#  - cliente: acepta la huella del servidor la primera vez sin preguntar
RUN echo "PasswordAuthentication no" > /etc/ssh/sshd_config.d/examen.conf && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config.d/examen.conf && \
    echo "AuthorizedKeysFile .ssh/authorized_keys /llaves/api.pub" >> /etc/ssh/sshd_config.d/examen.conf && \
    echo "StrictHostKeyChecking accept-new" > /etc/ssh/ssh_config.d/examen.conf

# Si Hadoop quedo mal instalado el build truena aqui y no hasta usarlo
RUN hadoop version

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

# ENTRYPOINT prepara las llaves y CMD es lo que se queda corriendo (el servidor SSH)
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D", "-e"]
