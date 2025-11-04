
# Importa las funciones CRUD del repositorio de productos
from repository.products_repository import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)

# Servicio para listar todos los productos
def list_products():
    return get_all_products()  # Llama al repositorio para obtener todos los productos

# Servicio para obtener un producto por su ID
def get_product(product_id):
    return get_product_by_id(product_id)  # Llama al repositorio para obtener el producto por ID

# Servicio para agregar un nuevo producto
def add_product(data):
    return create_product(data)  # Llama al repositorio para crear el producto

# Servicio para modificar un producto existente
def modify_product(product_id, data):
    return update_product(product_id, data)  # Llama al repositorio para actualizar el producto

# Servicio para eliminar un producto
def remove_product(product_id):
    return delete_product(product_id)  # Llama al repositorio para eliminar el producto