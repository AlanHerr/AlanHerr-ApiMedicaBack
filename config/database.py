import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from model.base import Base
from model.user import User  # Importante para que Base los reconozca
from model.model_metadata import ModelMetadata 
from dotenv import load_dotenv

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URL')
SQLITE_URI = 'sqlite:///medical_local.db'

def get_engine():
    """
    Crea el motor de base de datos priorizando la remota con driver psycopg.
    """
    if DATABASE_URI:
        try:
            uri = DATABASE_URI
            # Normalización para Railway y SQLAlchemy + Psycopg3
            if uri.startswith('postgres://'):
                uri = uri.replace('postgres://', 'postgresql+psycopg://', 1)
            elif uri.startswith('postgresql://') and '+psycopg' not in uri:
                uri = uri.replace('postgresql://', 'postgresql+psycopg://', 1)

            engine = create_engine(uri, echo=False, pool_pre_ping=True)
            
            # Prueba de conexión rápida
            with engine.connect() as conn:
                logger.info("✅ Conexión a PostgreSQL en Railway exitosa.")
            return engine
        except Exception as e:
            logger.warning(f"⚠️ Fallo conexión remota: {e}. Usando SQLite local.")
    
    return create_engine(SQLITE_URI, echo=False)

# Inicialización global
engine = get_engine()
Session = sessionmaker(bind=engine)

def init_db():
    """
    Crea las tablas basándose en los modelos importados.
    Se llama desde app.py para asegurar el orden de ejecución.
    """
    try:
        # Esto busca todo lo que herede de Base (User, ModelMetadata, etc.)
        Base.metadata.create_all(engine)
        logger.info("🚀 Tablas verificadas y creadas correctamente.")
    except Exception as e:
        logger.error(f"❌ Error crítico al crear tablas: {e}")

def get_db_session():
    return Session()