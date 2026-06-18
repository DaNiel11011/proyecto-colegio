from flask import Blueprint, render_template, request, redirect, session
from db import conectar
from models import usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return render_template("index.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = conectar()
    cur = conn.cursor()
    user = usuario.obtener_por_credenciales(cur, username, password)
    cur.close()
    conn.close()

    if user:
        session["usuario"]    = username
        session["rol"]        = user[0]
        session["id_usuario"] = user[1]

        if user[0] == "ADMIN":
            return redirect("/admin")
        elif user[0] == "PROFESOR":
            return redirect("/profesor")
        elif user[0] == "ESTUDIANTE":
            return redirect("/estudiante")
        elif user[0] == "ADMINISTRATIVO":
            return redirect("/administrativo")

    return render_template("index.html", error="Usuario o contraseña incorrectos")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
