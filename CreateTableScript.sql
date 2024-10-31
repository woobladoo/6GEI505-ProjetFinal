CREATE TABLE Role (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE Client (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    courriel TEXT NOT NULL UNIQUE,
    telephone TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL
);

CREATE TABLE Employe (
    id INTEGER PRIMARY KEY,
    idRole INTEGER NOT NULl,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    courriel TEXT NOT NULL UNIQUE,
    telephone TEXT NOT NULL UNIQUE,
    motPasse TEXT NOT NULL,
    FOREIGN KEY (idRole) REFERENCES Role(id)
);

CREATE TABLE Projet (
    id INTEGER PRIMARY KEY,
    idClient INTEGER NOT NULL,
    etatProjet INTEGER NOT NULL,
    idChef INTEGER NOT NULL,
    nom TEXT NOT NULL UNIQUE,
    dateDebut DATE,
    dateFin DATE,
    isTemplate BOOLEAN NOT NULL,
    FOREIGN KEY (idClient) REFERENCES Client(id),
    FOREIGN KEY (etatProjet) REFERENCES Etat(id),
    FOREIGN KEY (idChef) REFERENCES Employe(id)
);

CREATE TABLE Tache (
    id INTEGER PRIMARY KEY,
    idProjet INTEGER NOT NULL,
    etatTache INTEGER NOT NULL,
    membreAssigne INTEGER NOT NULL,
    tacheParent INTEGER NOT NULL,
    nom TEXT NOT NULL UNIQUE,
    dateDebut DATE,
    dateFin DATE,
    FOREIGN KEY (idProjet) REFERENCES Projet(id),
    FOREIGN KEY (etatTache) REFERENCES Etat(id),
    FOREIGN KEY (membreAssigne) REFERENCES Employe(id),
    FOREIGN KEY (tacheParent) REFERENCES Tache(id)
);

CREATE TABLE Etat (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL UNIQUE
);

CREATE TABLE Temps (
    id INTEGER PRIMARY KEY,
    idEmploye INTEGER NOT NULL,
    idTache INTEGER NOT NULL,
    heuresTravaillees REAL NOT NULL,
    dateTravaille DATE,
    FOREIGN KEY (idEmploye) REFERENCES Employe(id),
    FOREIGN KEY (idTache) REFERENCES Tache(id)
);
