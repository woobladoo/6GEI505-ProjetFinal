from flask import Flask, request, url_for, redirect, render_template, session, flash ##import de la classe flask et de certaines fonctions utiles
from datetime import date
import sqlite3

app = Flask(__name__,template_folder='templates', static_folder='static') ##Instanciation de la classe flask

app.config['SECRET_KEY'] = 'gros secret'
DB = 'DATA.db'

# users hardcoder
users = {"admin": "password123"}

def get_db():                           #connexion à la base de données
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row  # Allows us to access rows by column name
    return conn

def get_projets():
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


@app.route('/', methods=['GET', 'POST'])        ##Définition de l'url d'accueil
def home():           ##Fonction pour gérer la réaction de la page d'accueil, le titre est dynamique
  return redirect(url_for('login'))

@app.route('/listeProjets', methods=['GET', 'POST'])        ##Définition de l'url d'accueil
def listeProjets():           ##Fonction pour gérer la réaction de la page d'accueil, le titre est dynamique
  projets = get_projets() #Chercher tous les projets dans table Projets de la BD
  return render_template('listeProjets.html', projets = projets)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if the username exists and password matches
        if username in users and users[username] == password:
            session['username'] = username  # Start a session
            flash('Login successful!', 'success')
            return redirect(url_for('listeProjets'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    return render_template('profil.html')

@app.route('/employes', methods=['GET', 'POST'])
def employes():
    return render_template('employes.html')

@app.route('/projet', methods=['GET', 'POST'])
def projet():
    return render_template('projet.html')

@app.route('/tache', methods=['GET', 'POST'])
def tache():
    return render_template('taches.html')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    return render_template('inscription.html')

@app.route('/add_projet', methods=['GET', 'POST'])
def add_projet():
    clients = get_clients()
    return render_template('add_projet.html', clients = clients)


if __name__ == '__main__':        ##Permet de lancer notre site web flask
    app.run(debug=True)

