from sqlalchemy import Column, Integer, String, Enum
import enum
from app.db.base import Base

class UserRole(enum.Enum):
    MEDICO = "MEDICO"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

