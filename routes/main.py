# main.py

from flask import Blueprint, render_template, session, flash, redirect, url_for, abort, request
from sqlalchemy.orm import joinedload
import os
import random
from math import ceil
from flask_mail import Message
from datetime import datetime
from models import Usuario, Producto, ProductoImagen, Blog, Direccion, Localidad, Genero
from app import db, mail  
from datetime import datetime
from services.precio_service import formatear_precio_mostrar, calcular_precio_con_descuento
from werkzeug.utils import secure_filename

BLOG_UPLOAD_FOLDER = 'static/img/blog'
UPLOAD_PROFILE_FOLDER = 'static/img/profiles'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
def index():
    # Obtener todos los productos con sus imágenes principales
    productos = Producto.query.join(ProductoImagen).filter(ProductoImagen.es_principal == True).all()
    
    # Formatear los precios de todos los productos
    for producto in productos:
        producto.precio_formateado = formatear_precio_mostrar(producto)
        
        # Obtener la URL de la imagen principal
        imagen_principal = next((img for img in producto.imagenes if img.es_principal), None)
        producto.imagen_url = imagen_principal.url_imagen if imagen_principal else '../static/img/products/default.jpg'
    
    # Ordenar los productos por ID en orden descendente para las nuevas llegadas
    productos_ordenados = sorted(productos, key=lambda p: p.producto_id, reverse=True)
    
    # Obtener productos destacados (al azar)
    featured_products = random.sample(productos, min(len(productos), 4))
    
    # Obtener nuevas llegadas (los productos con los IDs más altos)
    new_products = productos_ordenados[:4]

    return render_template('index.html', 
                           featured_products=featured_products, 
                           new_products=new_products)
    
    
# Ruta: /profile - Muestra el perfil del usuario
@bp.route('/profile')
def profile():
    # Obtener el ID del usuario de la sesión
    user_id = session.get('user_id')
    # Si no hay un ID de usuario en la sesión, redirigir al login
    if not user_id:
        flash('Por favor inicia sesión para ver tu perfil', 'error')  # Mostrar mensaje de error
        return redirect(url_for('auth.login'))  # Redirigir a la página de inicio de sesión

    # Consultar la información del usuario junto con la relación 'persona'
    usuario = Usuario.query.options(joinedload(Usuario.persona)).get(user_id)
    # Si no se encuentra el usuario, lanzar error 404
    if not usuario:
        abort(404)

    # Consultar todos los productos asociados al usuario actual
    productos = Producto.query.filter_by(usuario_id=user_id).all()
    # Formatear el precio de cada producto para mostrarlo de forma legible
    for producto in productos:
        producto.precio_formateado = formatear_precio_mostrar(producto)

    # Renderizar la plantilla del perfil, pasando los datos del usuario y sus productos
    return render_template('profile.html', 
                           usuario=usuario, 
                           productos=productos)
    

# Ruta: /contact - Muestra y procesa el formulario de contacto
@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    # Verificar si la solicitud es de tipo POST (el formulario fue enviado)
    if request.method == 'POST':
        # Obtener los datos del formulario enviados por el usuario
        nombre = request.form.get('nombre')  # Nombre del remitente
        email = request.form.get('email')    # Correo electrónico del remitente
        asunto = request.form.get('asunto')  # Asunto del mensaje
        mensaje = request.form.get('mensaje')  # Contenido del mensaje

        # Validar que todos los campos del formulario estén completos
        if not nombre or not email or not asunto or not mensaje:
            flash('Todos los campos son obligatorios.', 'error')  # Mostrar mensaje de error si falta un campo
        else:
            # Enviar el correo utilizando los datos proporcionados
            enviar_correo(nombre, email, asunto, mensaje)
            flash('Mensaje enviado con éxito.', 'success')  # Mostrar mensaje de éxito
            return redirect(url_for('main.contact'))  # Redirigir a la misma página de contacto

    # Renderizar la plantilla del formulario de contacto
    return render_template('contact.html')

def enviar_correo(nombre, email, asunto, mensaje):
    msg = Message(asunto, recipients=['example@gmail.com'])
    msg.body = f"Nombre: {nombre}\nEmail: {email}\nMensaje:\n{mensaje}"
    mail.send(msg)


