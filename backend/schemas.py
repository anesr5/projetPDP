from pydantic import BaseModel, ConfigDict #pydantic sert à structurer les données, que toutes les données soit correct     
from typing import Optional #pour pouvoir modifier juste un élément d'un étudiant ou entreprises

class ProfilEtudiantCreate(BaseModel):
    telephone: str = ""
    adresse: str = ""
    linkedin: str = ""

class ProfilEtudiantUpdate(BaseModel):
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    linkedin: Optional[str] = None

class EtudiantCreate(BaseModel): 
    email:str
    mdp:str
    age:int
    name:str
    cv:str
    lettre_motiv:str = ""
    competences:str = ""
    profil: Optional[ProfilEtudiantCreate] = None

class EntrepriseCreate(BaseModel):
    email:str
    mdp:str
    name:str

class Login(BaseModel): 
    email:str
    mdp:str

class EtudiantUpdate(BaseModel): 
    email: Optional[str] = None
    age : Optional[int] = None
    cv : Optional[str] = None
    lettre_motiv : Optional[str] = None
    name : Optional[str] = None
    mdp : Optional[str] = None
    competences : Optional[str] = None
    profil: Optional[ProfilEtudiantUpdate] = None

class EntrepriseUpdate(BaseModel):
    email: Optional[str] = None
    mdp: Optional[str] = None
    name: Optional[str] = None

class OffreCreate(BaseModel):
    titre: str
    description: str
    type: str
    competences: str
    duree: str
    debut: str
    lieu: str
    entreprise_id: int

class OffreUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    competences: Optional[str] = None
    duree: Optional[str] = None
    debut: Optional[str] = None
    lieu: Optional[str] = None
    entreprise_id: Optional[int] = None

class OffreOut(BaseModel):
    id: int
    titre: str
    description: str
    entreprise_id: int

    model_config = ConfigDict(from_attributes=True)

class CandidatureCreate(BaseModel):
    etudiant_id: int
    offre_id: int

class MessageCreate(BaseModel):
    contenu: str
    expediteur_id: int
    destinataire_id: int
    expediteur_type: str
    destinataire_type: str

class MessageResponse(BaseModel):
    id: int
    contenu: str
    expediteur_id: int
    destinataire_id: int
    expediteur_type: str
    destinataire_type: str

    model_config = ConfigDict(from_attributes=True)

class CVExtract(BaseModel):
    cv: str  # base64 data URL

class MessageEmailCreate(BaseModel):
    contenu: str
    destinataire_email: str
    expediteur_id: int
    expediteur_type: str
