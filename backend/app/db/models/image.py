import enum

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class ExamType(enum.Enum):
    MAMOGRAFIA = "MAMOGRAFIA"
    ECOGRAFIA = "ECOGRAFIA"
    OTRO = "OTRO"


class Image(Base):
    __tablename__ = "images"
    __table_args__ = (CheckConstraint("laterality IN ('L','R')", name="ck_images_laterality"),)

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)  # nombre original informado por el cliente
    filepath = Column(String, nullable=False)  # clave en el StorageBackend
    mime_type = Column(String, nullable=False)

    width = Column(Integer)
    height = Column(Integer)
    size_kb = Column(Integer)

    exam_type = Column(
        Enum(ExamType, name="examtype"),
        nullable=False,
        server_default=ExamType.MAMOGRAFIA.value,
        default=ExamType.MAMOGRAFIA,
    )
    laterality = Column(String(1), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    sha256 = Column(String(64), nullable=True)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    case = relationship("Case", back_populates="images")
    inference_result = relationship("InferenceResult", back_populates="image", uselist=False)
