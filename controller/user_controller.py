from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from service.user_service import UserService

users_bp = Blueprint('users', __name__)

@users_bp.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    user = UserService.register_user(username, password)
    if not user:
        return jsonify({'error': 'User already exists'}), 409
    return jsonify({'message': 'User registered successfully'}), 201

@users_bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = UserService.authenticate(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token}), 200

@users_bp.route('/users/', methods=['GET'])
@jwt_required()
def list_users():
    users = UserService.list_users()
    users_list = [ {'id': u.id, 'username': u.username} for u in users ]
    return jsonify(users_list), 200
