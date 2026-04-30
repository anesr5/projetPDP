import base64
import io

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


app = FastAPI(
    title="API Genie Log - stages et emplois",
    description="API REST pour des etudiants qui postulent a des offres publiees par des entreprises.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


TECH_KEYWORDS = [
    "python", "javascript", "java", "c++", "c#", "typescript", "php", "ruby", "swift", "kotlin",
    "react", "angular", "vue", "nextjs", "nodejs", "django", "flask", "fastapi", "spring",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "git", "docker", "kubernetes", "linux", "aws", "azure",
    "html", "css", "bootstrap", "tailwind",
    "machine learning", "data science", "ia", "nlp", "tensorflow", "pytorch",
    "agile", "scrum", "rest", "api", "figma", "excel", "word", "powerpoint", "photoshop",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def model_data(model, **kwargs):
    if hasattr(model, "model_dump"):
        return model.model_dump(**kwargs)
    return model.dict(**kwargs)


def commit_or_400(db: Session, message: str = "Donnees invalides ou deja existantes"):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc


def get_etudiant_or_404(db: Session, etudiant_id: int):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Etudiant introuvable")
    return etudiant


def get_entreprise_or_404(db: Session, entreprise_id: int):
    entreprise = db.query(models.Entreprise).filter(models.Entreprise.id == entreprise_id).first()
    if not entreprise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise introuvable")
    return entreprise


def get_offre_or_404(db: Session, offre_id: int):
    offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offre introuvable")
    return offre


def serialize_profil(profil):
    if not profil:
        return None
    return {
        "id": profil.id,
        "telephone": profil.telephone,
        "adresse": profil.adresse,
        "linkedin": profil.linkedin,
        "etudiant_id": profil.etudiant_id,
    }


def serialize_etudiant(etudiant):
    return {
        "id": etudiant.id,
        "name": etudiant.name,
        "email": etudiant.email,
        "age": etudiant.age,
        "cv": etudiant.cv,
        "lettre_motiv": etudiant.lettre_motiv,
        "competences": etudiant.competences or "",
        "profil": serialize_profil(etudiant.profil),
    }


def serialize_entreprise(entreprise, include_offres=False):
    data = {
        "id": entreprise.id,
        "name": entreprise.name,
        "email": entreprise.email,
    }
    if include_offres:
        data["offres"] = [serialize_offre(offre) for offre in entreprise.offres]
    return data


def serialize_offre(offre):
    return {
        "id": offre.id,
        "titre": offre.titre,
        "description": offre.description,
        "type": offre.type,
        "competences": offre.competences,
        "duree": offre.duree,
        "debut": offre.debut,
        "lieu": offre.lieu,
        "entreprise_id": offre.entreprise_id,
    }


@app.get("/")
async def root():
    return {
        "message": "API Genie Log - gestion de demandes de stage et d'emploi",
        "docs": "/docs",
    }


@app.options("/inscription-etudiant")
async def preflight_inscription_etudiant(request: Request):
    return JSONResponse(content={"message": "OK"}, status_code=status.HTTP_200_OK)


@app.post("/etudiants", status_code=status.HTTP_201_CREATED)
@app.post("/inscription-etudiant", status_code=status.HTTP_201_CREATED)
def creer_etudiant(etudiant: schemas.EtudiantCreate, db: Session = Depends(get_db)):
    profil_data = model_data(etudiant.profil) if etudiant.profil else {}
    etudiant_data = model_data(etudiant, exclude={"profil"})
    nouveau_etudiant = models.Etudiant(**etudiant_data)
    nouveau_etudiant.profil = models.ProfilEtudiant(**profil_data)
    db.add(nouveau_etudiant)
    commit_or_400(db, "Email etudiant deja utilise")
    db.refresh(nouveau_etudiant)
    return serialize_etudiant(nouveau_etudiant)


@app.get("/etudiants")
def lister_etudiants(db: Session = Depends(get_db)):
    return [serialize_etudiant(etudiant) for etudiant in db.query(models.Etudiant).all()]


@app.get("/etudiants/{id}")
@app.get("/etudiant/{id}")
def lire_etudiant(id: int, db: Session = Depends(get_db)):
    return serialize_etudiant(get_etudiant_or_404(db, id))


@app.put("/etudiants/{id}")
@app.patch("/etudiants/{id}")
@app.put("/etudiant/{id}")
@app.patch("/etudiant/{id}")
def modifier_etudiant(id: int, modif: schemas.EtudiantUpdate, db: Session = Depends(get_db)):
    etudiant = get_etudiant_or_404(db, id)
    data = model_data(modif, exclude_unset=True)
    profil_data = data.pop("profil", None)

    for champ, valeur in data.items():
        setattr(etudiant, champ, valeur)

    if profil_data is not None:
        if not etudiant.profil:
            etudiant.profil = models.ProfilEtudiant()
        for champ, valeur in profil_data.items():
            setattr(etudiant.profil, champ, valeur)

    commit_or_400(db, "Modification etudiant invalide")
    db.refresh(etudiant)
    return serialize_etudiant(etudiant)


@app.delete("/etudiants/{id}")
@app.delete("/etudiant/{id}")
def supprimer_etudiant(id: int, db: Session = Depends(get_db)):
    etudiant = get_etudiant_or_404(db, id)
    db.delete(etudiant)
    db.commit()
    return {"message": "Etudiant supprime"}


@app.get("/etudiants/{id}/profil")
def lire_profil_etudiant(id: int, db: Session = Depends(get_db)):
    return serialize_profil(get_etudiant_or_404(db, id).profil)


@app.put("/etudiants/{id}/profil")
@app.patch("/etudiants/{id}/profil")
def modifier_profil_etudiant(id: int, modif: schemas.ProfilEtudiantUpdate, db: Session = Depends(get_db)):
    etudiant = get_etudiant_or_404(db, id)
    if not etudiant.profil:
        etudiant.profil = models.ProfilEtudiant()
    for champ, valeur in model_data(modif, exclude_unset=True).items():
        setattr(etudiant.profil, champ, valeur)
    commit_or_400(db, "Modification profil invalide")
    db.refresh(etudiant)
    return serialize_profil(etudiant.profil)


@app.post("/entreprises", status_code=status.HTTP_201_CREATED)
@app.post("/inscription-entreprise", status_code=status.HTTP_201_CREATED)
def creer_entreprise(entreprise: schemas.EntrepriseCreate, db: Session = Depends(get_db)):
    nouvelle_entreprise = models.Entreprise(**model_data(entreprise))
    db.add(nouvelle_entreprise)
    commit_or_400(db, "Email ou nom entreprise deja utilise")
    db.refresh(nouvelle_entreprise)
    return serialize_entreprise(nouvelle_entreprise)


@app.get("/entreprises")
def lister_entreprises(db: Session = Depends(get_db)):
    return [serialize_entreprise(entreprise) for entreprise in db.query(models.Entreprise).all()]


@app.get("/entreprises/{id}")
@app.get("/entreprise/{id}")
def lire_entreprise(id: int, db: Session = Depends(get_db)):
    return serialize_entreprise(get_entreprise_or_404(db, id), include_offres=True)


@app.put("/entreprises/{id}")
@app.patch("/entreprises/{id}")
def modifier_entreprise(id: int, modif: schemas.EntrepriseUpdate, db: Session = Depends(get_db)):
    entreprise = get_entreprise_or_404(db, id)
    for champ, valeur in model_data(modif, exclude_unset=True).items():
        setattr(entreprise, champ, valeur)
    commit_or_400(db, "Modification entreprise invalide")
    db.refresh(entreprise)
    return serialize_entreprise(entreprise)


@app.delete("/entreprises/{id}")
def supprimer_entreprise(id: int, db: Session = Depends(get_db)):
    entreprise = get_entreprise_or_404(db, id)
    db.delete(entreprise)
    db.commit()
    return {"message": "Entreprise supprimee"}


@app.post("/auth/etudiants/login")
@app.post("/login_etudiant")
def connecter_etudiant(login: schemas.Login, db: Session = Depends(get_db)):
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.email == login.email).first()
    if not etudiant or etudiant.mdp != login.mdp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    return {"message": "Connexion reussie", "id": etudiant.id}


@app.post("/auth/entreprises/login")
@app.post("/login_entreprises")
def connecter_entreprise(login: schemas.Login, db: Session = Depends(get_db)):
    entreprise = db.query(models.Entreprise).filter(models.Entreprise.email == login.email).first()
    if not entreprise or entreprise.mdp != login.mdp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    return {"message": "Connexion reussie", "id": entreprise.id}


@app.post("/extraire-cv")
def extraire_cv(payload: schemas.CVExtract):
    if pdfplumber is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La dependance pdfplumber n est pas installee",
        )
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
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Erreur extraction PDF: {exc}") from exc


