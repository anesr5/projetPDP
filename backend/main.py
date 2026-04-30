from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, SessionLocal
import models
import schemas
import base64
import io
import pdfplumber


app = FastAPI(
    title="Mon API de gestion de demande de stage et d'emploi",
    description="Une API pour permettre aux étudiants de postuler aux offres de stages et aux entreprises de publier des offres.",
    version="1.0.0"
)

# Autoriser toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pendant développement : tout autoriser
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

models.Base.metadata.create_all(bind=engine)

# Migration: add competences column to etudiants if not exists
with engine.connect() as _conn:
    try:
        _conn.execute(text("ALTER TABLE etudiants ADD COLUMN competences TEXT DEFAULT ''"))
        _conn.commit()
    except Exception:
        pass  # column already exists

@app.get("/")
async def root():
    return {"message": "Mon API de gestion de demande de stage et d'emploi"}

#Créer une session avec la base de données 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.options("/inscription-etudiant")
async def preflight_inscription_etudiant(request: Request):
    return JSONResponse(content={"message": "OK"}, status_code=200)
@app.post("/inscription-etudiant")
def inscription_etudiant(etudiant: schemas.EtudiantCreate, db: Session = Depends(get_db)):
    nouveau_etudiants = models.Etudiant(
        email=etudiant.email,
        name=etudiant.name,
        mdp=etudiant.mdp,
        age=etudiant.age,
        cv=etudiant.cv,
        lettre_motiv=etudiant.lettre_motiv,
        competences=etudiant.competences
    )
    db.add(nouveau_etudiants)
    db.commit()
    db.refresh(nouveau_etudiants)
    return nouveau_etudiants

@app.post("/inscription-entreprise")
def inscription_entreprise(entreprise: schemas.EntrepriseCreate, db: Session=Depends(get_db)):
    nouvelle_entreprise = models.Entreprise(
        name = entreprise.name, 
        email = entreprise.email,
        mdp = entreprise.mdp
    )
    db.add(nouvelle_entreprise)
    db.commit()
    db.refresh(nouvelle_entreprise)
    return nouvelle_entreprise 

@app.get("/etudiants")
def list_etudiant(db: Session = Depends(get_db)):
    etudiants = db.query(models.Etudiant).all()
    return etudiants

@app.get("/entreprises")
def list_entreprises(db:Session = Depends(get_db)):
    entreprises = db.query(models.Entreprise).all()
    return entreprises

@app.post("/login_etudiant")
def connexion_etudiant(log_etudiant: schemas.Login, db: Session = Depends(get_db)):
    connexion_etudiant = db.query(models.Etudiant).filter(models.Etudiant.email==log_etudiant.email).first()
    if not connexion_etudiant:
        return {"Email invalide"}
    if connexion_etudiant.mdp != log_etudiant.mdp:
        return{"Mdp invalide"}
    
    return {
        "message": "Connexion réussie",
        "id": connexion_etudiant.id
    }

@app.post("/login_entreprises")
def connexion_entreprise(log_entreprises: schemas.Login,db:Session = Depends(get_db)):
    connexion_entreprises = db.query(models.Entreprise).filter(models.Entreprise.email==log_entreprises.email).first()
    if not connexion_entreprises:
        return {"Email invalide"}
    if connexion_entreprises.mdp != log_entreprises.mdp:
        return{"Mdp invalide"}
    return {
        "message": "Connexion réussie",
        "id": connexion_entreprises.id
    }
    

@app.get("/etudiant/{id}")
def recup_etudiant(id: int,db:Session = Depends(get_db)):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == id).first()
    if not etudiant:
        return("Etudiant non trouvé")
    
    return etudiant

@app.delete("/etudiant/{id}")
def delet_etudiant(id: int, db:Session = Depends(get_db)):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == id).first() #on recuppere l'étudiant

    if not etudiant:
        return("Cet étudiant n'existe pas")
    
    db.delete(etudiant) # on supprime l'étudiant récupérer
    db.commit()

    return ("étudiant supprimé") 

@app.put("/etudiant/{id}")
def modifier_etudiant(id: int,modif: schemas.EtudiantUpdate, db:Session=Depends(get_db)):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == id).first()

    if not etudiant:
        return("Cet étudiant n'existe pas")
    
    if modif.email is not None: #on voit si le champ de modification pour modifier ou le champ
        etudiant.email = modif.email
    if modif.mdp is not None: 
        etudiant.mdp = modif.mdp
    if modif.cv is not None:
        etudiant.cv = modif.cv
    if modif.age is not None:
        etudiant.age = modif.age
    if modif.name is not None:
        etudiant.name = modif.name
    if modif.lettre_motiv is not None:
        etudiant.lettre_motiv = modif.lettre_motiv
    if modif.competences is not None:
        etudiant.competences = modif.competences

    db.commit()
    db.refresh(etudiant)

    return etudiant

@app.get("/etudiant/{id}")
def get_etudiant(id: int, db:Session=Depends(get_db)):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == id).first()
    if not etudiant:
        return {"message : étudiant introuvable"}
    return {
        "name" : etudiant.name,   
        "email" : etudiant.email,
        "age" : etudiant.age,
        "cv" : etudiant.cv,
        "lettre_motiv": etudiant.lettre_motiv,
        "competences": etudiant.competences or ""
    }