@bp.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para crear una entrada de blog', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        contenido = request.form.get('contenido')
        imagen = request.files.get('imagen')

        if not titulo or not contenido:
            flash('El título y el contenido son obligatorios', 'error')
        else:
            # Manejar la carga de imagen
            imagen_filename = None
            if imagen and imagen.filename != '':
                if allowed_file(imagen.filename):
                    # Generar un nombre de archivo único
                    filename = secure_filename(imagen.filename)
                    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    filepath = os.path.join(BLOG_UPLOAD_FOLDER, filename)
                    imagen.save(filepath)
                    imagen_filename = filename
                else:
                    flash('Tipo de archivo no permitido. Use PNG, JPG, JPEG o GIF.', 'error')
                    return redirect(url_for('main.add_post'))

            nuevo_post = Blog(
                titulo=titulo,
                contenido=contenido,
                fecha_creacion=datetime.utcnow(),
                autor_id=session['user_id'],
                imagen=imagen_filename  # Guardar el nombre de archivo de imagen
            )
            db.session.add(nuevo_post)
            db.session.commit()
            flash('Entrada de blog creada con éxito', 'success')
            return redirect(url_for('main.blog'))

    return render_template('add_post.html')

# Modificar la ruta de blog para manejar la imagen
@bp.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts_per_page = 5

    # Verificar si el usuario ha iniciado sesión
    user_logged_in = 'user_id' in session

    # Obtener todos los posts ordenados por fecha de creación descendente
    blog_posts = Blog.query.order_by(Blog.fecha_creacion.desc()).all()

    # Calcular el número total de páginas
    total_pages = ceil(len(blog_posts) / posts_per_page)

    # Obtener los posts para la página actual
    start = (page - 1) * posts_per_page
    end = start + posts_per_page
    current_page_posts = blog_posts[start:end]

    # Modificar para usar la imagen del post si está disponible
    for post in current_page_posts:
        # Si hay una imagen en la base de datos, usarla; de lo contrario, usar una imagen por defecto
        post.img = post.imagen if post.imagen else random.choice(['b1 (1).jpg', 'b2 (1).jpg', 'b3.jpg', 'b4.jpg', 'b5.jpg'])

    return render_template('blog.html',
                        blog_posts=current_page_posts,
                        current_page=page,
                        total_pages=total_pages,
                        user_logged_in=user_logged_in)

