from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def inicializar_tabla():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            correo VARCHAR(150) UNIQUE,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

inicializar_tabla()

@app.route('/')
def home():
    return "🚀 API Flask conectada a PostgreSQL en Render"

@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    nombre = data.get('nombre')
    correo = data.get('correo')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (nombre, correo) VALUES (%s, %s) RETURNING id;", (nombre, correo))
    nuevo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": nuevo_id, "mensaje": "Usuario creado con éxito"}), 201

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, correo, fecha_registro FROM usuarios;")
    filas = cur.fetchall()
    cur.close()
    conn.close()

    usuarios = [
        {"id": f[0], "nombre": f[1], "correo": f[2], "fecha_registro": f[3].isoformat()}
        for f in filas
    ]
    return jsonify(usuarios)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
