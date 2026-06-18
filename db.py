import psycopg2
import os

def conectar():
    database_url = os.getenv("DATABASE_URL")

    # Si estamos en Render o en otro servidor
    if database_url:
        return psycopg2.connect(database_url)

    # Si estamos trabajando en la PC local
    os.environ["PGPASSFILE"] = "NUL"

    return psycopg2.connect(
        host="localhost",
        database="colegio_db",
        user="postgres",
        password="22022005"
    )