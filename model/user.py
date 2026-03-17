
from sqlalchemy import Column, Integer, String, Boolean
from model.base import Base
import logging

logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        logger.info(f'Representación de usuario solicitada: {self.username}')
        return f'<User {self.username}>'
