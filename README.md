# API Genie Log

API RESTful conteneurisée développée dans le cadre de la SAE **Développement & Déploiement d’une Application Web RESTful Conteneurisée**.

## Contexte du projet

Ce projet a pour objectif de proposer une API REST permettant la gestion d'une plateforme de mise en relation entre étudiants et entreprises.

L'application permet notamment de :
- gérer les étudiants ;
- gérer les entreprises ;
- gérer les offres ;
- gérer les candidatures ;
- suivre l’état d’une candidature.

Le projet respecte les contraintes demandées dans la SAE :
- API REST conforme aux standards HTTP ;
- base de données relationnelle ;
- persistance des données avec ORM ;
- conteneurisation avec Docker ;
- orchestration avec Docker Compose.

## Technologies utilisées

- **Backend** : FastAPI
- **ORM** : SQLAlchemy
- **Base de données** : PostgreSQL
- **Conteneurisation** : Docker
- **Orchestration** : Docker Compose

## Dépôt GitHub

Le code source du projet est disponible ici :

[https://github.com/anesr5/projetPDP](https://github.com/anesr5/projetPDP)

## Structure du projet

```bash
.
├── app/
├── database/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Architecture du projet

L’architecture repose sur deux conteneurs Docker :
- un conteneur pour l’API FastAPI ;
- un conteneur pour la base de données PostgreSQL.

Docker Compose permet de lancer l’ensemble du projet et d’assurer la communication entre les services.

## Lancer le projet avec Docker Compose

### 1. Cloner le dépôt

```bash
git clone https://github.com/anesr5/projetPDP.git
cd projetPDP
```

### 2. Lancer les conteneurs

```bash
docker compose up --build
```

### 3. Accéder à l’application

Une fois les conteneurs lancés, l’API est accessible à l’adresse suivante :

- API : [http://localhost:8000](http://localhost:8000)
- Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc : [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Jeu de données de test

Le projet contient un fichier SQL ou un script d’import permettant d’initialiser un jeu de données minimal pour les tests.

Exemples de données manipulées :
- étudiants ;
- entreprises ;
- offres ;
- candidatures.

## Exemples de routes de l’API

Voici quelques routes principales de l’API :

### Étudiants
- `GET /students`
- `GET /students/{id}`
- `POST /students`
- `PUT /students/{id}`
- `DELETE /students/{id}`

### Entreprises
- `GET /companies`
- `GET /companies/{id}`
- `POST /companies`
- `PUT /companies/{id}`
- `DELETE /companies/{id}`

### Offres
- `GET /offers`
- `GET /offers/{id}`
- `POST /offers`
- `PUT /offers/{id}`
- `DELETE /offers/{id}`

### Candidatures
- `GET /applications`
- `GET /applications/{id}`
- `POST /applications`
- `PUT /applications/{id}`
- `DELETE /applications/{id}`

## Exemple d’utilisation

Après le lancement du projet, il est possible de tester directement l’API depuis Swagger :
1. ouvrir [http://localhost:8000/docs](http://localhost:8000/docs)
2. sélectionner une route ;
3. cliquer sur **Try it out** ;
4. exécuter la requête.

## Relations modélisées

Le projet met en œuvre les relations demandées dans l’énoncé :
- **One-to-One**
- **One-to-Many / Many-to-One**
- **Many-to-Many**

Ces relations sont représentées dans les entités du code ainsi que dans le schéma relationnel de la base de données.

## Image Docker Hub

L’image Docker de l’API est disponible ici :

[https://hub.docker.com/r/ayoubhakim/genie-log-api](https://hub.docker.com/r/ayoubhakim/genie-log-api)

### Lancer l’image en local

```bash
docker pull ayoubhakim/genie-log-api
docker run -p 8000:8000 ayoubhakim/genie-log-api
```

## Persistance des données

La base de données est lancée avec Docker Compose.

Si un volume Docker est utilisé, il permet de conserver les données même après l’arrêt des conteneurs.

## Auteur

Projet réalisé dans le cadre de la SAE DDAW – Sup-Galilée.