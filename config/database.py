
# Importa módulos necesarios para la configuración y conexión a la base de datos
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from model.base import Base
from model.user import User
from model.model_metadata import ModelMetadata
from dotenv import load_dotenv

# Configura el nivel de logging para mostrar mensajes informativos
logging.basicConfig(level=logging.INFO)

# Carga variables de entorno desde el archivo .env
load_dotenv()

# Obtiene la URI de la base de datos remota desde variables comunes
# Prioriza DATABASE_URL (Railway/Heroku) y mantiene compatibilidad con MYSQL_URI
DATABASE_URI = os.getenv('DATABASE_URL') or os.getenv('MYSQL_URI')
# Define la URI para la base de datos local SQLite como respaldo
SQLITE_URI = 'sqlite:///medical_local.db'

# Función para obtener el motor de conexión a la base de datos
def get_engine():
    """
    Intenta crear una conexión con la base de datos remota. Si falla, usa SQLite local.
    """
    if DATABASE_URI:
        try:
            # Normaliza driver de Postgres a psycopg (psycopg3)
            uri = DATABASE_URI
            if uri.startswith('postgres://'):
                uri = uri.replace('postgres://', 'postgresql+psycopg://', 1)
            elif uri.startswith('postgresql://') and '+psycopg' not in uri and '+psycopg2' not in uri:
                uri = uri.replace('postgresql://', 'postgresql+psycopg://', 1)

            # Crea el motor de conexión usando la URI remota
            engine = create_engine(uri, echo=False, pool_pre_ping=True)

            # Probar conexión abriendo y cerrando una conexión (solo en proceso principal del reloader)
            try:
                conn = engine.connect()
                conn.close()
                # Evita doble log con el reloader de Flask
                if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or 'WERKZEUG_RUN_MAIN' not in os.environ:
                    logging.info('Conexión a la base de datos remota exitosa.')
            except OperationalError:
                raise
            return engine
        except OperationalError:
            # Si falla la conexión, muestra un warning y usa SQLite local
            logging.warning('No se pudo conectar a la base de datos remota. Usando SQLite local.')
        except Exception as e:
            # Cubre errores de importación del driver u otros problemas de creación del engine
            logging.warning(f'Fallo al inicializar el motor de BD remoto ({type(e).__name__}): {e}. Usando SQLite local.')
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
