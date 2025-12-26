from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, email FROM usuarios ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
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
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre, email) VALUES (?, ?)", (nombre, email))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return jsonify({"id": new_id, "nombre": nombre, "email": email})
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Ese email ya existe"}), 400

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
