FROM debian:bookworm-slim

ARG HADOOP_VERSION=3.3.6

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


RUN ln -s /usr/lib/jvm/java-17-openjdk-$(dpkg --print-architecture) /usr/lib/jvm/java-17

ENV JAVA_HOME=/usr/lib/jvm/java-17
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin


RUN useradd -m -s /bin/bash hadoop && \
    mkdir -p /home/hadoop/.ssh /data/input /data/output /run/sshd && \
    chmod 700 /home/hadoop/.ssh && \
    chown -R hadoop:hadoop /home/hadoop/.ssh /data/output


RUN (wget --progress=dot:giga -O /tmp/hadoop.tar.gz \
        https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz || \
     wget --progress=dot:giga -O /tmp/hadoop.tar.gz \
        https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz) && \
    tar -xzf /tmp/hadoop.tar.gz -C /opt && \
    rm /tmp/hadoop.tar.gz && \
    ln -s /opt/hadoop-${HADOOP_VERSION} /opt/hadoop && \
    rm -rf /opt/hadoop/share/doc && \
    chown -R hadoop:hadoop /opt/hadoop-${HADOOP_VERSION}

RUN echo "export JAVA_HOME=$JAVA_HOME" > /etc/profile.d/hadoop.sh && \
    echo "export HADOOP_HOME=$HADOOP_HOME" >> /etc/profile.d/hadoop.sh && \
    echo "export HADOOP_CONF_DIR=$HADOOP_CONF_DIR" >> /etc/profile.d/hadoop.sh && \
    echo "export PATH=\$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin" >> /etc/profile.d/hadoop.sh


RUN echo "PasswordAuthentication no" > /etc/ssh/sshd_config.d/examen.conf && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config.d/examen.conf && \
    echo "AuthorizedKeysFile .ssh/authorized_keys /llaves/api.pub" >> /etc/ssh/sshd_config.d/examen.conf && \
    echo "StrictHostKeyChecking accept-new" > /etc/ssh/ssh_config.d/examen.conf


RUN hadoop version

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22


ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D", "-e"]
