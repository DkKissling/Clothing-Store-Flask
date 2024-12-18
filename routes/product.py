# product.py
from sqlalchemy.sql.expression import func
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from werkzeug.utils import secure_filename 
from models import Producto, Categoria, Descuento, ProductoImagen
from app import db  
from services.precio_service import formatear_precio_mostrar
from flask import current_app

bp = Blueprint('product', __name__)

@bp.route('/shop')
def shop():
    categorias = Categoria.query.all()
    categoria_id = request.args.get('category', type=int)
    page = request.args.get('page', 1, type=int)

    # Modificamos la query base para incluir solo productos en stock
    productos_query = Producto.query.filter_by(stock=True)

    if categoria_id:
        productos_query = productos_query.filter_by(categoria_id=categoria_id)
        categoria_seleccionada = Categoria.query.get(categoria_id)
    else:
        categoria_seleccionada = None

    productos_paginados = productos_query.paginate(page=page, per_page=12)
    productos = productos_paginados.items

    # Agregar la imagen y precio formateado a los productos
    for producto in productos:
        imagen_principal = ProductoImagen.query.filter_by(producto_id=producto.producto_id, es_principal=True).first()
        if imagen_principal:
            producto.imagen = imagen_principal.url_imagen
        else:
            producto.imagen = 'default.jpg'
        
        producto.precio_formateado = formatear_precio_mostrar(producto)

    return render_template('shop.html', 
                           categorias=categorias, 
                           productos=productos, 
                           categoria_seleccionada=categoria_seleccionada,
                           productos_paginados=productos_paginados)
    
@bp.route('/product/<int:product_id>')
def product(product_id):
    producto = Producto.query.get_or_404(product_id)
    
    imagen_principal = ProductoImagen.query.filter_by(producto_id=producto.producto_id, es_principal=True).first()
    if imagen_principal:
        producto.imagen = imagen_principal.url_imagen
    else:
        producto.imagen = 'default.jpg'

    producto.precio_formateado = formatear_precio_mostrar(producto)

    featured_products = Producto.query.order_by(func.random()).limit(4).all()
    for prod in featured_products:
        prod.precio_formateado = formatear_precio_mostrar(prod)
        imagen_principal = ProductoImagen.query.filter_by(producto_id=prod.producto_id, es_principal=True).first()
        if imagen_principal:
            prod.imagen = imagen_principal.url_imagen
        else:
            prod.imagen = 'default.jpg'
    
    return render_template('product.html', producto=producto, featured_products=featured_products)

@bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para añadir un producto', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nombre = request.form.get('product-name')
        descripcion = request.form.get('product-description')
        precio = request.form.get('product-price')
        categoria_id = request.form.get('category-id')
        principal_image = request.form.get('principal-image')

        # Verificar los campos obligatorios
        if not all([nombre, descripcion, precio, categoria_id]):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('product.add_product'))

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            usuario_id=user_id,
            categoria_id=categoria_id
        )

        db.session.add(nuevo_producto)
        db.session.flush()  # Para obtener el ID del producto recién creado

        # Función para guardar imagen
        def save_image(imagen, index):
            if imagen and imagen.filename:
                filename = secure_filename(imagen.filename)
                image_path = os.path.join('static', 'img', 'products', filename)
                full_path = os.path.join(current_app.root_path, image_path)
                imagen.save(full_path)
                
                db_image_path = f"../static/img/products/{filename}"
                es_principal = str(index) == principal_image
                nueva_imagen = ProductoImagen(
                    producto_id=nuevo_producto.producto_id,
                    url_imagen=db_image_path,
                    es_principal=es_principal
                )
                db.session.add(nueva_imagen)
                return True
            return False

        # Guardar imágenes
        imagenes_guardadas = 0
        for i in range(1, 5):  # 1 a 4 inclusive
            imagen = request.files.get(f'product-image-{i}')
            if imagen and imagen.filename:
                if save_image(imagen, i):
                    imagenes_guardadas += 1

        if imagenes_guardadas == 0:
            db.session.rollback()
            flash('Debe subir al menos una imagen', 'error')
            return redirect(url_for('product.add_product'))

        db.session.commit()
        flash(f'Producto añadido con éxito. Se guardaron {imagenes_guardadas} imágenes.', 'success')
        return redirect(url_for('product.shop'))

    categorias = Categoria.query.all()
    return render_template('add_product.html', categorias=categorias)

@bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para editar un producto', 'error')
        return redirect(url_for('auth.login'))

    producto = Producto.query.get_or_404(product_id)

    if producto.usuario_id != user_id:
        abort(403)

    if request.method == 'POST':
        producto.nombre = request.form.get('product-name')
        producto.descripcion = request.form.get('product-description')
        producto.precio = request.form.get('product-price')
        producto.categoria_id = request.form.get('category-id')

        imagen = request.files.get('product-image')
        if imagen:
            filename = secure_filename(imagen.filename)
            image_path = os.path.join('static/img/products', filename)
            imagen.save(image_path)

            imagen_principal = ProductoImagen.query.filter_by(producto_id=producto.producto_id, es_principal=True).first()
            if imagen_principal:
                imagen_principal.url_imagen = filename
            else:
                nueva_imagen = ProductoImagen(
                    producto_id=producto.producto_id,
                    url_imagen=filename,
                    es_principal=True
                )
                db.session.add(nueva_imagen)

        descuento_id = request.form.get('discount-id')
        producto.descuento_id = descuento_id if descuento_id else None

        db.session.commit()
        flash('Producto actualizado con éxito', 'success')
        return redirect(url_for('product.product', product_id=producto.producto_id))

    categorias = Categoria.query.all()
    descuentos = Descuento.query.all()

    return render_template('edit_product.html', 
                           producto=producto, 
                           categorias=categorias, 
                           descuentos=descuentos,
                           descuento_aplicado=producto.descuento_id)

