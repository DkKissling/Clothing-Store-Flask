from flask import Flask
from dotenv import load_dotenv
import os
from extensions import db, migrate, mail  # Importamos las extensiones desde un archivo separado

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Configuración de Flask-Mail

app.config['MAIL_SERVER'] = 'smtp.pythonanywhere.com'  # Servidor SMTP de PythonAnywhere
app.config['MAIL_PORT'] = int(os.getenv('SMTP_PORT', 587))  # Asegúrate de que este puerto sea correcto
app.config['MAIL_USE_TLS'] = True  # Asegúrate de usar TLS
app.config['MAIL_USERNAME'] = os.getenv('nombre de usuario pythonanywhere')  # Tu usuario de PythonAnywhere
app.config['MAIL_PASSWORD'] = os.getenv('contraseña de python anywhere')  # Tu contraseña de PythonAnywhere


# Inicializa las extensiones
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# Importa los blueprints después de crear 'db'
from routes import auth, main, product

app.register_blueprint(auth.bp)
app.register_blueprint(main.bp)
app.register_blueprint(product.bp)