TECH_KEYWORDS = [
    "python","javascript","java","c++","c#","typescript","php","ruby","swift","kotlin",
    "react","angular","vue","nextjs","nodejs","django","flask","fastapi","spring",
    "sql","mysql","postgresql","mongodb","redis","sqlite",
    "git","docker","kubernetes","linux","aws","azure",
    "html","css","bootstrap","tailwind",
    "machine learning","data science","nlp","tensorflow","pytorch",
    "agile","scrum","rest","api","figma","excel","word","powerpoint","photoshop"
]

@app.post("/extraire-cv")
def extraire_cv(payload: schemas.CVExtract):
    try:
        b64_data = payload.cv.split(",", 1)[1] if "," in payload.cv else payload.cv
        pdf_bytes = base64.b64decode(b64_data)
        text_content = ""
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + " "
        text_lower = text_content.lower()
        detected = [kw for kw in TECH_KEYWORDS if kw in text_lower]
        return {"competences": detected, "nb": len(detected)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur extraction PDF: {str(e)}")


@app.get("/etudiant/{id}/recommandations")
def recommander_offres(id: int, db: Session = Depends(get_db)):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    offres = db.query(models.Offre).all()
    student_skills = set(
        s.strip().lower() for s in (etudiant.competences or "").replace(',', ' ').split()
        if len(s.strip()) > 1
    )

    resultats = []
    for offre in offres:
        offer_skills = set(
            s.strip().lower() for s in offre.competences.replace(',', ' ').split()
            if len(s.strip()) > 1
        )
        if offer_skills and student_skills:
            common = student_skills.intersection(offer_skills)
            score = round(len(common) / len(offer_skills) * 100)
        else:
            score = 0
        resultats.append({
            "id": offre.id, "titre": offre.titre, "description": offre.description,
            "lieu": offre.lieu, "duree": offre.duree, "type": offre.type,
            "competences": offre.competences, "debut": offre.debut,
            "entreprise_id": offre.entreprise_id, "score": score
        })

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:5]


@app.get("/etudiant/{id}/analyse")
def analyser_profil(id: int, db: Session = Depends(get_db)):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    text_comp = (etudiant.competences or "").lower()

    TECH_KEYWORDS = [
        "python","javascript","java","c++","c#","typescript","php","ruby","swift","kotlin",
        "react","angular","vue","nextjs","nodejs","django","flask","fastapi","spring",
        "sql","mysql","postgresql","mongodb","redis","sqlite",
        "git","docker","kubernetes","linux","aws","azure",
        "html","css","bootstrap","tailwind",
        "machine learning","data science","ia","nlp","tensorflow","pytorch",
        "agile","scrum","rest","api"
    ]
    detected = [kw for kw in TECH_KEYWORDS if kw in text_comp]
    all_words = set(w.strip().lower() for w in text_comp.replace(',', ' ').split() if len(w.strip()) > 2)
    extra = [w for w in all_words if w not in TECH_KEYWORDS]

    filled = sum([
        bool(etudiant.name), bool(etudiant.email), bool(etudiant.age),
        bool(etudiant.cv and etudiant.cv.startswith("data:")),
        bool(etudiant.competences)
    ])
    profile_score = round(filled / 5 * 100)

    offres = db.query(models.Offre).all()
    student_skills = set(w.strip().lower() for w in text_comp.replace(',', ' ').split() if len(w.strip()) > 1)
    compatibilites = []
    for offre in offres:
        offer_skills = set(s.strip().lower() for s in offre.competences.replace(',', ' ').split() if len(s.strip()) > 1)
        if offer_skills and student_skills:
            common = student_skills.intersection(offer_skills)
            compatibilites.append(round(len(common) / len(offer_skills) * 100))
    avg_compat = round(sum(compatibilites) / len(compatibilites)) if compatibilites else 0

    return {
        "competences_detectees": detected,
        "mots_cles": extra[:10],
        "profile_score": profile_score,
        "compatibilite_moyenne": avg_compat,
        "nb_competences": len(detected) + len(extra)
    }


@app.get("/entreprise/{id}")
def get_entreprise(id: int, db:Session=Depends(get_db)):
    entreprise = db.query(models.Entreprise).filter(models.Entreprise.id == id).first()
    if not entreprise:
        return {"message : entreprise introuvable"}
    return {
        "name" : entreprise.name,   
        "email" : entreprise.email,
        "offres" : entreprise.offres
    }

@app.post("/offres")
def creer_offre(offre: schemas.OffreCreate, db: Session = Depends(get_db)):
    nouvelle_offre = models.Offre(
        titre=offre.titre,
        description=offre.description,
        type=offre.type,
        competences=offre.competences,
        duree=offre.duree,
        debut=offre.debut,
        lieu=offre.lieu,
        entreprise_id=offre.entreprise_id
    )
    db.add(nouvelle_offre)
    db.commit()
    db.refresh(nouvelle_offre)
    return nouvelle_offre

