from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.profesor_controller import profesor_bp
from controllers.estudiante_controller import estudiante_bp
from controllers.administrativo_controller import administrativo_bp

app = Flask(__name__)
app.secret_key = "12345"

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profesor_bp)
app.register_blueprint(estudiante_bp)
app.register_blueprint(administrativo_bp)

if __name__ == "__main__":
    app.run(debug=True)

#en la terminal antes de intentar hacer correr la aplicación, 
#se debe ejecutar el comando "pip install flask psycopg2" para instalar las dependencias necesarias

#FINALMENTE
#posterior a haber echo lo que indica db_colegio.sql y db.py, se debe ejecutar el comando "python app.py" para correr la aplicación.