@app.post("/offres", status_code=status.HTTP_201_CREATED)
def creer_offre(offre: schemas.OffreCreate, db: Session = Depends(get_db)):
    get_entreprise_or_404(db, offre.entreprise_id)
    nouvelle_offre = models.Offre(**model_data(offre))
    db.add(nouvelle_offre)
    commit_or_400(db, "Creation offre invalide")
    db.refresh(nouvelle_offre)
    return serialize_offre(nouvelle_offre)


@app.get("/offres")
def lister_offres(db: Session = Depends(get_db)):
    return [serialize_offre(offre) for offre in db.query(models.Offre).all()]


@app.get("/offres/{id}")
def lire_offre(id: int, db: Session = Depends(get_db)):
    return serialize_offre(get_offre_or_404(db, id))


@app.put("/offres/{id}")
@app.patch("/offres/{id}")
def modifier_offre(id: int, modif: schemas.OffreUpdate, db: Session = Depends(get_db)):
    offre = get_offre_or_404(db, id)
    data = model_data(modif, exclude_unset=True)
    if "entreprise_id" in data:
        get_entreprise_or_404(db, data["entreprise_id"])
    for champ, valeur in data.items():
        setattr(offre, champ, valeur)
    commit_or_400(db, "Modification offre invalide")
    db.refresh(offre)
    return serialize_offre(offre)


