# Importa herramientas de Flask para crear rutas y manejar peticiones/respuestas JSON
from flask import Blueprint, jsonify, request

# Importa funciones del servicio de productos para la lógica de negocio

from service.products_service import (
    list_products,
    get_product,
    add_product,
    modify_product,
    remove_product
)
from flask_jwt_extended import jwt_required

# Crea un blueprint para agrupar las rutas relacionadas con productos
products_bp = Blueprint('products', __name__)

# Endpoint para obtener todos los productos
@products_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    # Llama al servicio para obtener la lista de productos
    products = list_products()
    # Convierte cada producto a diccionario
    products_list = [p.__dict__ for p in products]
    # Elimina la clave interna de SQLAlchemy
    for p in products_list:
        p.pop('_sa_instance_state', None)
    # Devuelve la lista como JSON y código 200
    return jsonify(products_list), 200

# Endpoint para obtener un producto por ID
@products_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product_route(product_id):
    # Llama al servicio para obtener el producto por ID
    product = get_product(product_id)
    # Si no existe, responde con error 404
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    # Convierte el producto a diccionario y elimina clave interna
    prod_dict = product.__dict__
    prod_dict.pop('_sa_instance_state', None)
    # Devuelve el producto como JSON y código 200
    return jsonify(prod_dict), 200

# Endpoint para crear un nuevo producto
@products_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product_route():
    # Obtiene los datos enviados por el cliente
    data = request.json
    # Valida que estén todos los campos requeridos
    if not data or not all(k in data for k in ('name', 'category', 'price', 'quantity')):
        return jsonify({'error': 'Bad request'}), 400
    # Llama al servicio para crear el producto
    product = add_product(data)
    # Convierte el producto a diccionario y elimina clave interna
    prod_dict = product.__dict__
    prod_dict.pop('_sa_instance_state', None)
    # Devuelve el producto creado como JSON y código 201
    return jsonify(prod_dict), 201

# Endpoint para actualizar un producto existente
@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product_route(product_id):
    # Obtiene los datos enviados por el cliente
    data = request.json
    # Valida que haya datos
    if not data:
        return jsonify({'error': 'Bad request'}), 400
    # Llama al servicio para actualizar el producto
    product = modify_product(product_id, data)
    # Si no existe, responde con error 404
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    # Convierte el producto actualizado a diccionario y elimina clave interna
    prod_dict = product.__dict__
    prod_dict.pop('_sa_instance_state', None)
    # Devuelve el producto actualizado como JSON y código 200
    return jsonify(prod_dict), 200

# Endpoint para eliminar un producto
@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product_route(product_id):
    # Llama al servicio para eliminar el producto
    product = remove_product(product_id)
    # Si no existe, responde con error 404
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    # Devuelve mensaje de éxito como JSON y código 200
    return jsonify({'result': 'Product deleted'}), 200