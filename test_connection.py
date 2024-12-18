from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Configurar las credenciales directamente en el código
USERNAME = 'dkkissling'
PASSWORD = 'NuevaContraseñaSegura'
HOST = 'dkkissling.mysql.pythonanywhere-services.com'
DATABASE = 'dkkissling$newGirls'

# Construir la URI de la base de datos
DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}"

def test_connection():
    try:
        # Crear un motor de conexión
        engine = create_engine(DATABASE_URI)
        # Probar la conexión
        with engine.connect() as connection:
            print("¡Conexión exitosa a la base de datos!")
    except OperationalError as e:
        print("Error en la conexión:", e)

if __name__ == "__main__":
    print(f"Intentando conectar a: {HOST}")
    test_connection()