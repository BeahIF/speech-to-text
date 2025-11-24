from sqlalchemy import Column, ForeignKey, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, sessionmaker

import uuid

from models.question import Base


class Transcription(Base):
    __tablename__ = 'transcriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey('practice.id'), nullable=False)  # ✅ com ForeignKey
    transcription = Column(Text, nullable=False)
    resolution = Column(Text, nullable=False)
    
    # practice = relationship("Practice", backref="transcriptions")
