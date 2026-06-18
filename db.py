import psycopg2
import os

def conectar():
    os.environ["PGPASSFILE"] = "NUL"
    return psycopg2.connect(
        host="localhost",
        database="colegio_db",
        user="postgres",
        password="22022005"
    )

# en password se debe colocar la contraseña del usuario postgres, si es diferente a la que se muestra.