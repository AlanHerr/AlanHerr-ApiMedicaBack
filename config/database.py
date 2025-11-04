
# Importa módulos necesarios para la configuración y conexión a la base de datos
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from model.products_models import Base
from model.user import User
from dotenv import load_dotenv

# Configura el nivel de logging para mostrar mensajes informativos
logging.basicConfig(level=logging.INFO)

# Carga variables de entorno desde el archivo .env
load_dotenv()

# Obtiene la URI de la base de datos remota desde la variable de entorno
DATABASE_URI = os.getenv('MYSQL_URI')  # Usas esta variable en tu .env
# Define la URI para la base de datos local SQLite como respaldo
SQLITE_URI = 'sqlite:///products_local.db'  # Nombre ajustado para productos

# Función para obtener el motor de conexión a la base de datos
def get_engine():
    """
    Intenta crear una conexión con la base de datos remota. Si falla, usa SQLite local.
    """
    if DATABASE_URI:
        try:
            # Crea el motor de conexión usando la URI remota
            engine = create_engine(DATABASE_URI, echo=False)
            # Probar conexión abriendo y cerrando una conexión
            conn = engine.connect()
            conn.close()
            logging.info('Conexión a la base de datos remota exitosa.')
            return engine
        except OperationalError:
            # Si falla la conexión, muestra un warning y usa SQLite local
            logging.warning('No se pudo conectar a la base de datos remota. Usando SQLite local.')
    # Si no hay URI remota o falla, usa SQLite local
    engine = create_engine(SQLITE_URI, echo=False)
    return engine

# Obtiene el motor de conexión (remoto o local)
engine = get_engine()
# Crea una fábrica de sesiones para interactuar con la base de datos
Session = sessionmaker(bind=engine)
# Crea las tablas en la base de datos si no existen, usando el modelo Base
Base.metadata.create_all(engine)

# Función para obtener una nueva sesión de base de datos
def get_db_session():
    """
    Retorna una nueva sesión de base de datos para ser utilizada en los servicios o controladores.
    """
    return Session()
