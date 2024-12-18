from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario, Persona, Categoria, Localidad, Genero
from app import db
from utils import generate_temp_password
import smtplib
import logging
import os
from dotenv import load_dotenv
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():


    # Obtener datos necesarios para el formulario
    categorias = Categoria.query.all()
    localidades = Localidad.query.all()
    generos = Genero.query.all()

    if request.method == 'POST':
        if 'login' in request.form:
            # Lógica de inicio de sesión
            username = request.form['username']
            password = request.form['password']
            
            user = Usuario.query.filter_by(nombre_usuario=username).first()
            if user and user.contrasena == password:
                hashed_password = generate_password_hash(password)
                user.contrasena = hashed_password
                db.session.commit()
                
            if user and (check_password_hash(user.contrasena, password) or (user.temp_password and check_password_hash(user.temp_password, password))):
                session['user_id'] = user.usuario_id
                
                if user.temp_password and check_password_hash(user.temp_password, password):
                    flash('Por favor, cambia tu contrasena temporal.', 'info')
                    return redirect(url_for('auth.reset_password'))
                
                return redirect(url_for('main.profile'))
            else:
                flash('Usuario o contrasena inválidos', 'error')
        
        elif 'register' in request.form:
            # Lógica de registro
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            fecha_nacimiento = request.form['fecha_nacimiento']
            genero_id = request.form['genero_id']
            localidad_id = request.form['localidad_id']
            
            existing_user = Usuario.query.filter((Usuario.nombre_usuario == username) | (Usuario.correo_electronico == email)).first()
            
            if existing_user:
                flash('El nombre de usuario o correo electrónico ya existe', 'error')
            else:
                nueva_persona = Persona(
                    nombre=nombre, 
                    apellido=apellido, 
                    fecha_nacimiento=fecha_nacimiento,
                    genero_id=genero_id,
                    localidad_id=localidad_id
                )
                hashed_password = generate_password_hash(password)
                new_user = Usuario(
                    nombre_usuario=username, 
                    correo_electronico=email, 
                    contrasena=hashed_password, 
                    persona=nueva_persona
                )
                db.session.add(new_user)
                db.session.commit()
                flash('¡Cuenta creada exitosamente! Por favor inicia sesión.', 'success')
                return redirect(url_for('auth.login'))
    
    return render_template('login.html', categorias=categorias, localidades=localidades, generos=generos)

def send_email(to_email, subject, body):
    # Obtener configuración desde variables de entorno
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # Verificar que todas las variables necesarias estén presentes
    if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
        logging.error("Configuración SMTP incompleta")
        print("Variables actuales:")
        print(f"SMTP_SERVER: {smtp_server}")
        print(f"SMTP_PORT: {smtp_port}")
        print(f"SMTP_USERNAME: {smtp_username}")
        print(f"SMTP_PASSWORD: {'*' * len(smtp_password) if smtp_password else 'No configurado'}")
        raise ValueError("Faltan variables de configuración SMTP en el archivo .env")

    # Crear el mensaje MIME
    msg = MIMEMultipart()
    
    # Configurar los encabezados
    msg['From'] = formataddr((str(Header('', 'utf-8')), smtp_username))
    msg['To'] = to_email
    msg['Subject'] = Header(subject, 'utf-8').encode()

    # Adjuntar el cuerpo del mensaje
    text_part = MIMEText(body, 'plain', 'utf-8')
    msg.attach(text_part)

    server = None
    try:
        # Crear la conexión SMTP
        logging.info(f"Intentando conectar a {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        # Identificarse con el servidor
        server.ehlo()
        
        # Iniciar TLS
        server.starttls()
        server.ehlo()  # Nuevo EHLO después de STARTTLS
        
        logging.info("Conexión establecida y TLS iniciado")
        
        # Iniciar sesión
        server.login(smtp_username, smtp_password)
        logging.info("Login exitoso")
        
        # Enviar el correo
        server.send_message(msg)
        logging.info("Correo enviado exitosamente")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Error de autenticación SMTP. Verifica usuario y contraseña.")
        raise
    except smtplib.SMTPException as e:
        logging.error(f"Error SMTP: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Error inesperado al enviar el correo: {str(e)}")
        raise
    finally:
        if server is not None:
            try:
                server.quit()
                logging.info("Conexión SMTP cerrada correctamente")
            except Exception as e:
                logging.error(f"Error al cerrar la conexión SMTP: {str(e)}")
                
                
# Ruta: /forgot_password - Maneja la solicitud de restablecimiento de contraseña
@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    # Verificar si la solicitud es de tipo POST (el formulario fue enviado)
    if request.method == 'POST':
        email = request.form['email']  # Obtener el correo electrónico ingresado en el formulario

        # Buscar en la base de datos si existe un usuario con el correo proporcionado
        user = Usuario.query.filter_by(correo_electronico=email).first()

        if user:  # Si el usuario existe
            # Generar una contraseña temporal aleatoria
            temp_password = generate_temp_password()
            
            # Generar un hash de la contraseña temporal para almacenarlo de forma segura en la base de datos
            hashed_temp_password = generate_password_hash(temp_password)
            user.temp_password = hashed_temp_password  # Guardar la contraseña temporal hash en la base de datos
            db.session.commit()  # Confirmar los cambios en la base de datos

            # Configurar el asunto y cuerpo del correo que se enviará al usuario
            email_subject = 'Tu Contraseña Temporal'
            email_body = f'Tu contraseña temporal es: {temp_password}'

            try:
                # Intentar enviar el correo electrónico con la contraseña temporal
                if send_email(user.correo_electronico, email_subject, email_body):
                    # Mostrar un mensaje de éxito si el correo se envía correctamente
                    flash('Se ha enviado una contraseña temporal a tu correo electrónico.', 'success')
                    return redirect(url_for('auth.reset_password'))  # Redirigir a la página de restablecimiento
            except Exception as e:
                # Manejar errores al enviar el correo electrónico
                flash(f'Hubo un problema al enviar el correo: {str(e)}', 'error')
                logging.error(f"Fallo al enviar correo a {email}: {str(e)}")
            return redirect(url_for('auth.forgot_password'))  # Redirigir al mismo formulario

        else:  # Si no se encontró un usuario con el correo ingresado
            flash('No se encontró ningún usuario con ese correo electrónico.', 'error')  # Mostrar mensaje de error
            logging.warning(f"Intento de recuperación de contraseña para correo no existente: {email}")
            return redirect(url_for('auth.forgot_password'))  # Redirigir al mismo formulario

    # Si la solicitud es de tipo GET (el usuario solo accede a la página)
    return render_template('forgot_password.html')  # Renderizar la plantilla del formulario de recuperación

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' not in session:
        flash('Por favor inicia sesión para cambiar tu contraseña.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('auth.reset_password'))
        
        user_id = session['user_id']
        user = Usuario.query.get(user_id)
        user.contrasena = generate_password_hash(new_password)
        user.temp_password = None  # Eliminar la contraseña temporal
        db.session.commit()

        flash('¡Tu contraseña ha sido cambiada exitosamente!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('reset_password.html')

@bp.route('/logout')
def logout():
    # Cerrar sesión del usuario
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

@bp.route('/2FA_setup')
def faSetup():
    return render_template('2FA_setup.html')