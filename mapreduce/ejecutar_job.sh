#!/bin/bash
# Parte C1: corre el job de MapReduce con Hadoop Streaming y mide el tiempo.
#
# Uso (desde la carpeta del proyecto, en la terminal de la Mac):
#   docker compose exec -u hadoop hadoop bash /app/mapreduce/ejecutar_job.sh

ENTRADA=/data/input/ventas_125053132.csv
SALIDA=/data/output/resultado

if [ "$(whoami)" != "hadoop" ]; then
    echo "Este script se corre como el usuario hadoop:"
    echo "  docker compose exec -u hadoop hadoop bash /app/mapreduce/ejecutar_job.sh"
    exit 1
fi

if [ ! -f "$ENTRADA" ]; then
    echo "No encuentro $ENTRADA"
    echo "Revisa que el CSV este en la carpeta data/ del proyecto."
    exit 1
fi

# Hadoop no sobreescribe una carpeta de salida que ya existe, hay que borrarla antes
rm -rf "$SALIDA"

# La carpeta del repo esta montada en solo lectura, asi que trabajo sobre una copia
rm -rf /tmp/job
mkdir /tmp/job
cp /app/mapreduce/mapper.py /app/mapreduce/reducer.py /tmp/job/
chmod +x /tmp/job/mapper.py /tmp/job/reducer.py
cd /tmp/job

time hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -input "$ENTRADA" \
    -output "$SALIDA" \
    -mapper mapper.py -reducer reducer.py \
    -file mapper.py -file reducer.py

echo
echo "Archivos de salida:"
ls -l "$SALIDA"
echo
echo "Resultado (tienda, ticket promedio, numero de ventas):"
cat "$SALIDA/part-00000"
