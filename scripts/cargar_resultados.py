#!/usr/bin/env python3
# cargar_resultados.py
# Parte D: lee la salida del job de MapReduce (part-00000) y mete los registros
# en la tabla "resultados" de PostgreSQL.
#
# Se corre dentro del contenedor api, que ya tiene psycopg2, las variables de la
# base de datos y el volumen con la salida de Hadoop:
#   docker compose exec api python scripts/cargar_resultados.py
import os
import sys

import psycopg2

RUTA = sys.argv[1] if len(sys.argv) > 1 else "/data/output/resultado/part-00000"


def leer_resultados(ruta):
    registros = []
    with open(ruta) as archivo:
        for linea in archivo:
            partes = linea.strip().split("\t")
            # cada linea es: tienda <TAB> ticket_promedio <TAB> num_ventas
            if len(partes) != 3:
                continue
            tienda, promedio, ventas = partes
            registros.append((tienda, float(promedio), int(ventas)))
    return registros


def main():
    if not os.path.exists(RUTA):
        print(f"No encuentro {RUTA}. Primero hay que correr el job de Hadoop.")
        sys.exit(1)

    registros = leer_resultados(RUTA)

    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )
    cur = conn.cursor()

    # misma tabla que crea la api, por si este script se corre antes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            tienda          VARCHAR(10) PRIMARY KEY,
            ticket_promedio NUMERIC(12, 2) NOT NULL,
            num_ventas      INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ON CONFLICT: si la tienda ya estaba se actualiza en vez de duplicarse,
    # asi el script se puede correr varias veces sin problema
    for registro in registros:
        cur.execute(
            """INSERT INTO resultados (tienda, ticket_promedio, num_ventas)
               VALUES (%s, %s, %s)
               ON CONFLICT (tienda) DO UPDATE
                   SET ticket_promedio = EXCLUDED.ticket_promedio,
                       num_ventas = EXCLUDED.num_ventas""",
            registro,
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Listo: se cargaron {len(registros)} registros en la tabla resultados")


if __name__ == "__main__":
    main()
