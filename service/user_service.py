from repository.user_repository import UserRepository
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    @staticmethod
    def register_user(username, password):
        if UserRepository.get_by_username(username):
            return None  # Usuario ya existe
        hashed_password = generate_password_hash(password)
        user = UserRepository.create_user(username, hashed_password)
        return user

    @staticmethod
    def authenticate(username, password):
        user = UserRepository.get_by_username(username)
        if user and check_password_hash(user.password, password):
            return user
        return None

    @staticmethod
    def list_users():
        return UserRepository.get_all()
