import os
from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

def get_conn():
    # Lee siempre la variable en cada conexión (más seguro en producción)
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurada en Render (Environment Variables).")
    return psycopg2.connect(database_url)

def init_db():
    # Crea tabla si no existe (PostgreSQL)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
            """)
        conn.commit()

# ✅ IMPORTANTE: en Render (gunicorn) NO corre el bloque __main__,
# así que inicializamos la DB al arrancar el servicio.
try:
    init_db()
except Exception as e:
    # No detenemos el server si falla al iniciar; lo mostramos en logs.
    print("DB init warning:", e)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre, email FROM usuarios ORDER BY id DESC")
            rows = cur.fetchall()

    usuarios = [{"id": r[0], "nombre": r[1], "email": r[2]} for r in rows]
    return jsonify(usuarios)

@app.route("/api/usuarios", methods=["POST"])
def crear_usuario():
    data = request.get_json(force=True)
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip()

    if not nombre or not email:
        return jsonify({"error": "Faltan datos: nombre y email"}), 400

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuarios (nombre, email) VALUES (%s, %s) RETURNING id",
                    (nombre, email)
                )
                new_id = cur.fetchone()[0]
            conn.commit()

        return jsonify({"id": new_id, "nombre": nombre, "email": email})

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Ese email ya existe"}), 400

    except Exception as e:
        # Para ver el error real en Render Logs
        print("ERROR /api/usuarios POST:", e)
        return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    # Esto solo aplica cuando lo corras en tu PC (local)
    app.run(debug=True)
