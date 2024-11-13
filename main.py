#!/usr/bin/env python3
"""! @brief Application Web pour un gestionnaire de projet et de temps."""
##
#@mainpage Page principale
#
#@section description_main Description
#Ceci est une application web pour faire la gestion des projets et du temps mis sur les projets
#
#@section notes_main Notes
#- Fait par Antoine Methot, Maxime Simard et Mayatta Ndiaye. Isaak St-Hilaire pour la Documentation
#
# Copyright (c) 2024 A.Methot, M.Simard, M.Ndiaye Tous droits réservés.

from flask import Flask, request, url_for, redirect, render_template, session, flash ##import de la classe flask et de certaines fonctions utiles
from datetime import date
import sqlite3

app = Flask(__name__,template_folder='templates', static_folder='static') ##Instanciation de la classe flask

app.config['SECRET_KEY'] = 'gros secret'
DB = 'DATA.db'

# users hardcoder
users = {"admin": "password123"}

def get_db():                           #connexion à la base de données
    """!
    @brief Se connecte ala base de données
    @return Retourne une connection à la base de données
    """
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # Allows us to access rows by column name
    return conn

def check_user_exists(username, password):

    """!
    @brief Vérifie si un utilisateur existe dans la base de données
    @param username le courriel d'un employé dans la base de données
    @param password le mot de passe d'un employé dans la base de données
    @return Retourne un employé de la base de données
    """

    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Employe WHERE courriel = ? AND motPasse = ?", (username, password))
    user = cursor.fetchone()
    
    return user is not None

def get_projets():

    """!
    @brief Se connecte a la base de données et cherche les projets
    @return Retourne la liste de projets
    """
        
    conn = sqlite3.connect(DB) # Connect to DB
    cursor = conn.cursor()

    query = '''
    SELECT Projet.id, Projet.idClient, Projet.etatProjet, Projet.idChef, Projet.nom, Projet.dateDebut, Projet.dateFin,
        Client.prenom || ' ' || Client.nom AS client_name, Employe.prenom || ' ' || Employe.nom AS manager_name
    FROM Projet
    LEFT JOIN Client ON Projet.idClient = Client.id
    LEFT JOIN Employe ON Projet.idChef = Employe.id
    '''
    cursor.execute(query) #Cherche tous les projets dans la table projet
    projets = cursor.fetchall()
    conn.close()
    return projets

def get_clients():
    """!
    @brief Se connecte ala base de données et cherche les clients
    @return Retourne une liste des clients
    """
    conn = sqlite3.connect(DB) # Connect to DB
    cursor = conn.cursor()
    query = '''
    SELECT id, nom, prenom, courriel, telephone, status
    FROM Client
    '''
    cursor.execute(query)
    clients = cursor.fetchall()
    print(clients)
    conn.close
    return clients

def get_gestionnaires():
    """!
    @brief Se connecte a la base de données et cherche les gestionnaires
    @return Retourne une liste des gestionnaires
    """
    conn = sqlite3.connect(DB) # Connect to DB
    cursor = conn.cursor()
    query = '''
    SELECT id, idRole, nom, prenom
    FROM Employe
    WHERE idRole = 1 OR idRole = 2
    '''
    cursor.execute(query)
    gestionnaires = cursor.fetchall()
    print(gestionnaires)
    conn.close
    return gestionnaires


@app.route('/', methods=['GET', 'POST'])        ##Définition de l'url d'accueil
def home():           ##Fonction pour gérer la réaction de la page d'accueil, le titre est dynamique
  """!
  @brief Affiche la page d'acceuil
  @return affiche la page de connexion
  """
  return redirect(url_for('login'))

@app.route('/listeProjets', methods=['GET', 'POST'])        ##Définition de l'url de la page de connexion
def listeProjets():           ##Fonction pour gérer la réaction de la page d'accueil, le titre est dynamique
  """!
  @brief Cherche les projets dans la base de données
  @return affiche la page avec la liste des projets
  """
  projets = get_projets() #Chercher tous les projets dans table Projets de la BD
  return render_template('listeProjets.html', projets = projets)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """!
    @brief Cherche les utilisateurs de la BD et compare les courriels et mot de passes avec les données dans BD
    @return Si les données match le formulaire, retourne la page de listeProjet sinon la meme page de connexion
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if the username exists and password matches
        if check_user_exists(username, password):
            session['username'] = username  # Start a session
            flash('Login successful!', 'success')
            return redirect(url_for('listeProjets'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """!
    @brief affiche un message de deconnexion
    @return affiche la page de connexion
    """
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    """!
    @brief Render le template de profil html
    @return affiche la page profil
    """
    return render_template('profil.html')

@app.route('/employes', methods=['GET', 'POST'])
def employes():
    """!
    @brief Render le template de employes html
    @return affiche la page avec la liste employes
    """
    return render_template('employes.html')

@app.route('/projet', methods=['GET', 'POST'])
def projet():
    """!
    @brief Render le template de projet html
    @return affiche la page contenant les tâches du projet
    """
    return render_template('projet.html')

@app.route('/tache', methods=['GET', 'POST'])
def tache():
    """!
    @brief Render le template de taches html
    @return affiche la page d'une tâche avec les sous-tâches et description
    """
    return render_template('taches.html')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """!
    @brief Render le template de inscription html
    @return affiche la page d'inscription d'un employé
    """
    return render_template('inscription.html')

@app.route('/add_projet', methods=['GET', 'POST'])
def add_projet():
    """!
    @brief Cherche les clients et les gestionnaires dans la BD pour avoir les données du formulaire d'ajout de projet
    @return Affiche le formulaire d'ajout de projet
    """
    clients = get_clients()
    gestionnaires = get_gestionnaires()
    return render_template('add_projet.html', clients = clients, gestionnaires = gestionnaires)

@app.route('/add_projet_todb', methods=['POST'])
def add_projet_todb():
    """!
    @brief Prend les informations du formulaire et les ajoute à la DB
    @return redirige vers la page liste de projet
    """
    # Get form data from the request
    nom = request.form['nom']
    client_id = request.form['Client']
    gestionnaire_id = request.form['Gestionnaire']
    date_debut = request.form['date_debut']
    date_fin = request.form['date_fin']
    is_template = request.form['Template']

    # Connect to the database and insert the new project
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = '''
    INSERT INTO Projet (idClient, etatProjet, idChef, nom, dateDebut, dateFin, isTemplate)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (client_id, 1, gestionnaire_id, nom, date_debut, date_fin, is_template))
    conn.commit()
    conn.close()

    # Redirect back to the form page or another page after successful insertion
    return redirect(url_for('listeProjets'))


@app.route('/delete_projet/<int:projet_id>', methods=['POST'])
def delete_projet(projet_id):
    """!
    @brief Supprime un projet de la BD
    @param projet_id le ID du projet a supprimer
    @return redirige vers la page liste projet
    """
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = 'DELETE FROM Projet WHERE id = ?'
    cursor.execute(query, (projet_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('listeProjets'))  # Redirect to the project list or another page


if __name__ == '__main__':        ##Permet de lancer notre site web flask
    app.run(debug=True)