#!/usr/bin/env python3
# mapper.py
# Pregunta: ticket promedio (ingreso promedio por registro) por tienda
#
# Entrada: lineas del CSV
#   id,fecha_hora,tienda,categoria,producto,cantidad,precio_unitario,metodo_pago
# Salida:
#   tienda <TAB> ingreso        (ingreso = cantidad * precio_unitario)
import sys

for linea in sys.stdin:
    campos = linea.strip().split(",")

    
    if campos[0] == "id":
        continue

   
    try:
        if len(campos) != 8:
            raise ValueError("no tiene 8 columnas")
        tienda = campos[2]
        cantidad = int(campos[5])
        precio = float(campos[6])
        if tienda == "":
            raise ValueError("sin tienda")
    except ValueError:
        # contador de Hadoop Streaming, sale al final del log del job
        sys.stderr.write("reporter:counter:Examen,LineasInvalidas,1\n")
        continue

    ingreso = cantidad * precio
    print(f"{tienda}\t{ingreso:.2f}")
