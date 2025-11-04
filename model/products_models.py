
# Importa los tipos de columna y datos para definir la estructura de la tabla
from sqlalchemy import Column, Integer, String, Float
# Importa la función para crear la clase base de los modelos
from sqlalchemy.ext.declarative import declarative_base

# Crea la clase base para todos los modelos de la base de datos
Base = declarative_base()

# Define el modelo Product que representa la tabla 'products' en la base de datos
class Product(Base):
    __tablename__ = 'products'  # Nombre de la tabla en la base de datos
    id = Column(Integer, primary_key=True)  # Columna id, clave primaria
    name = Column(String(100), nullable=False)  # Columna name, cadena de hasta 100 caracteres, no nula
    category = Column(String(50), nullable=False)  # Columna category, cadena de hasta 50 caracteres, no nula
    price = Column(Float, nullable=False)  # Columna price, tipo flotante, no nula
    quantity = Column(Integer, nullable=False)  # Columna quantity, tipo entero, no nula