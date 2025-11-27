from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base

class ProcessedImage(Base):
    __tablename__ = "processed_images"

    id = Column(Integer, primary_key=True, index=True)
    input_path = Column(String)
    output_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
