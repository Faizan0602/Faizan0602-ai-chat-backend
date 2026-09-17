from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    file_type = Column(String)
    size_bytes = Column(Integer)
    status = Column(String, default="uploaded")   # uploaded -> processing -> ready -> failed
    uploaded_at = Column(DateTime, server_default=func.now())