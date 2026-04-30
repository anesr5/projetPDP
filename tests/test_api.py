import os
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "backend"))

os.environ["DATABASE_URL"] = f"sqlite:///{ROOT_DIR / 'tests' / 'test.db'}"

import models  # noqa: E402
import schemas  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
from main import (  # noqa: E402
    connecter_etudiant,
    creer_candidature,
    creer_entreprise,
    creer_etudiant,
    creer_offre,
    lire_etudiant,
    modifier_etudiant,
    modifier_statut_candidature,
)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_etudiant_crud_and_one_to_one_profile(db):
    etudiant = creer_etudiant(
        schemas.EtudiantCreate(
            email="alice@test.local",
            mdp="secret",
            age=21,
            name="Alice",
            cv="CV",
            lettre_motiv="Motivation",
            competences="python fastapi",
            profil=schemas.ProfilEtudiantCreate(
                telephone="0600000001",
                adresse="Paris",
                linkedin="https://linkedin.example/alice",
            ),
        ),
        db,
    )

    assert etudiant["id"] == 1
    assert etudiant["profil"]["telephone"] == "0600000001"

    modifie = modifier_etudiant(
        1,
        schemas.EtudiantUpdate(age=22, profil=schemas.ProfilEtudiantUpdate(adresse="Saint-Denis")),
        db,
    )
    assert modifie["age"] == 22
    assert modifie["profil"]["adresse"] == "Saint-Denis"

    lu = lire_etudiant(1, db)
    assert lu["email"] == "alice@test.local"


def test_entreprise_offre_and_candidature_flow(db):
    etudiant = creer_etudiant(
        schemas.EtudiantCreate(
            email="karim@test.local",
            mdp="secret",
            age=22,
            name="Karim",
            cv="CV",
            lettre_motiv="",
            competences="javascript react",
        ),
        db,
    )
    entreprise = creer_entreprise(
        schemas.EntrepriseCreate(email="rh@test.local", mdp="secret", name="Tech RH"),
        db,
    )
    offre = creer_offre(
        schemas.OffreCreate(
            titre="Stage web",
            description="Developpement frontend",
            type="stage",
            competences="javascript react",
            duree="3 mois",
            debut="2026-06-01",
            lieu="Paris",
            entreprise_id=entreprise["id"],
        ),
        db,
    )

    candidature = creer_candidature(
        schemas.CandidatureCreate(etudiant_id=etudiant["id"], offre_id=offre["id"]),
        db,
    )
    assert candidature["statut"] == "en attente"

    with pytest.raises(HTTPException) as duplicate:
        creer_candidature(
            schemas.CandidatureCreate(etudiant_id=etudiant["id"], offre_id=offre["id"]),
            db,
        )
    assert duplicate.value.status_code == 409

    update = modifier_statut_candidature(candidature["id"], "acceptee", db)
    assert "acceptee" in update["message"]


def test_not_found_and_login_errors_use_http_status_codes(db):
    with pytest.raises(HTTPException) as missing:
        lire_etudiant(999, db)
    assert missing.value.status_code == 404

    with pytest.raises(HTTPException) as bad_login:
        connecter_etudiant(schemas.Login(email="missing@test.local", mdp="bad"), db)
    assert bad_login.value.status_code == 401


def test_models_include_required_relationships():
    assert models.Etudiant.profil.property.uselist is False
    assert models.Entreprise.offres.property.mapper.class_ is models.Offre
    assert models.Candidature.etudiant.property.mapper.class_ is models.Etudiant
    assert models.Candidature.offre.property.mapper.class_ is models.Offre
