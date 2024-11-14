-- SQLite

DROP TABLE IF EXISTS Temps;

CREATE TABLE Temps (
    id INTEGER PRIMARY KEY,
    idEmployeTache INTEGER NOT NULL,
    heuresTravaillees REAL NOT NULL,
    dateTravaille DATE,
    FOREIGN KEY (idEmployeTache) REFERENCES EmployeTache(id)
);