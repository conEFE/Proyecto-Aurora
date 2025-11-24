from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)

    width = Column(Integer)
    height = Column(Integer)
    size_kb = Column(Integer)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    case = relationship("Case", back_populates="images")
    
    # Relación con resultado de inferencia
    inference_result = relationship("InferenceResult", back_populates="image", uselist=False)
