CREATE TABLE IF NOT EXISTS etudiants (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    email VARCHAR UNIQUE,
    mdp VARCHAR,
    age INTEGER,
    cv VARCHAR,
    lettre_motiv VARCHAR,
    competences VARCHAR DEFAULT ''
);

CREATE INDEX IF NOT EXISTS ix_etudiants_id ON etudiants (id);

CREATE TABLE IF NOT EXISTS profils_etudiants (
    id SERIAL PRIMARY KEY,
    telephone VARCHAR DEFAULT '',
    adresse VARCHAR DEFAULT '',
    linkedin VARCHAR DEFAULT '',
    etudiant_id INTEGER NOT NULL UNIQUE REFERENCES etudiants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_profils_etudiants_id ON profils_etudiants (id);

CREATE TABLE IF NOT EXISTS entreprises (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    email VARCHAR UNIQUE,
    mdp VARCHAR
);

CREATE INDEX IF NOT EXISTS ix_entreprises_id ON entreprises (id);
CREATE INDEX IF NOT EXISTS ix_entreprises_name ON entreprises (name);

CREATE TABLE IF NOT EXISTS offres (
    id SERIAL PRIMARY KEY,
    titre VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    competences VARCHAR NOT NULL,
    duree VARCHAR NOT NULL,
    debut VARCHAR NOT NULL,
    lieu VARCHAR NOT NULL,
    entreprise_id INTEGER NOT NULL REFERENCES entreprises(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_offres_id ON offres (id);

CREATE TABLE IF NOT EXISTS candidatures (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER NOT NULL REFERENCES etudiants(id) ON DELETE CASCADE,
    offre_id INTEGER NOT NULL REFERENCES offres(id) ON DELETE CASCADE,
    statut VARCHAR DEFAULT 'en attente',
    CONSTRAINT uq_candidature_etudiant_offre UNIQUE (etudiant_id, offre_id)
);

CREATE INDEX IF NOT EXISTS ix_candidatures_id ON candidatures (id);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    contenu VARCHAR NOT NULL,
    expediteur_id INTEGER NOT NULL,
    destinataire_id INTEGER NOT NULL,
    expediteur_type VARCHAR NOT NULL,
    destinataire_type VARCHAR NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_messages_id ON messages (id);

INSERT INTO etudiants (id, name, email, mdp, age, cv, lettre_motiv, competences)
VALUES
    (1, 'Alice Martin', 'alice@example.com', 'alice123', 21, 'CV Alice', 'Motivation Alice', 'python fastapi sql docker'),
    (2, 'Karim Benali', 'karim@example.com', 'karim123', 22, 'CV Karim', 'Motivation Karim', 'javascript react nodejs')
ON CONFLICT (id) DO NOTHING;

INSERT INTO profils_etudiants (id, telephone, adresse, linkedin, etudiant_id)
VALUES
    (1, '0600000001', 'Saint-Denis', 'https://linkedin.com/in/alice', 1),
    (2, '0600000002', 'Paris', 'https://linkedin.com/in/karim', 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO entreprises (id, name, email, mdp)
VALUES
    (1, 'TechNova', 'contact@technova.example', 'tech123'),
    (2, 'DataWorks', 'rh@dataworks.example', 'data123')
ON CONFLICT (id) DO NOTHING;

INSERT INTO offres (id, titre, description, type, competences, duree, debut, lieu, entreprise_id)
VALUES
    (1, 'Stage backend FastAPI', 'Developpement d une API REST et tests automatises', 'stage', 'python fastapi sql docker', '3 mois', '2026-06-01', 'Paris', 1),
    (2, 'Alternance frontend React', 'Creation d interfaces web pour une plateforme RH', 'alternance', 'javascript react html css', '12 mois', '2026-09-01', 'Saint-Denis', 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO candidatures (id, etudiant_id, offre_id, statut)
VALUES
    (1, 1, 1, 'en attente')
ON CONFLICT (id) DO NOTHING;

SELECT setval('etudiants_id_seq', (SELECT MAX(id) FROM etudiants));
SELECT setval('profils_etudiants_id_seq', (SELECT MAX(id) FROM profils_etudiants));
SELECT setval('entreprises_id_seq', (SELECT MAX(id) FROM entreprises));
SELECT setval('offres_id_seq', (SELECT MAX(id) FROM offres));
SELECT setval('candidatures_id_seq', (SELECT MAX(id) FROM candidatures));
