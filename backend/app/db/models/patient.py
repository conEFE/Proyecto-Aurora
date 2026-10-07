from sqlalchemy import Column, Date, DateTime, Integer, String, Text, func

from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    sex = Column(String, nullable=True)  # 'M', 'F', 'O'
    medical_history = Column(Text, nullable=True)  # Ficha médica/historial
    created_at = Column(DateTime(timezone=True), server_default=func.now())
