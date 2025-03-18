from sqlalchemy import Column, Text, String
from sqlalchemy.dialects.postgresql import UUID
import uuid

from models.question import Base


class Transcription(Base):
    __tablename__ = 'transcriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mock_code = Column(String, nullable=False)
    transcription = Column(Text, nullable=False)
    resolution = Column(Text, nullable=False)