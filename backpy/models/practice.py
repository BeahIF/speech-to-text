from sqlalchemy import Column, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

from models.base import Base
class Practice(Base):
    __tablename__ = 'practice'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution = Column(Text, nullable=False)
    data = Column(Date, nullable=False)
    feedback = Column(Text, nullable=True)
    status = Column(String(20), nullable=True)
    language = Column(String(50), nullable=False)

    transcriptions = relationship('Transcription', backref='practice', lazy=True)

    questionId = Column(UUID(as_uuid=True), ForeignKey('questions.id'))
    question = relationship("Question", back_populates="practices")

