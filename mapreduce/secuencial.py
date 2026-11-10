#!/usr/bin/env python3
# secuencial.py
# La misma pregunta (ticket promedio por tienda) pero sin Hadoop:
# se lee el CSV linea por linea y se va acumulando en diccionarios.
#
# Uso: python3 secuencial.py /data/input/ventas_125053132.csv
# Salida (mismo formato que el reducer):
#   tienda <TAB> ticket_promedio <TAB> num_ventas
import sys

ruta = sys.argv[1] if len(sys.argv) > 1 else "/data/input/ventas_125053132.csv"

suma = {}
ventas = {}

with open(ruta) as archivo:
    for linea in archivo:
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
            continue

        # se redondea igual que el mapper para sumar exactamente los mismos valores
        ingreso = round(cantidad * precio, 2)
        suma[tienda] = suma.get(tienda, 0.0) + ingreso
        ventas[tienda] = ventas.get(tienda, 0) + 1

for tienda in sorted(suma):
    promedio = suma[tienda] / ventas[tienda]
    print(f"{tienda}\t{promedio:.2f}\t{ventas[tienda]}")
