from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)

from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (CheckConstraint("sex IN ('F','M','O')", name="ck_patients_sex"),)

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    sex = Column(String(1), nullable=True)
    medical_history = Column(Text, nullable=True)
    family_history_first_degree = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    previous_breast_cancer = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    consent_given = Column(Boolean, nullable=False, server_default=text("false"), default=False)
    consent_at = Column(DateTime(timezone=True), nullable=True)
    consent_registered_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
