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

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

class Anfrage(Base):
    __tablename__ = "anfragen"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefon = Column(String, nullable=True)
    massnahme = Column(String, nullable=False)
    gebaeudetyp = Column(String, nullable=False)
    baujahr = Column(Integer, nullable=True)
    ergebnis = Column(Text, nullable=True)
    erstellt_am = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)