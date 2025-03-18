from sqlalchemy import create_engine, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

from models.base import Base


class Question(Base):
    __tablename__ = 'questions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    audioTranscription = Column(String)  # Campo opcional para transcrição de áudio

    # Relação OneToMany com PracticeEntity, assumindo que você também traduzirá essa entidade
    practices = relationship("Practice", back_populates="question")
