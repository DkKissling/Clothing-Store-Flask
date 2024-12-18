from app import db
from sqlalchemy.orm import relationship


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Genero(db.Model):
    genero_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class Localidad(db.Model):
    localidad_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincia.provincia_id'))

class Pais(db.Model):
    pais_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Permiso(db.Model):
    permiso_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class Persona(db.Model):
    persona_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    genero_id = db.Column(db.Integer, db.ForeignKey('genero.genero_id'))
    localidad_id = db.Column(db.Integer, db.ForeignKey('localidad.localidad_id'))

class Producto(db.Model):
    producto_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Boolean, nullable=False, default=False)  # Cambiado a Boolean
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    categoria = relationship('Categoria', backref='productos')
    descuento_id = db.Column(db.Integer, db.ForeignKey('descuento.descuento_id'), nullable=True)
    descuento = relationship('Descuento', backref='productos_descuento')
    imagenes = relationship('ProductoImagen', back_populates='producto', cascade='all, delete-orphan')
    
class ProductoImagen(db.Model):
    imagen_id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.producto_id'), nullable=False)
    url_imagen = db.Column(db.String(255), nullable=False)
    es_principal = db.Column(db.Boolean, default=False)
    producto = relationship('Producto', back_populates='imagenes')
    
class Provincia(db.Model):
    provincia_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.pais_id'))

class Usuario(db.Model):
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    correo_electronico = db.Column(db.String(255), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    temp_password = db.Column(db.String(255))  
    foto_perfil = db.Column(db.String(255), nullable=True, default=None)  
    permiso_id = db.Column(db.Integer, db.ForeignKey('permiso.permiso_id'))
    persona_id = db.Column(db.Integer, db.ForeignKey('persona.persona_id'), nullable=False)
    persona = db.relationship('Persona', backref=db.backref('usuario', uselist=False))

    
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    imagen = db.Column(db.String(100), nullable=True) 
    autor_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'))
    autor = db.relationship('Usuario', backref='blog_posts')
    
class Direccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(255), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'))
    usuario = db.relationship('Usuario', backref='direcciones')


class Descuento(db.Model):
    descuento_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)  # Descuento en porcentaje (ej. 10.00 para 10%)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    activo = db.Column(db.Boolean, default=True)