@app.get("/offres")
def lire_offres(db: Session = Depends(get_db)):
    return db.query(models.Offre).all()

@app.delete("/offres/{id}")
def supprimer_offre(id: int, db: Session = Depends(get_db)):
    offre = db.query(models.Offre).filter(models.Offre.id == id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre introuvable")
    db.delete(offre)
    db.commit()
    return {"message": "Offre supprimée"}

@app.post("/postuler")
def postuler(candidature: schemas.CandidatureCreate, db: Session = Depends(get_db)):
    
    existing = db.query(models.Candidature).filter(
        models.Candidature.etudiant_id == candidature.etudiant_id,
        models.Candidature.offre_id == candidature.offre_id
    ).first()

    if existing:
        return {"message": "Vous avez déjà postulé à cette offre."}
    
    nouvelle_candidature = models.Candidature(
        etudiant_id=candidature.etudiant_id,
        offre_id=candidature.offre_id
    )
    db.add(nouvelle_candidature)
    db.commit()
    db.refresh(nouvelle_candidature)
    return {"message": "Candidature envoyée avec succès !"}

@app.get("/candidatures/{etudiant_id}")
def voir_candidatures(etudiant_id: int, db: Session = Depends(get_db)):
    candidatures = db.query(models.Candidature).filter(models.Candidature.etudiant_id == etudiant_id).all()

    resultats = []
    for c in candidatures:
        offre = db.query(models.Offre).filter(models.Offre.id == c.offre_id).first()
        if offre:
            resultats.append({
                "titre": offre.titre,
                "description": offre.description,
                "lieu": offre.lieu,
                "debut": offre.debut,
                "statut": c.statut  
            })

    return resultats

@app.get("/entreprise/{entreprise_id}/candidatures")
def voir_candidatures_reçues(entreprise_id: int, db: Session = Depends(get_db)):
    offres = db.query(models.Offre).filter(models.Offre.entreprise_id == entreprise_id).all()
    resultats = []

    for offre in offres:
        candidatures = db.query(models.Candidature).filter(models.Candidature.offre_id == offre.id).all()
        for c in candidatures:
            etu = db.query(models.Etudiant).filter(models.Etudiant.id == c.etudiant_id).first()
            if etu:
                resultats.append({
                    "id": c.id,
                    "offre_titre": offre.titre,
                    "etudiant_nom": etu.name,
                    "etudiant_email": etu.email,
                    "etudiant_cv": etu.cv,
                    "etudiant_lettre": etu.lettre_motiv,
                    "statut": c.statut
                })

    return resultats


@app.put("/candidature/{id}/statut")
def modifier_statut_candidature(id: int, nouveau_statut: str, db: Session = Depends(get_db)):
    candidature = db.query(models.Candidature).filter(models.Candidature.id == id).first()

    if not candidature:
        raise HTTPException(status_code=404, detail="Candidature non trouvée")

    if nouveau_statut.lower() not in ["acceptée", "refusée", "en attente"]:
        raise HTTPException(status_code=400, detail="Statut invalide")

    candidature.statut = nouveau_statut.lower()
    db.commit()
    db.refresh(candidature)

    return {"message": f"Statut mis à jour vers '{candidature.statut}'"}

@app.post("/messages")
def envoyer_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    msg = models.Message(**message.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@app.get("/messages/{user_id}")
def recevoir_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.destinataire_id == user_id).all()

    resultats = []
    for m in messages:
        # Récupérer l'expéditeur
        if m.expediteur_type == "etudiant":
            expediteur = db.query(models.Etudiant).filter_by(id=m.expediteur_id).first()
        else:
            expediteur = db.query(models.Entreprise).filter_by(id=m.expediteur_id).first()
        
        # Récupérer le destinataire
        if m.destinataire_type == "etudiant":
            destinataire = db.query(models.Etudiant).filter_by(id=m.destinataire_id).first()
        else:
            destinataire = db.query(models.Entreprise).filter_by(id=m.destinataire_id).first()

        resultats.append({
            "contenu": m.contenu,
            "expediteur": expediteur.email if expediteur else "inconnu",
            "destinataire": destinataire.email if destinataire else "inconnu"
        })

    return resultats




@app.post("/message/email")
def envoyer_message_par_email(data: schemas.MessageEmailCreate, db: Session = Depends(get_db)):
    # Chercher le destinataire par email
    destinataire = (
        db.query(models.Etudiant).filter(models.Etudiant.email == data.destinataire_email).first() or
        db.query(models.Entreprise).filter(models.Entreprise.email == data.destinataire_email).first()
    )

    if not destinataire:
        return {"message": "Destinataire introuvable"}

    nouveau_message = models.Message(
        contenu=data.contenu,
        expediteur_id=data.expediteur_id,
        expediteur_type=data.expediteur_type,
        destinataire_id=destinataire.id,
        destinataire_type="etudiant" if isinstance(destinataire, models.Etudiant) else "entreprise"
    )
    db.add(nouveau_message)
    db.commit()
    db.refresh(nouveau_message)

    return {"message": "Message envoyé avec succès"}