@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Por favor inicia sesión para editar tu perfil', 'error')
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.options(joinedload(Usuario.persona)).get(user_id)
    if not usuario:
        abort(404)

    if request.method == 'POST':
        # Actualizar los datos del usuario
        usuario.nombre_usuario = request.form.get('username')
        usuario.persona.nombre = request.form.get('nombre')
        usuario.persona.apellido = request.form.get('apellido')

        # Manejar la foto de perfil
        foto = request.files.get('photo')
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            filepath = os.path.join(UPLOAD_PROFILE_FOLDER, f"{user_id}_{filename}")
            foto.save(filepath)
            usuario.foto_perfil = filepath  # Guardar la ruta de la imagen

        try:
            db.session.commit()
            flash('Perfil actualizado con éxito', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el perfil: {e}', 'error')

        return redirect(url_for('main.profile'))

    return render_template('edit_profile.html', usuario=usuario)


# Ruta: /config_profile - Configuración del perfil del usuario
# Se proporciona una sección por defecto 'personal-info' si no se especifica otra
@bp.route('/config_profile', defaults={'section': 'personal-info'}, methods=['GET', 'POST'])
@bp.route('/config_profile/<section>', methods=['GET', 'POST'])
def config_profile(section):
    # Lista de secciones válidas disponibles para la configuración del perfil
    valid_sections = [
        'personal-info', 'addresses', 'product-management',
        'order-management', 'analytics', 'reviews', 'notifications',
        'account-security', 'subscriptions', 'privacy-security', 'support', 'store-settings'
    ]

    # Si la sección proporcionada no está en la lista, asignar la sección por defecto
    if section not in valid_sections:
        section = 'personal-info'

    # Obtener el ID del usuario almacenado en la sesión
    user_id = session.get('user_id')

    # Si no hay un usuario autenticado, redirigir a la página de inicio de sesión
    if not user_id:
        flash('Por favor inicia sesión para acceder a la configuración del perfil', 'error')  # Mensaje de error
        return redirect(url_for('auth.login'))  # Redirigir al login

    # Consultar el usuario actual y cargar la relación con la tabla 'persona'
    usuario = Usuario.query.options(joinedload(Usuario.persona)).get(user_id)

    # Si el usuario no existe, lanzar un error 404
    if not usuario:
        abort(404)

    # Obtener todas las localidades y géneros disponibles para el formulario
    localidades = Localidad.query.all()
    generos = Genero.query.all()

    # Procesar el formulario cuando el método sea POST
    if request.method == 'POST':
        # Verificar si la sección actual es 'personal-info'
        if section == 'personal-info':
            # Actualizar los datos personales del usuario con la información del formulario
            usuario.nombre_usuario = request.form.get('username')  # Nuevo nombre de usuario
            usuario.persona.nombre = request.form.get('name')  # Nuevo nombre personal
            usuario.persona.apellido = request.form.get('lastname')  # Nuevo apellido
            usuario.correo_electronico = request.form.get('email')  # Nuevo correo electrónico
            usuario.persona.genero_id = request.form.get('genero')  # ID del género seleccionado
            usuario.persona.localidad_id = request.form.get('localidad')  # ID de la localidad seleccionada
            
            try:
                # Guardar los cambios en la base de datos
                db.session.commit()
                flash('Información personal actualizada con éxito', 'success')  # Mensaje de éxito
            except Exception as e:
                # En caso de error, revertir los cambios
                db.session.rollback()
                flash('Error al actualizar la información personal: ' + str(e), 'error')  # Mensaje de error
            
        # Verificar si la sección actual es 'addresses'
        elif section == 'addresses':
            # Obtener la nueva dirección ingresada en el formulario
            nueva_direccion = request.form.get('direccion-new')
            if nueva_direccion:  # Si se proporciona una dirección nueva
                # Crear una nueva instancia de dirección asociada al usuario actual
                direccion = Direccion(direccion=nueva_direccion, usuario_id=user_id)
                db.session.add(direccion)  # Añadir la nueva dirección a la base de datos
                try:
                    # Guardar los cambios en la base de datos
                    db.session.commit()
                    flash('Nueva dirección añadida con éxito', 'success')  # Mensaje de éxito
                except Exception as e:
                    # En caso de error, revertir los cambios
                    db.session.rollback()
                    flash('Error al añadir la dirección: ' + str(e), 'error')  # Mensaje de error

        # Aquí puedes añadir la lógica para las otras secciones
        elif section == 'product-management':
            # Lógica para gestión de productos
            pass

        elif section == 'order-management':
            # Lógica para gestión de pedidos
            pass

        elif section == 'analytics':
            # Lógica para analytics
            pass

        elif section == 'reviews':
            # Lógica para reviews
            pass

        elif section == 'notifications':
            # Lógica para notificaciones
            pass

        elif section == 'account-security':
            # Lógica para seguridad de la cuenta
            pass

        elif section == 'subscriptions':
            # Lógica para suscripciones
            pass

        elif section == 'privacy-security':
            # Lógica para privacidad y seguridad
            pass

        elif section == 'support':
            # Lógica para soporte
            pass

        elif section == 'store-settings':
            # Lógica para configuración de la tienda
            pass

        return redirect(url_for('main.config_profile', section=section))

    direcciones = Direccion.query.filter_by(usuario_id=user_id).all() if section == 'addresses' else []

    return render_template('config_profile.html', 
                           section=section, 
                           usuario=usuario,
                           direcciones=direcciones,
                           localidades=localidades,
                           generos=generos)

@bp.route('/delete_address/<int:address_id>', methods=['POST'])
def delete_address(address_id):
    if 'user_id' not in session:
        flash('Por favor inicia sesión para eliminar una dirección', 'error')
        return redirect(url_for('auth.login'))

    direccion = Direccion.query.get_or_404(address_id)

    if direccion.usuario_id != session['user_id']:
        abort(403)  # Forbidden

    db.session.delete(direccion)
    db.session.commit()

    flash('Dirección eliminada con éxito', 'success')
    return redirect(url_for('main.config_profile', section='addresses'))

@bp.route('/set_default_address/<int:address_id>', methods=['POST'])
def set_default_address(address_id):
    if 'user_id' not in session:
        flash('Por favor inicia sesión para establecer una dirección predeterminada', 'error')
        return redirect(url_for('auth.login'))

    direccion = Direccion.query.get_or_404(address_id)

    if direccion.usuario_id != session['user_id']:
        abort(403)  # Forbidden

    # Set all addresses to non-default
    Direccion.query.filter_by(usuario_id=session['user_id']).update({Direccion.is_default: False})

    # Set the selected address as default
    direccion.is_default = True
    db.session.commit()

    flash('Dirección establecida como predeterminada con éxito', 'success')
    return redirect(url_for('main.config_profile', section='addresses'))

@bp.route('/user-panel')
def user_panel():
    return render_template('user-panel.html')

@bp.route('/client-reviews')
def client_reviews():
    return render_template('client-reviews.html')

@bp.route('/client-activities')
def client_activities():
    return render_template('client_activities.html')