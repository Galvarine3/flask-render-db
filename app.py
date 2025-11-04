from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

# Obtener la URL de conexión desde las variables de entorno (Render la entrega automáticamente)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Función para inicializar la tabla si no existe
def inicializar_tabla():
    try:
        conn = psycopg2.connect(DATABASE_URL)
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
        print("✅ Tabla 'usuarios' verificada/creada correctamente.")
    except Exception as e:
        print("❌ Error al inicializar la tabla:", e)

# Inicializar tabla al inicio
inicializar_tabla()


# 🔹 Ruta principal
@app.route('/')
def index():
    return "🚀 Servidor Flask funcionando correctamente en Render"


# 🔹 Ruta para verificar conexión a la base de datos
@app.route("/check_db")
def check_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return f"✅ Conexión exitosa a la base de datos - hora del servidor: {result[0]}"
    except Exception as e:
        return f"❌ Error al conectar a la base de datos: {e}"


# 🔹 (Ejemplo) Ruta para registrar usuarios desde tu app Android
@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    nombre = data.get('nombre')
    correo = data.get('correo')

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (nombre, correo) VALUES (%s, %s)", (nombre, correo))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"mensaje": "Usuario registrado correctamente ✅"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# 🔹 Ruta para obtener todos los usuarios registrados
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, correo, fecha_registro FROM usuarios ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        usuarios = []
        for r in rows:
            usuarios.append({
                "id": r[0],
                "nombre": r[1],
                "correo": r[2],
                "fecha_registro": r[3].isoformat()
            })

        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 Iniciar aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
