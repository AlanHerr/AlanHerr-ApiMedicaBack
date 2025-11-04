
# Importa el modelo Product y la función para obtener una sesión de base de datos
from model.products_models import Product
from config.database import get_db_session

# Obtiene todos los productos de la base de datos
def get_all_products():
    session = get_db_session()  # Crea una nueva sesión
    products = session.query(Product).all()  # Consulta todos los productos
    session.close()  # Cierra la sesión
    return products  # Devuelve la lista de productos

# Obtiene un producto por su ID
def get_product_by_id(product_id):
    session = get_db_session()  # Crea una nueva sesión
    product = session.query(Product).filter_by(id=product_id).first()  # Busca el producto por ID
    session.close()  # Cierra la sesión
    return product  # Devuelve el producto o None

# Crea un nuevo producto en la base de datos
def create_product(data):
    session = get_db_session()  # Crea una nueva sesión
    product = Product(**data)  # Crea una instancia del modelo Product con los datos recibidos
    session.add(product)  # Agrega el producto a la sesión
    session.commit()  # Guarda los cambios en la base de datos
    session.refresh(product)  # Actualiza la instancia con los datos de la base
    session.close()  # Cierra la sesión
    return product  # Devuelve el producto creado

# Actualiza los datos de un producto existente
def update_product(product_id, data):
    session = get_db_session()  # Crea una nueva sesión
    product = session.query(Product).filter_by(id=product_id).first()  # Busca el producto por ID
    if product:
        for key, value in data.items():  # Recorre los datos recibidos
            setattr(product, key, value)  # Actualiza cada atributo del producto
        session.commit()  # Guarda los cambios
        session.refresh(product)  # Actualiza la instancia
    session.close()  # Cierra la sesión
    return product  # Devuelve el producto actualizado o None

# Elimina un producto de la base de datos
def delete_product(product_id):
    session = get_db_session()  # Crea una nueva sesión
    product = session.query(Product).filter_by(id=product_id).first()  # Busca el producto por ID
    if product:
        session.delete(product)  # Elimina el producto
        session.commit()  # Guarda los cambios
    session.close()  # Cierra la sesión
    return product  # Devuelve el producto eliminado o None