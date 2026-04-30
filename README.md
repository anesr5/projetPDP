# Genie Log - API de stages et emplois

Genie Log est une application web qui met en relation des etudiants et des entreprises.
Les etudiants peuvent creer un profil, consulter des offres, postuler et echanger des messages.
Les entreprises peuvent publier des offres et suivre les candidatures recues.

## Contexte

Le projet repond au besoin de centraliser la recherche de stages et d emplois dans une meme plateforme.
Il permet a des etudiants de valoriser leur profil et de candidater a des offres.
Il permet aussi aux entreprises de publier des offres et de suivre les candidatures.

## Choix techniques

- Backend : FastAPI
- ORM : SQLAlchemy
- Base de donnees : PostgreSQL
- Conteneurisation : Docker
- Orchestration : Docker Compose
- Documentation API : Swagger / OpenAPI
- Validation des donnees : Pydantic

## Architecture

- backend/ : API REST FastAPI, modeles SQLAlchemy, schemas Pydantic
- frontend/ : pages HTML CSS JS statiques qui consomment l API
- database/init.sql : schema relationnel et jeu de donnees minimal
- Dockerfile : image Docker de l API
- docker-compose.yml : orchestration de l API et de PostgreSQL

Relations modelisees :

- One-to-One : Etudiant vers ProfilEtudiant
- One-to-Many / Many-to-One : Entreprise vers Offre
- Many-to-Many : Etudiant vers Offre via Candidature

## Lancement avec Docker Compose

```bash
docker compose up --build
```

API :
- http://localhost:8000
- http://localhost:8000/docs
- http://localhost:8000/openapi.json

PostgreSQL :
- host : localhost
- port : 5432
- database : genie_log
- user : genie_log
- password : genie_log_password

Le volume Docker postgres_data conserve les donnees PostgreSQL entre deux lancements.

## Lancement local sans Docker

Sous Linux ou macOS :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --app-dir backend
```

Sous Windows PowerShell :

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --app-dir backend
```

Par defaut, l API utilise backend/genie_log.db en SQLite si DATABASE_URL n est pas defini.

## Donnees de test

Le fichier database/init.sql cree un jeu de donnees minimal dans PostgreSQL :

- Etudiant : alice@example.com / alice123
- Etudiant : karim@example.com / karim123
- Entreprise : contact@technova.example / tech123
- Entreprise : rh@dataworks.example / data123

## Demonstration API

La demonstration peut etre faite directement dans Swagger :

- http://localhost:8000/docs

Parcours de demonstration conseille :

1. Creer un etudiant
2. Creer une entreprise
3. Creer une offre
4. Creer une candidature
5. Modifier le statut d une candidature
6. Lister les candidatures d un etudiant ou d une entreprise

## Exemples de routes REST

Creer un etudiant :

```bash
curl -X POST http://localhost:8000/etudiants -H "Content-Type: application/json" -d "{\"email\":\"nora@example.com\",\"mdp\":\"nora123\",\"age\":20,\"name\":\"Nora\",\"cv\":\"CV\",\"lettre_motiv\":\"Motivation\",\"competences\":\"python sql docker\",\"profil\":{\"telephone\":\"0600000003\",\"adresse\":\"Villetaneuse\",\"linkedin\":\"\"}}"
```

Connexion etudiant :

```bash
curl -X POST http://localhost:8000/auth/etudiants/login -H "Content-Type: application/json" -d "{\"email\":\"alice@example.com\",\"mdp\":\"alice123\"}"
```

Lister les offres :

```bash
curl http://localhost:8000/offres
```

Creer une offre :

```bash
curl -X POST http://localhost:8000/offres -H "Content-Type: application/json" -d "{\"titre\":\"Stage API REST\",\"description\":\"Developpement backend\",\"type\":\"stage\",\"competences\":\"python fastapi postgresql\",\"duree\":\"4 mois\",\"debut\":\"2026-06-01\",\"lieu\":\"Paris\",\"entreprise_id\":1}"
```

Postuler :

```bash
curl -X POST http://localhost:8000/candidatures -H "Content-Type: application/json" -d "{\"etudiant_id\":1,\"offre_id\":2}"
```

Modifier le statut d une candidature :

```bash
curl -X PUT "http://localhost:8000/candidatures/1/statut?nouveau_statut=acceptee"
```

## Image Docker Hub

Commande de build locale :

```bash
docker build -t genie-log-api:latest .
```

Commande pour taguer et pousser l image :

```bash
docker tag genie-log-api:latest ayoubhakim/genie-log-api:latest
docker push ayoubhakim/genie-log-api:latest
```

Lien Docker Hub :

```text
https://hub.docker.com/r/ayoubhakim/genie-log-api
```

Commande de lancement depuis Docker Hub :

```bash
docker run --rm -p 8000:8000 -e DATABASE_URL=sqlite:////tmp/genie_log.db ayoubhakim/genie-log-api:latest
```

## Tests

```bash
pytest
```