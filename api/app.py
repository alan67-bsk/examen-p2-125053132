# app.py
# API del examen: CRUD sobre la tabla "resultados", que guarda la salida del job
# de MapReduce (ticket promedio por tienda).
import os

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_connection():
    # DB_HOST vale "db", que es el nombre del servicio en docker-compose.yml.
    # Docker resuelve ese nombre dentro de la red del compose, no hace falta la IP.
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )


def consultar(sql, parametros=None):
    """Ejecuta un SQL, guarda los cambios y regresa las filas como diccionarios."""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, parametros)
        filas = cur.fetchall() if cur.description else []
        conn.commit()
        cur.close()
        return filas
    finally:
        conn.close()


def crear_tabla():
    consultar("""
        CREATE TABLE IF NOT EXISTS resultados (
            tienda          VARCHAR(10) PRIMARY KEY,
            ticket_promedio NUMERIC(12, 2) NOT NULL,
            num_ventas      INTEGER NOT NULL DEFAULT 0
        )
    """)


def a_json(fila):
    # NUMERIC llega como Decimal y se pasa a float para que salga como numero
    return {
        "tienda": fila["tienda"],
        "ticket_promedio": float(fila["ticket_promedio"]),
        "num_ventas": fila["num_ventas"],
    }


@app.route("/")
def inicio():
    return jsonify({
        "servicio": "API DataMart",
        "pregunta": "Ticket promedio por tienda",
        "endpoints": [
            "GET /resultados",
            "GET /resultados/<tienda>",
            "POST /resultados",
            "PUT /resultados/<tienda>",
            "DELETE /resultados/<tienda>",
        ],
    })


# ---------- Lectura ----------

@app.route("/resultados", methods=["GET"])
def listar_resultados():
    filas = consultar(
        "SELECT tienda, ticket_promedio, num_ventas FROM resultados ORDER BY tienda"
    )
    return jsonify([a_json(f) for f in filas])


@app.route("/resultados/<tienda>", methods=["GET"])
def obtener_resultado(tienda):
    filas = consultar(
        "SELECT tienda, ticket_promedio, num_ventas FROM resultados WHERE tienda = %s",
        (tienda.upper(),),
    )
    if not filas:
        return jsonify({"error": f"No hay resultados para la tienda {tienda}"}), 404
    return jsonify(a_json(filas[0]))


# ---------- Escritura ----------

@app.route("/resultados", methods=["POST"])
def crear_resultado():
    datos = request.get_json(silent=True) or {}
    try:
        tienda = str(datos["tienda"]).strip().upper()
        ticket = float(datos["ticket_promedio"])
        ventas = int(datos.get("num_ventas", 0))
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": "Se necesita tienda (texto), ticket_promedio (numero) y opcional num_ventas (entero)"
        }), 400

    if tienda == "":
        return jsonify({"error": "La tienda no puede ir vacia"}), 400

    try:
        filas = consultar(
            """INSERT INTO resultados (tienda, ticket_promedio, num_ventas)
               VALUES (%s, %s, %s)
               RETURNING tienda, ticket_promedio, num_ventas""",
            (tienda, ticket, ventas),
        )
    except psycopg2.IntegrityError:
        return jsonify({"error": f"La tienda {tienda} ya existe, usa PUT para cambiarla"}), 409

    return jsonify(a_json(filas[0])), 201


@app.route("/resultados/<tienda>", methods=["PUT"])
def actualizar_resultado(tienda):
    datos = request.get_json(silent=True) or {}
    try:
        ticket = float(datos["ticket_promedio"])
        ventas = int(datos["num_ventas"]) if "num_ventas" in datos else None
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": "Se necesita ticket_promedio (numero) y opcional num_ventas (entero)"
        }), 400

    # COALESCE deja num_ventas como estaba si no lo mandaron
    filas = consultar(
        """UPDATE resultados
              SET ticket_promedio = %s,
                  num_ventas = COALESCE(%s, num_ventas)
            WHERE tienda = %s
        RETURNING tienda, ticket_promedio, num_ventas""",
        (ticket, ventas, tienda.upper()),
    )
    if not filas:
        return jsonify({"error": f"No hay resultados para la tienda {tienda}"}), 404
    return jsonify(a_json(filas[0]))


@app.route("/resultados/<tienda>", methods=["DELETE"])
def eliminar_resultado(tienda):
    filas = consultar(
        "DELETE FROM resultados WHERE tienda = %s RETURNING tienda",
        (tienda.upper(),),
    )
    if not filas:
        return jsonify({"error": f"No hay resultados para la tienda {tienda}"}), 404
    return jsonify({"mensaje": f"Se elimino la tienda {filas[0]['tienda']}"})


if __name__ == "__main__":
    crear_tabla()
    app.run(host="0.0.0.0", port=5000)
