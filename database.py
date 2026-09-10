from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "foerderungen.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Foerderung(Base):
    __tablename__ = "foerderungen"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    beschreibung = Column(Text, nullable=True)
    massnahme = Column(String, nullable=False)
    gebaeudetyp = Column(String, nullable=False)
    max_foerderung = Column(Float, nullable=True)
    zuschuss = Column(String, nullable=True)
    details = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)