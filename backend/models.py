from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Etudiant(Base): #On crée la classe étudiant qui hérite de base 
    __tablename__ = "etudiants"

    id = Column(Integer,primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    mdp = Column(String, unique=True)
    age = Column(Integer)
    cv = Column(String)
    lettre_motiv = Column(String)
    competences = Column(String, default="")

class Entreprise(Base): #On crée la classe entreprise qui hérite de base
    __tablename__ = "entreprises"

    id = Column(Integer,primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    mdp = Column(String,unique=True)
    offres = relationship("Offre", back_populates="entreprise")



class Offre(Base):
    __tablename__ = "offres"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)
    competences = Column(String, nullable=False)
    duree = Column(String, nullable=False)
    debut = Column(String, nullable=False)
    lieu = Column(String, nullable=False)
    entreprise_id = Column(Integer, ForeignKey("entreprises.id"))


    entreprise = relationship("Entreprise", back_populates="offres")

class Candidature(Base):
    __tablename__ = "candidatures"

    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"))
    offre_id = Column(Integer, ForeignKey("offres.id"))
    statut = Column(String, default="en attente")

    etudiant = relationship("Etudiant")
    offre = relationship("Offre")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    contenu = Column(String, nullable=False)
    expediteur_id = Column(Integer, nullable=False)
    destinataire_id = Column(Integer, nullable=False)
    expediteur_type = Column(String, nullable=False)  # "etudiant" ou "entreprise"
    destinataire_type = Column(String, nullable=False)  # "etudiant" ou "entreprise"
