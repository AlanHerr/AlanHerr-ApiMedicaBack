from config.database import engine
from model.base import Base

# IMPORTAR MODELOS
from model.user_model import User
from model.model_metadata import ModelMetadata

# Crear tablas
Base.metadata.create_all(bind=engine)

print("Database tables created successfully")