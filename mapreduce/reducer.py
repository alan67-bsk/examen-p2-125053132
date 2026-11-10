#!/usr/bin/env python3
# reducer.py
# Pregunta: ticket promedio (ingreso promedio por registro) por tienda
#
# Entrada (Hadoop ya la entrega ordenada por tienda):
#   tienda <TAB> ingreso
# Salida:
#   tienda <TAB> ticket_promedio <TAB> num_ventas
import sys

tienda_actual = None
suma = 0.0
ventas = 0


def emitir(tienda, suma, ventas):
    promedio = suma / ventas
    print(f"{tienda}\t{promedio:.2f}\t{ventas}")


for linea in sys.stdin:
    partes = linea.strip().split("\t")
    if len(partes) != 2:
        continue

    tienda = partes[0]
    try:
        ingreso = float(partes[1])
    except ValueError:
        continue

    # Como viene ordenado, cuando cambia la tienda ya termine con la anterior
    if tienda != tienda_actual:
        if tienda_actual is not None:
            emitir(tienda_actual, suma, ventas)
        tienda_actual = tienda
        suma = 0.0
        ventas = 0

    suma += ingreso
    ventas += 1

# la ultima tienda se queda pendiente al salir del ciclo
if tienda_actual is not None:
    emitir(tienda_actual, suma, ventas)
