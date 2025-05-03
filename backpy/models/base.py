from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# Configuração da string de conexão do banco de dados
DATABASE_URI = 'postgresql://postgres:12345678@localhost/postgres'

# Criando o motor (engine) do SQLAlchemy
engine = create_engine(DATABASE_URI, echo=True)

# Criando uma sessão que é thread-safe
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base declarativa, da qual todos os modelos herdarão
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from models.question import Question  
    from models.practice import Practice
    from models.transcription import Transcription
    Base.metadata.create_all(bind=engine)

