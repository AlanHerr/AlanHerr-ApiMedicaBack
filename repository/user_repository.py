from model.user import User
from config.database import get_db_session

class UserRepository:
    @staticmethod
    def get_by_username(username):
        session = get_db_session()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        return user

    @staticmethod
    def create_user(username, hashed_password):
        session = get_db_session()
        user = User(username=username, password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()
        return user

    @staticmethod
    def get_all():
        session = get_db_session()
        users = session.query(User).all()
        session.close()
        return users
