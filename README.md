# Proyecto E-commerce de Ropa

## Descripción
Este es un proyecto de comercio electrónico desarrollado con Flask que permite a los usuarios crear tiendas online para vender productos de ropa. El sistema incluye características como gestión de usuarios, productos, blog, carrito de compras y panel de administración.
Existe una version online para ver las funciones principales, por motivos de seguridad hemos bloqueado el login para evitar que puedan realizar cambios sobre la misma https://newgirls.pythonanywhere.com/, (por ahi pasa que al ingresar por primera vez hay que recargar la pagina debido que el servidor es gratuito y tiene errores) Dejamos algunas imagenes para ver sus funciones principales luego de estar logueado.

## Imagenes de Muestra

En el Perfil en el te va a permitir Agregar, Editar, Borrar y Cambiar el estado de Stock de los productos. Como asi tambien editar el Nombre, Apellido, Imagen y Usuario 
![image](https://github.com/user-attachments/assets/46658149-23cf-457e-85ae-142fee3d94ac)


En el Shop apareceran nuevas opciones para agregar y eliminar categorias para los productos.
![image](https://github.com/user-attachments/assets/6e98d8b2-846d-4d8d-8e63-ee90ddbc864f)


En la ruta Cart vamos a tener la opcion de eligir modificar la cantidad o eliminar el producto que seleccionamos y en caso de tener un descuento aplicarlo.
![image](https://github.com/user-attachments/assets/b66cb14d-8a45-41dd-b0c4-012b633b14e6)


En el panel de configuracion tenemos varias opciones en las cuales se destacan configuracion Personal y Direcciones que permite no solo modificar el usuario nombre, email y Localidad sino tambien la direccion en la cual se asocia al perfil, pudiendo tener hasta 3 direcciones y permitiendo establecer una como predeterminada para las funciones de compra.
![image](https://github.com/user-attachments/assets/49d86bcf-ca73-434b-9b41-7ff0e2725ffa)


En el Blog aparecera un boton para agregar un nuevo post
![image](https://github.com/user-attachments/assets/5349561f-93e2-48f3-a303-00e1fdcbabca)


## Características Principales
- Sistema de autenticación de usuarios
- Gestión de productos con imágenes múltiples
- Sistema de categorías
- Blog integrado
- Carrito de compras
- Panel de configuración de perfil
- Sistema de direcciones múltiples
- Gestión de descuentos
- Sistema de recuperación de contraseña

## Requisitos Previos
- Python 3.x
- pip (gestor de paquetes de Python)
- MySQL/PostgreSQL (base de datos)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar las variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```plaintext
SMTP_SERVER=<tu-servidor-smtp>
SMTP_PORT=<puerto-smtp>
SMTP_USERNAME=<tu-usuario-smtp>
SMTP_PASSWORD=<tu-contraseña-smtp>
DATABASE_URL=<url-de-tu-base-de-datos>
SECRET_KEY=<tu-clave-secreta>
```

5. Crear las carpetas necesarias para almacenamiento:
```bash
mkdir -p static/img/products
mkdir -p static/img/blog
mkdir -p static/img/profiles
```

6. Inicializar la base de datos:
```bash
flask db upgrade
```

## Ejecución
Para ejecutar el proyecto en modo desarrollo:
```bash
flask run
```
La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto
- `auth.py`: Manejo de autenticación y usuarios
- `main.py`: Rutas principales y funcionalidad core
- `product.py`: Gestión de productos y carrito
- `models.py`: Modelos de la base de datos
- `/templates`: Archivos HTML de la aplicación
- `/static`: Archivos estáticos (CSS, JS, imágenes)

## Funcionalidades por Módulo

### Módulo de Autenticación (auth.py)
- Registro de usuarios
- Inicio de sesión
- Recuperación de contraseña
- Gestión de perfiles

### Módulo Principal (main.py)
- Página principal
- Blog
- Contacto
- Gestión de perfiles
- Panel de usuario

### Módulo de Productos (product.py)
- Listado de productos
- Gestión de productos (CRUD)
- Carrito de compras
- Gestión de categorías
- Sistema de stock

## Consideraciones de Seguridad
- Las contraseñas se almacenan hasheadas
- Sistema de recuperación de contraseña seguro
- Protección contra accesos no autorizados
- Validación de formularios
- Manejo seguro de sesiones

## Soporte
Para reportar problemas o solicitar ayuda, por favor crear un issue en el repositorio del proyecto.