@bp.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para borrar un producto', 'error')
        return redirect(url_for('auth.login'))

    producto = Producto.query.get_or_404(product_id)

    if producto.usuario_id != user_id:
        abort(403)

    # Eliminar las imágenes asociadas al producto
    ProductoImagen.query.filter_by(producto_id=product_id).delete()

    db.session.delete(producto)
    db.session.commit()
    flash('Producto borrado con éxito', 'success')
    return redirect(url_for('product.shop'))

@bp.route('/cart')
def cart():
    return render_template('cart.html')

@bp.route('/order-management')
def orderManagement():
    return render_template('order-management.html')

@bp.route('/toggle_stock/<int:product_id>', methods=['POST'])
def toggle_stock(product_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autorizado'}), 401

    producto = Producto.query.get_or_404(product_id)

    if producto.usuario_id != user_id:
        return jsonify({'error': 'Prohibido'}), 403

    try:
        # Cambiar el estado del stock
        producto.stock = not producto.stock
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_stock_status': producto.stock,
            'message': 'En stock' if producto.stock else 'Sin stock'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    
    
@bp.route('/add_category', methods=['GET', 'POST'])
def add_category():
    # Verificar si el usuario está logueado
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para añadir una categoría', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        nombre = request.form.get('category-name')
        
        # Verificar que el nombre no esté vacío
        if not nombre:
            flash('El nombre de la categoría es obligatorio', 'error')
            return redirect(url_for('product.add_category'))
        
        # Verificar si la categoría ya existe
        categoria_existente = Categoria.query.filter_by(nombre=nombre).first()
        if categoria_existente:
            flash('Ya existe una categoría con ese nombre', 'error')
            return redirect(url_for('product.add_category'))
        
        # Crear nueva categoría
        nueva_categoria = Categoria(nombre=nombre)
        
        try:
            db.session.add(nueva_categoria)
            db.session.commit()
            flash('Categoría agregada con éxito', 'success')
            return redirect(url_for('product.shop'))
        except Exception as e:
            db.session.rollback()
            flash('Error al agregar la categoría', 'error')
            return redirect(url_for('product.add_category'))
    
    return render_template('add_category.html')


@bp.route('/delete-category', methods=['GET'])
def delete_category_view():
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para eliminar categorías', 'error')
        return redirect(url_for('auth.login'))
    
    categorias = Categoria.query.all()
    return render_template('delete_category.html', categorias=categorias)

@bp.route('/delete-category/<int:categoria_id>', methods=['POST'])
def delete_category(categoria_id):  # Añadimos el parámetro aquí
    user_id = session.get('user_id')
    if not user_id:
        flash('Debes iniciar sesión para eliminar categorías', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        categoria = Categoria.query.get_or_404(categoria_id)
        
        # Verificar si hay productos asociados a esta categoría
        productos = Producto.query.filter_by(categoria_id=categoria_id).first()
        if productos:
            flash('No se puede eliminar la categoría porque tiene productos asociados', 'error')
            return redirect(url_for('product.delete_category_view'))
        
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoría eliminada con éxito', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la categoría', 'error')
    
    return redirect(url_for('product.delete_category_view'))

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Verificar si el usuario está iniciado sesión
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    # Obtener el producto
    producto = Producto.query.get_or_404(product_id)
    
    # Obtener cantidad del formulario (por defecto 1 si no se especifica)
    quantity = request.form.get('quantity', type=int, default=1)
    size = request.form.get('size', default='')

    # Inicializar carrito en sesión si no existe
    if 'cart' not in session:
        session['cart'] = []

    # Verificar si el producto ya está en el carrito
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id and item['size'] == size:
            item['quantity'] += quantity
            break
    else:
        # Si el producto no está en el carrito, añadir nuevo elemento
        cart.append({
            'product_id': product_id,
            'name': producto.nombre,
            'price': float(producto.precio),
            'quantity': quantity,
            'size': size,
            'image': producto.imagenes[0].url_imagen if producto.imagenes else '../static/img/products/default.jpg'
        })

    session['cart'] = cart
    session.modified = True  # Asegurar que la sesión se guarde

    return jsonify({'message': 'Producto añadido al carrito'}), 200


@bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    # Verificar si el usuario está iniciado sesión
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    # Verificar si hay un carrito en la sesión
    if 'cart' not in session:
        return jsonify({'error': 'Carrito no encontrado'}), 404

    # Obtener el carrito actual
    cart = session['cart']

    # Encontrar y eliminar el producto
    cart = [item for item in cart if item['product_id'] != product_id]

    # Actualizar el carrito en la sesión
    session['cart'] = cart
    session.modified = True

    return jsonify({
        'message': 'Producto eliminado del carrito',
        'cart_count': len(cart)
    }), 200
    

@bp.route('/update_cart_quantity/<int:product_id>', methods=['POST'])
def update_cart_quantity(product_id):
    # Verificar si el usuario está iniciado sesión
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    # Verificar si hay un carrito en la sesión
    if 'cart' not in session:
        return jsonify({'error': 'Carrito no encontrado'}), 404

    # Obtener la nueva cantidad del request
    data = request.get_json()
    new_quantity = data.get('quantity', 1)

    # Obtener el carrito actual
    cart = session['cart']

    # Actualizar la cantidad del producto
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = max(1, new_quantity)  # Asegurar que la cantidad sea al menos 1
            break

    # Actualizar el carrito en la sesión
    session['cart'] = cart
    session.modified = True

    return jsonify({
        'success': True,
        'message': 'Cantidad actualizada'
    }), 200