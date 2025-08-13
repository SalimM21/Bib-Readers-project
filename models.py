# models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Adherent(Base):
    __tablename__ = "adherents"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(20), default="adherent")
    date_inscription = Column(DateTime, default=datetime.utcnow)

    # Relation : un adhérent peut avoir plusieurs emprunts et réservations
    emprunts = relationship("Emprunt", back_populates="adherent")
    reservations = relationship("Reservation", back_populates="adherent")

class Emprunt(Base):
    __tablename__ = "emprunts"
    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id"))
    id_livre = Column(Integer, ForeignKey("livres.id"))
    date_emprunt = Column(Date, default=datetime.utcnow)
    date_retour_prevue = Column(Date)
    date_retour_effectif = Column(Date, nullable=True)

    adherent = relationship("Adherent", back_populates="emprunts")
    livre = relationship("Livre", back_populates="emprunts")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id"))
    id_livre = Column(Integer, ForeignKey("livres.id"))
    date_reservation = Column(Date, default=datetime.utcnow)
    statut = Column(String(50))

    adherent = relationship("Adherent", back_populates="reservations")
    livre = relationship("Livre", back_populates="reservations")

class HistoriqueEmprunt(Base):
    __tablename__ = "historique_emprunts"
    id_adherent = Column(Integer, ForeignKey("adherents.id"), primary_key=True)
    id_livre = Column(Integer, ForeignKey("livres.id"), primary_key=True)
    note = Column(Integer)
    date_emprunt = Column(Date)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id"))
    message = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    lu = Column(Boolean, default=False)
