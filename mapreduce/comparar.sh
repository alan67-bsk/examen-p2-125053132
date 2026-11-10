#!/bin/bash
# Parte C2: corre el script secuencial, mide el tiempo y compara su resultado
# contra el del job de MapReduce.
#
# Uso (desde la carpeta del proyecto, en la terminal de la Mac):
#   docker compose exec -u hadoop hadoop bash /app/mapreduce/comparar.sh

ENTRADA=/data/input/ventas_125053132.csv
RESULTADO_MR=/data/output/resultado/part-00000
RESULTADO_SEC=/data/output/secuencial.txt

if [ ! -f "$RESULTADO_MR" ]; then
    echo "Todavia no existe $RESULTADO_MR, primero corre ejecutar_job.sh"
    exit 1
fi

echo "Corriendo el script secuencial..."
time python3 /app/mapreduce/secuencial.py "$ENTRADA" > "$RESULTADO_SEC"

echo
if diff "$RESULTADO_MR" "$RESULTADO_SEC" > /dev/null; then
    echo "OK: MapReduce y el secuencial dan el MISMO resultado ($(wc -l < "$RESULTADO_MR") tiendas)"
else
    echo "OJO: los resultados NO coinciden, estas son las diferencias:"
    diff "$RESULTADO_MR" "$RESULTADO_SEC"
fi
