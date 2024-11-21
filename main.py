from flask import Flask, request, url_for, redirect, render_template, session, flash, jsonify ##import de la classe flask et de certaines fonctions utiles
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

def check_user_exists(username, password):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Employee_emp WHERE emp_courriel = ? AND emp_motPasse = ?;", (username, password))
    user = cursor.fetchone()
    
    return user is not None

def get_user_role(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_role_id AS idRole FROM Employee_emp WHERE emp_courriel = ?;", (username,))
    role = cursor.fetchone()
    conn.close()
    return role[0] if role else None

def get_user(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employee_emp WHERE emp_courriel = ?;", (username,))  # Adjust columns as needed
    user = cursor.fetchall()
    conn.close()
    return user

def get_employes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id AS id, emp_prenom AS prenom, emp_nom AS nom, emp_courriel AS courriel, emp_telephone AS telephone, emp_role_id AS idRole FROM Employee_emp;")  # Adjust columns as needed
    employes = cursor.fetchall()
    conn.close()
    return employes

def get_projets():
    conn = sqlite3.connect(DB) # Connect to DB
    cursor = conn.cursor()

    query = '''
    SELECT Projet_proj.proj_id AS id, 
        Projet_proj.proj_clnt_id AS idClient, 
        Projet_proj.proj_etat_etat AS etatProjet, 
        Projet_proj.proj_emp_id AS idChef, 
        Projet_proj.proj_nom AS nom, 
        Projet_proj.proj_dateDebut AS dateDebut, 
        Projet_proj.proj_dateFin AS dateFin, 
        Client_clnt.clnt_prenom || ' ' || Client_clnt.clnt_nom AS client_name, 
        Employee_emp.emp_prenom || ' ' || Employee_emp.emp_nom AS manager_name
    FROM Projet_proj
    LEFT JOIN Client_clnt ON Projet_proj.proj_clnt_id = Client_clnt.clnt_id
    LEFT JOIN Employee_emp ON Projet_proj.proj_emp_id = Employee_emp.emp_id;

    '''
    cursor.execute(query) #Cherche tous les projets dans la table projet
    projets = cursor.fetchall()
    conn.close()
    return projets

def get_clients():
    conn = sqlite3.connect(DB) # Connect to DB
    cursor = conn.cursor()
    query = '''
    SELECT clnt_id AS id, 
        clnt_nom AS nom, 
        clnt_prenom AS prenom, 
        clnt_courriel AS courriel, 
        clnt_telephone AS telephone, 
        clnt_status AS status
    FROM Client_clnt;
    '''
    cursor.execute(query)
    clients = cursor.fetchall()
    print(clients)
    conn.close
    return clients

def get_gestionnaires():
    conn = sqlite3.connect(DB) # Connect to DB
    cursor = conn.cursor()
    query = '''
    SELECT emp_id AS id, 
        emp_role_id AS idRole, 
        emp_nom AS nom, 
        emp_prenom AS prenom
    FROM Employee_emp
    WHERE emp_role_id = 1 OR emp_role_id = 2;
    '''
    cursor.execute(query)
    gestionnaires = cursor.fetchall()
    print(gestionnaires)
    conn.close
    return gestionnaires


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
        if check_user_exists(username, password):
            session['username'] = username  # Start a session
            user_role = get_user_role(username)
            if user_role:
                session['role'] = user_role
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
    courriel = session.get('username')
    user = get_user(courriel)
    return render_template('profil.html', user=user)

@app.route('/employes', methods=['GET', 'POST'])
def employes():
    listeEmploye = get_employes()
    return render_template('employes.html', employes=listeEmploye)







@app.route('/projet/<int:id>', methods=['GET'])
def projet(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Projet_proj WHERE proj_id = ?", (id,))
    projet = cursor.fetchone()
    

     # Vérifiez si le projet existe
    if not projet:
        conn.close()
        return "Projet non trouvé", 404
    
    # Fetch tasks related to the project (assuming you have a Task table with project_id as a foreign key)
    cursor.execute("SELECT * FROM Tache_tch WHERE tch_proj_id = ?", (id,))
    taches = cursor.fetchall()

    conn.close()

    # Rendre la page avec les détails du projet
    return render_template('projet.html', projet=projet, taches=taches)


@app.route('/tache/<int:id>', methods=['GET', 'POST'])
def tache(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Projet_proj WHERE proj_id = ?", (id,))
    projet = cursor.fetchone()


    # Fetch tasks related to the project (assuming you have a Task table with project_id as a foreign key)
    cursor.execute("SELECT * FROM Tache_tch WHERE tch_proj_id = ?", (id,))
    taches = cursor.fetchall()

    conn.close()
    return render_template('Taches.html', projet=projet, taches=taches)

@app.route('/add_tache', methods=['POST'])
def add_tache():
    data = request.json
    print(data)
    name = data.get('name')
    start = data.get('start')
    end = data.get('end')
    proj_id = data.get('projid')

    if name and start and end:
        # Connexion à SQLite (ou une autre base de données)
        ######################################AJOUT AVEC PROJET ID##################################
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tache_tch (tch_nom, tch_dateDebut, tch_dateFin, tch_proj_id, tch_etat_etat)
            VALUES (?, ?, ?, ?, 1)
        """, (name, start, end, proj_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Tâche ajoutée avec succès!"}), 201

    return jsonify({"error": "Données incomplètes"}), 400

@app.route('/add_projet', methods=['GET', 'POST'])
def add_projet():
    clients = get_clients()
    gestionnaires = get_gestionnaires()


    return render_template('add_projet.html', clients = clients, gestionnaires = gestionnaires)

@app.route('/add_projet_todb', methods=['POST'])
def add_projet_todb():
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
    INSERT INTO Projet_proj (proj_clnt_id, proj_etat_etat, proj_emp_id, proj_nom, proj_dateDebut, proj_dateFin, proj_isTemplate)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (client_id, 1, gestionnaire_id, nom, date_debut, date_fin, is_template))
    conn.commit()
    conn.close()

    # Redirect back to the form page or another page after successful insertion
    return redirect(url_for('listeProjets'))


@app.route('/delete_projet/<int:projet_id>', methods=['POST'])
def delete_projet(projet_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = 'DELETE FROM Projet_proj WHERE proj_id = ?;'
    cursor.execute(query, (projet_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('listeProjets'))  # Redirect to the project list or another page

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    query = 'DELETE FROM Employee_emp WHERE emp_id = ?;'
    cursor.execute(query, (employee_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('employes'))  # Redirect to the project list or another page

@app.route('/update_profile', methods=['POST'])
def update_profile():
    session_courriel = session.get('username')
    user = get_user(session_courriel)
    # Get the form data from the request
    prenom = request.form['prenom']
    nom = request.form['nom']
    courriel = request.form['courriel']
    telephone = request.form['telephone']
    role = request.form['role']
    print(user[0]['emp_id'])
    print(prenom)
    print(nom)
    print(courriel)
    print(telephone)
    print(role)

    conn = get_db()
    cursor = conn.cursor()

    # Update the user data using a parameterized query
    cursor.execute("""
        UPDATE Employee_emp
        SET emp_prenom = ?, emp_nom = ?, emp_courriel = ?, emp_telephone = ?, emp_role_id = ?
        WHERE emp_id = ?
    """, (prenom, nom, courriel, telephone, role, user[0]['emp_id']))

    conn.commit()
    conn.close()

    # Update the user information in the database
    #update_user_in_db(user_id, prenom, nom, courriel, telephone, role)

    # After updating, redirect to the profile page
    return redirect(url_for('profil'))



@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        username = request.form['email']
        telephone = request.form['telephone']
        idrole = request.form['idrole']
        mot_de_passe = request.form['motdepasse']

        # Hachage du mot de passe

        # Connexion à la base de données et ajout de l'utilisateur
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        query ='INSERT INTO Employee_emp (emp_role_id, emp_nom, emp_prenom, emp_courriel, emp_telephone, emp_motPasse) VALUES (?, ?, ?, ?, ?, ?);'
        try:
            cursor.execute(query, (idrole, nom, prenom, username, telephone, mot_de_passe))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Ce numéro de téléphone est déjà enregistré.", "error")
            return redirect(url_for('inscription'))
        finally:
            conn.close()
        

        flash("Utilisateur ajouté avec succès", "success")
        return redirect(url_for('login'))

    return render_template('inscription.html')

if __name__ == '__main__':        ##Permet de lancer notre site web flask
    app.run(host='0.0.0.0',debug=True)
