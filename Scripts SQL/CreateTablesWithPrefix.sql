-- SQLite
-- Table: Role
CREATE TABLE Role_role (
    role_id INTEGER PRIMARY KEY,
    role_nom TEXT NOT NULL UNIQUE,
    role_desc TEXT
);

-- Table: Employee
CREATE TABLE Employee_emp (
    emp_id INTEGER PRIMARY KEY,
    emp_role_id INTEGER NOT NULL,
    emp_nom TEXT NOT NULL,
    emp_prenom TEXT NOT NULL,
    emp_courriel TEXT NOT NULL,
    emp_telephone TEXT,
    emp_motPasse TEXT NOT NULL,
    FOREIGN KEY (emp_role_id) REFERENCES Role_role(role_id)
);

-- Table: Client
CREATE TABLE Client_clnt (
    clnt_id INTEGER PRIMARY KEY,
    clnt_nom TEXT NOT NULL,
    clnt_prenom TEXT NOT NULL,
    clnt_courriel TEXT NOT NULL,
    clnt_telephone TEXT,
    clnt_status TEXT
);

-- Table: Project
CREATE TABLE Projet_proj (
    proj_id INTEGER PRIMARY KEY,
    proj_clnt_id INTEGER NOT NULL,
    proj_etat_etat INTEGER NOT NULL,
    proj_emp_id INTEGER NOT NULL,
    proj_nom TEXT NOT NULL,
    proj_dateDebut DATE,
    proj_dateFin DATE,
    proj_isTemplate BOOLEAN,
    FOREIGN KEY (proj_clnt_id) REFERENCES Client_clnt(clnt_id),
    FOREIGN KEY (proj_etat_etat) REFERENCES Etat_etat(etat_id),
    FOREIGN KEY (proj_emp_id) REFERENCES Employee_emp(emp_id)
);

-- Table: Task
CREATE TABLE Tache_tch (
    tch_id INTEGER PRIMARY KEY,
    tch_proj_id INTEGER NOT NULL,
    tch_etat_etat INTEGER NOT NULL,
    tch_parent INTEGER,
    tch_nom TEXT NOT NULL,
    tch_dateDebut DATE,
    tch_dateFin DATE,
    FOREIGN KEY (tch_proj_id) REFERENCES Projet_proj(proj_id),
    FOREIGN KEY (tch_etat_etat) REFERENCES Etat_etat(etat_id),
    FOREIGN KEY (tch_parent) REFERENCES Tache_tch(tch_id)
);

-- Table: State
CREATE TABLE Etat_etat (
    etat_id INTEGER PRIMARY KEY,
    etat_nom TEXT NOT NULL
);

-- Table: EmployeeTask
CREATE TABLE EmployeeTache_emptch (
    emptch_id INTEGER PRIMARY KEY,
    emptch_emp_id INTEGER NOT NULL,
    emptch_tch_id INTEGER NOT NULL,
    FOREIGN KEY (emptch_emp_id) REFERENCES Employee_emp(emp_id),
    FOREIGN KEY (emptch_tch_id) REFERENCES Tache_tch(tch_id)
);

-- Table: Time
CREATE TABLE Temps_tmp (
    tmp_id INTEGER PRIMARY KEY,
    tmp_emptch_id INTEGER NOT NULL,
    tmp_heuresTravaille REAL NOT NULL,
    tmp_dateTravaille DATE NOT NULL,
    FOREIGN KEY (tmp_emptch_id) REFERENCES EmployeeTache_emptch(emptch_id)
);
