from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos
DATABASE_URL = "sqlite:///./reservas.db"  

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Clase base para modelos ORM
Base = declarative_base()

# Sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)