from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from database import Base
from sqlalchemy.orm import relationship

class Etudiant(Base): #On crée la classe étudiant qui hérite de base 
    __tablename__ = "etudiants"

    id = Column(Integer,primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    mdp = Column(String)
    age = Column(Integer)
    cv = Column(String)
    lettre_motiv = Column(String)
    competences = Column(String, default="")
    profil = relationship(
        "ProfilEtudiant",
        back_populates="etudiant",
        uselist=False,
        cascade="all, delete-orphan",
    )
    candidatures = relationship(
        "Candidature",
        back_populates="etudiant",
        cascade="all, delete-orphan",
    )
    offres = relationship(
        "Offre",
        secondary="candidatures",
        viewonly=True,
        back_populates="etudiants",
    )

class ProfilEtudiant(Base):
    __tablename__ = "profils_etudiants"

    id = Column(Integer, primary_key=True, index=True)
    telephone = Column(String, default="")
    adresse = Column(String, default="")
    linkedin = Column(String, default="")
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), unique=True, nullable=False)

    etudiant = relationship("Etudiant", back_populates="profil")

class Entreprise(Base): #On crée la classe entreprise qui hérite de base
    __tablename__ = "entreprises"

    id = Column(Integer,primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    mdp = Column(String)
    offres = relationship("Offre", back_populates="entreprise", cascade="all, delete-orphan")



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
    entreprise_id = Column(Integer, ForeignKey("entreprises.id"), nullable=False)


    entreprise = relationship("Entreprise", back_populates="offres")
    candidatures = relationship(
        "Candidature",
        back_populates="offre",
        cascade="all, delete-orphan",
    )
    etudiants = relationship(
        "Etudiant",
        secondary="candidatures",
        viewonly=True,
        back_populates="offres",
    )

class Candidature(Base):
    __tablename__ = "candidatures"
    __table_args__ = (
        UniqueConstraint("etudiant_id", "offre_id", name="uq_candidature_etudiant_offre"),
    )

    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    offre_id = Column(Integer, ForeignKey("offres.id"), nullable=False)
    statut = Column(String, default="en attente")

    etudiant = relationship("Etudiant", back_populates="candidatures")
    offre = relationship("Offre", back_populates="candidatures")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    contenu = Column(String, nullable=False)
    expediteur_id = Column(Integer, nullable=False)
    destinataire_id = Column(Integer, nullable=False)
    expediteur_type = Column(String, nullable=False)  # "etudiant" ou "entreprise"
    destinataire_type = Column(String, nullable=False)  # "etudiant" ou "entreprise"