@app.delete("/offres/{id}")
def supprimer_offre(id: int, db: Session = Depends(get_db)):
    offre = get_offre_or_404(db, id)
    db.delete(offre)
    db.commit()
    return {"message": "Offre supprimee"}


@app.post("/candidatures", status_code=status.HTTP_201_CREATED)
@app.post("/postuler", status_code=status.HTTP_201_CREATED)
def creer_candidature(candidature: schemas.CandidatureCreate, db: Session = Depends(get_db)):
    get_etudiant_or_404(db, candidature.etudiant_id)
    get_offre_or_404(db, candidature.offre_id)
    existing = db.query(models.Candidature).filter(
        models.Candidature.etudiant_id == candidature.etudiant_id,
        models.Candidature.offre_id == candidature.offre_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Candidature deja existante")

    nouvelle_candidature = models.Candidature(**model_data(candidature))
    db.add(nouvelle_candidature)
    commit_or_400(db, "Creation candidature invalide")
    db.refresh(nouvelle_candidature)
    return {
        "message": "Candidature envoyee avec succes",
        "id": nouvelle_candidature.id,
        "statut": nouvelle_candidature.statut,
    }


@app.get("/etudiants/{id}/candidatures")
@app.get("/candidatures/{id}")
def lister_candidatures_etudiant(id: int, db: Session = Depends(get_db)):
    get_etudiant_or_404(db, id)
    candidatures = db.query(models.Candidature).filter(models.Candidature.etudiant_id == id).all()
    return [
        {
            "id": c.id,
            "offre_id": c.offre_id,
            "titre": c.offre.titre,
            "description": c.offre.description,
            "lieu": c.offre.lieu,
            "debut": c.offre.debut,
            "statut": c.statut,
        }
        for c in candidatures
    ]


@app.get("/entreprises/{id}/candidatures")
@app.get("/entreprise/{id}/candidatures")
def lister_candidatures_entreprise(id: int, db: Session = Depends(get_db)):
    get_entreprise_or_404(db, id)
    candidatures = (
        db.query(models.Candidature)
        .join(models.Offre)
        .filter(models.Offre.entreprise_id == id)
        .all()
    )
    return [
        {
            "id": c.id,
            "offre_id": c.offre_id,
            "offre_titre": c.offre.titre,
            "etudiant_id": c.etudiant_id,
            "etudiant_nom": c.etudiant.name,
            "etudiant_email": c.etudiant.email,
            "etudiant_cv": c.etudiant.cv,
            "etudiant_lettre": c.etudiant.lettre_motiv,
            "statut": c.statut,
        }
        for c in candidatures
    ]


@app.put("/candidatures/{id}/statut")
@app.patch("/candidatures/{id}/statut")
@app.put("/candidature/{id}/statut")
def modifier_statut_candidature(id: int, nouveau_statut: str, db: Session = Depends(get_db)):
    candidature = db.query(models.Candidature).filter(models.Candidature.id == id).first()
    if not candidature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidature introuvable")
    if nouveau_statut.lower() not in ["acceptee", "acceptée", "refusee", "refusée", "en attente"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Statut invalide")
    candidature.statut = nouveau_statut.lower()
    db.commit()
    db.refresh(candidature)
    return {"message": f"Statut mis a jour vers '{candidature.statut}'"}


@app.delete("/candidatures/{id}")
def supprimer_candidature(id: int, db: Session = Depends(get_db)):
    candidature = db.query(models.Candidature).filter(models.Candidature.id == id).first()
    if not candidature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidature introuvable")
    db.delete(candidature)
    db.commit()
    return {"message": "Candidature supprimee"}


@app.get("/etudiants/{id}/recommandations")
@app.get("/etudiant/{id}/recommandations")
def recommander_offres(id: int, db: Session = Depends(get_db)):
    etudiant = get_etudiant_or_404(db, id)
    offres = db.query(models.Offre).all()
    student_skills = {
        s.strip().lower()
        for s in (etudiant.competences or "").replace(",", " ").split()
        if len(s.strip()) > 1
    }

    resultats = []
    for offre in offres:
        offer_skills = {
            s.strip().lower()
            for s in offre.competences.replace(",", " ").split()
            if len(s.strip()) > 1
        }
        score = round(len(student_skills.intersection(offer_skills)) / len(offer_skills) * 100) if offer_skills else 0
        resultats.append({**serialize_offre(offre), "score": score})

    resultats.sort(key=lambda item: item["score"], reverse=True)
    return resultats[:5]


@app.get("/etudiants/{id}/analyse")
@app.get("/etudiant/{id}/analyse")
def analyser_profil(id: int, db: Session = Depends(get_db)):
    etudiant = get_etudiant_or_404(db, id)
    text_comp = (etudiant.competences or "").lower()
    detected = [kw for kw in TECH_KEYWORDS if kw in text_comp]
    all_words = {w.strip().lower() for w in text_comp.replace(",", " ").split() if len(w.strip()) > 2}
    extra = [w for w in all_words if w not in TECH_KEYWORDS]
    filled = sum([
        bool(etudiant.name),
        bool(etudiant.email),
        bool(etudiant.age),
        bool(etudiant.cv and etudiant.cv.startswith("data:")),
        bool(etudiant.competences),
    ])
    profile_score = round(filled / 5 * 100)

    compatibilites = []
    student_skills = {w.strip().lower() for w in text_comp.replace(",", " ").split() if len(w.strip()) > 1}
    for offre in db.query(models.Offre).all():
        offer_skills = {s.strip().lower() for s in offre.competences.replace(",", " ").split() if len(s.strip()) > 1}
        if offer_skills and student_skills:
            compatibilites.append(round(len(student_skills.intersection(offer_skills)) / len(offer_skills) * 100))
    avg_compat = round(sum(compatibilites) / len(compatibilites)) if compatibilites else 0

    return {
        "competences_detectees": detected,
        "mots_cles": extra[:10],
        "profile_score": profile_score,
        "compatibilite_moyenne": avg_compat,
        "nb_competences": len(detected) + len(extra),
    }


@app.post("/messages", status_code=status.HTTP_201_CREATED)
def envoyer_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    msg = models.Message(**model_data(message))
    db.add(msg)
    commit_or_400(db, "Creation message invalide")
    db.refresh(msg)
    return {
        "id": msg.id,
        "contenu": msg.contenu,
        "expediteur_id": msg.expediteur_id,
        "destinataire_id": msg.destinataire_id,
        "expediteur_type": msg.expediteur_type,
        "destinataire_type": msg.destinataire_type,
    }


@app.get("/messages/{user_id}")
def recevoir_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(models.Message.destinataire_id == user_id).all()
    resultats = []
    for message in messages:
        expediteur = (
            db.query(models.Etudiant).filter_by(id=message.expediteur_id).first()
            if message.expediteur_type == "etudiant"
            else db.query(models.Entreprise).filter_by(id=message.expediteur_id).first()
        )
        destinataire = (
            db.query(models.Etudiant).filter_by(id=message.destinataire_id).first()
            if message.destinataire_type == "etudiant"
            else db.query(models.Entreprise).filter_by(id=message.destinataire_id).first()
        )
        resultats.append({
            "id": message.id,
            "contenu": message.contenu,
            "expediteur": expediteur.email if expediteur else "inconnu",
            "destinataire": destinataire.email if destinataire else "inconnu",
        })
    return resultats


@app.post("/message/email")
def envoyer_message_par_email(data: schemas.MessageEmailCreate, db: Session = Depends(get_db)):
    destinataire = (
        db.query(models.Etudiant).filter(models.Etudiant.email == data.destinataire_email).first()
        or db.query(models.Entreprise).filter(models.Entreprise.email == data.destinataire_email).first()
    )
    if not destinataire:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destinataire introuvable")

    nouveau_message = models.Message(
        contenu=data.contenu,
        expediteur_id=data.expediteur_id,
        expediteur_type=data.expediteur_type,
        destinataire_id=destinataire.id,
        destinataire_type="etudiant" if isinstance(destinataire, models.Etudiant) else "entreprise",
    )
    db.add(nouveau_message)
    commit_or_400(db, "Creation message invalide")
    db.refresh(nouveau_message)
    return {"message": "Message envoye avec succes", "id": nouveau_message.id}
