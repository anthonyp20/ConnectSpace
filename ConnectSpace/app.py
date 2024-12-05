from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

# Configuración de la clave secreta
app.secret_key = "clave_super_secreta_para_connectspace"

# Conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

# Página de inicio (Login)
@app.route("/")
def index():
    return render_template("index.html")

# Inicio de sesión
@app.route("/connectspace", methods=["POST"])
def login():
    username = request.form["Username"]
    password = request.form["password"]

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        # Redirigir al dashboard
        return redirect(url_for("dashboard"))
    else:
        flash("Usuario o contraseña incorrectos", "error")
        return redirect(url_for("index"))

# Dashboard
@app.route("/connectspace")
def dashboard():
    return "<h1>Bienvenido a ConnectSpace</h1>"

# Restablecimiento de contraseña
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        flash("Enlace para restablecer la contraseña enviado a tu correo.", "success")
        return redirect(url_for("index"))
    return render_template("reset_password.html")

# Registro de usuario
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["password"]
        email = request.form["email"]

        conn = get_db_connection()
        user_exists = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user_exists:
            flash("El usuario ya existe. Intenta con otro.", "error")
            return redirect(url_for("registro"))

        # Guardamos el nuevo usuario con la contraseña cifrada
        hashed_password = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed_password, email),
        )
        conn.commit()
        conn.close()

        flash("Cuenta creada con éxito. Inicia sesión.", "success")
        return redirect(url_for("index"))
    return render_template("registro.html")

# Crear la base de datos y la tabla de usuarios (si no existe)
def init_db():
    conn = get_db_connection()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        );"""
    )
    conn.commit()
    conn.close()

# Llamada para crear la base de datos (únicamente al principio)
init_db()

if __name__ == "__main__":
    app.run(debug=True)
