from flask import Flask, request, url_for, redirect, render_template, session, flash, jsonify ##import de la classe flask et de certaines fonctions utiles
from datetime import datetime, date
from collections import namedtuple
import sqlite3

app = Flask(__name__,template_folder='templates', static_folder='static') ##Instanciation de la classe flask

Tache = namedtuple('Tache', ['id', 'projet_id', 'statut', 'nom', 'dateDebut', 'dateFin', 'employes'])


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

def get_emp_id_for_task(emptch_tch_id):
    conn = get_db() 
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT emptch_emp_id
        FROM EmployeeTache_emptch
        WHERE emptch_tch_id = ?;
    """, (emptch_tch_id,))
    
    results = cursor.fetchall()  
    
    conn.close()
    
    if results:
        # Extract the emp_id values from each row and return as a list
        emp_ids = [row[0] for row in results]
        return emp_ids  # Returns a list of emp_ids
    else:
        return []  # Returns an empty list if no matching emp_ids are found


import sqlite3

def get_temps_total(task_id):
    
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Exécution de la requête SQL pour calculer le temps total pour la tâche spécifiée
        cursor.execute("""
            SELECT SUM(tmp_heuresTravaille)
            FROM Temps_tmp
            JOIN EmployeeTache_emptch ON temps_tmp.tmp_emptch_id = EmployeeTache_emptch.emptch_id
            WHERE EmployeeTache_emptch.emptch_tch_id = ?
        """, (task_id,))

        # Récupération du résultat
        total_time = cursor.fetchone()[0]

        # Fermeture de la connexion
        conn.close()

        # Si aucun résultat n'est trouvé, on retourne None
        if total_time is None:
            return 0  # ou `None` si vous préférez indiquer que la tâche n'a pas été trouvée

        return total_time

    except sqlite3.Error as e:
        print(f"Erreur lors de l'accès à la base de données: {e}")
        return None


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

def get_projet_by_id(proj_id):
    conn1 = sqlite3.connect(DB)  # Connect to the DB
    cursor1 = conn1.cursor()

    query = """
    SELECT 
        Projet_proj.proj_id AS id, 
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
    LEFT JOIN Employee_emp ON Projet_proj.proj_emp_id = Employee_emp.emp_id
    WHERE Projet_proj.proj_id = ?;
    """
    
    # Use a parameterized query to execute
    cursor1.execute(query, (proj_id,))  
    projet = cursor1.fetchone()  # Fetch a single result
    conn1.close()
    
    return projet

def get_taches_by_project(proj_id):
    conn = sqlite3.connect(DB)  # Connect to the database
    cursor = conn.cursor()
    
    query = """
    SELECT 
        Tache_tch.tch_id AS id, 
        Tache_tch.tch_proj_id AS projet_id, 
        Etat_etat.etat_nom AS statut,  -- Get the status name instead of its ID
        Tache_tch.tch_nom AS nom, 
        Tache_tch.tch_dateDebut AS dateDebut, 
        Tache_tch.tch_dateFin AS dateFin
    FROM Tache_tch
    LEFT JOIN Etat_etat ON Tache_tch.tch_etat_etat = Etat_etat.etat_id  -- Join with the Etat_etat table
    WHERE Tache_tch.tch_proj_id = ? AND Tache_tch.tch_parent IS NULL;
    """
    cursor.execute(query, (proj_id,))
    taches = cursor.fetchall()
    conn.close()
    
    return taches

def get_soustaches_by_tache(task_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    query = """
    SELECT 
        Tache_tch.tch_id AS id, 
        Tache_tch.tch_proj_id AS projet_id, 
        Etat_etat.etat_nom AS statut,
        Tache_tch.tch_nom AS nom, 
        Tache_tch.tch_dateDebut AS dateDebut, 
        Tache_tch.tch_dateFin AS dateFin,
        GROUP_CONCAT(EmployeeTache_emptch.emptch_emp_id) AS employes_ids
    FROM Tache_tch
    LEFT JOIN Etat_etat ON Tache_tch.tch_etat_etat = Etat_etat.etat_id
    LEFT JOIN EmployeeTache_emptch ON Tache_tch.tch_id = EmployeeTache_emptch.emptch_tch_id
    WHERE Tache_tch.tch_parent = ?
    GROUP BY Tache_tch.tch_id, Tache_tch.tch_proj_id, Etat_etat.etat_nom, Tache_tch.tch_nom, Tache_tch.tch_dateDebut, Tache_tch.tch_dateFin
    """
    
    cursor.execute(query, (task_id,))
    taches = cursor.fetchall()
    
    # Convert the 'employes_ids' field from a comma-separated string to a list
    for i in range(len(taches)):
        employes_ids = taches[i][6]
        if employes_ids:
            taches[i] = taches[i][:6] + (employes_ids.split(','),)  # Replace the 7th element with the list of IDs
    
   
    conn.close()
    
    return taches


def get_tache_by_id(task_id):
    conn = sqlite3.connect(DB)  # Connect to the database
    conn.row_factory = sqlite3.Row  # Use Row factory to access columns by name
    cursor = conn.cursor()
    
    query = """
    SELECT 
        Tache_tch.tch_id AS id, 
        Tache_tch.tch_proj_id AS projet_id, 
        Etat_etat.etat_nom AS statut,  -- Get the status name instead of its ID
        Tache_tch.tch_nom AS nom, 
        Tache_tch.tch_dateDebut AS dateDebut, 
        Tache_tch.tch_dateFin AS dateFin,
        GROUP_CONCAT(Employee_emp.emp_prenom || ' ' || Employee_emp.emp_nom) AS employes  -- Combine first and last names
    FROM Tache_tch
    LEFT JOIN Etat_etat ON Tache_tch.tch_etat_etat = Etat_etat.etat_id  -- Join with the Etat_etat table
    LEFT JOIN EmployeeTache_emptch ON Tache_tch.tch_id = EmployeeTache_emptch.emptch_tch_id  -- Join with EmployeeTache_emptch table
    LEFT JOIN Employee_emp ON EmployeeTache_emptch.emptch_emp_id = Employee_emp.emp_id  -- Join with Employee_emp table
    WHERE Tache_tch.tch_id = ?  -- Only filter by task_id
    GROUP BY Tache_tch.tch_id;
    """
    
    cursor.execute(query, (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        # Convert Row object to a named tuple
        employes = row['employes'].split(',') if row['employes'] else []
        tache = Tache(
            id=row['id'],
            projet_id=row['projet_id'],
            statut=row['statut'],
            nom=row['nom'],
            dateDebut=row['dateDebut'],
            dateFin=row['dateFin'],
            employes=employes
        )
    else:
        tache = None  # Explicitly set to None if no task is found

   
    return tache


def utilisateur_assigne_tache(user_id, task_id):
    
    conn = sqlite3.connect(DB) # Connect to DB
    cursor = conn.cursor()

    # Requête pour vérifier l'association de l'utilisateur à la tâche
    query = """
    SELECT 1
    FROM EmployeeTache_emptch
    WHERE emptch_emp_id = ? AND emptch_tch_id = ?
    """
    
    cursor.execute(query, (user_id, task_id))
    result = cursor.fetchone()
    conn.close()

    # Retourne True si un résultat est trouvé, sinon False
    return result is not None

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

    projet = get_projet_by_id(id)
    if projet is None:
        return "Project not found", 404  # Or render a custom 404 page
    
    taches = get_taches_by_project(id)
    print(taches)

    # Rendre la page avec les détails du projet
    return render_template('projet.html', projet=projet, taches=taches)



@app.route('/projet/<int:proj_id>/tache/<int:task_id>', methods=['GET', 'POST'])
def tache(proj_id, task_id):
    username = session.get('username')
    user = get_user(username)
    if not user:
        return "User not found", 404

    projet = get_projet_by_id(proj_id)
    if projet is None:
        return "Project not found", 404  # Or render a custom 404 page

    tache = get_tache_by_id(task_id)
    if tache is None:
        return "Task not found", 404  # Or render a custom 404 page
    
    sousTaches = get_soustaches_by_tache(task_id)
    

    temps = get_temps_total(task_id)

    listeEmploye = get_employes()
    employesSurTache = get_emp_id_for_task(task_id)

    return render_template('Taches.html', projet=projet, tache=tache, sousTaches = sousTaches,employes=listeEmploye, user=user, temps=temps, employesSurTache = employesSurTache)

@app.route('/add_tache', methods=['POST'])
def add_tache():
    data = request.json
    name = data.get('name')
    start = data.get('start')
    end = data.get('end')
    proj_id = data.get('projid')
    parent_id = data.get('parentid')

    if name and start and end:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Tache_tch (tch_nom, tch_dateDebut, tch_dateFin, tch_proj_id, tch_parent, tch_etat_etat)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (name, start, end, proj_id, parent_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Tâche ajoutée avec succès!"}), 201

    return jsonify({"error": "Données incomplètes"}), 400

@app.route('/delete_tache/<int:projid>/<int:tacheid>', methods=['POST'])
def delete_tache(tacheid, projid):
    # Connect to the database
    conn = get_db()
    cursor = conn.cursor()

    # First, delete all sub-tasks linked to the task
    cursor.execute("DELETE FROM Tache_tch WHERE tch_parent = ?", (tacheid,))

    # Then, delete the task itself
    cursor.execute("DELETE FROM Tache_tch WHERE tch_id = ?", (tacheid,))

    # Commit the changes to the database
    conn.commit()
    conn.close()

    # Redirect to the project page or task list
    #flash('Task and all associated sub-tasks deleted successfully', 'success')
    return redirect(url_for('projet', id=projid))  # Redirect to the project page, adjust as needed



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
    # Connect to the database
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # First, delete all sub-tasks linked to the tasks of the project
    cursor.execute("""
        DELETE FROM Tache_tch 
        WHERE tch_parent IN (
            SELECT tch_id FROM Tache_tch WHERE tch_proj_id = ?
        )
    """, (projet_id,))

    # Then, delete all tasks directly linked to the project
    cursor.execute("DELETE FROM Tache_tch WHERE tch_proj_id = ?", (projet_id,))

    # Finally, delete the project itself
    cursor.execute("DELETE FROM Projet_proj WHERE proj_id = ?", (projet_id,))

    # Commit the changes to the database
    conn.commit()
    conn.close()

    # Redirect to the project list or another page
    #flash('Project, all associated tasks, and sub-tasks deleted successfully', 'success')
    return redirect(url_for('listeProjets'))  # Adjust redirection as necessary



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

@app.route('/ajouter_temps', methods=['POST'])
def ajouter_temps():

    # Récupération des données du formulaire
    data = request.get_json()
    tache_id = data.get('tache_id')
    temps_ajoute = int(data.get('temps_ajoute', 0))
    employe_id = int(data.get('employe_id', 0))
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")

    # Connexion à la base de données SQLite
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()


    # Vérifiez si l'employé est bien associé à la tâche dans la table EmployeeTache_emptch
    print(f"Données reçues: {data}")
    cursor.execute("SELECT emptch_id FROM EmployeeTache_emptch WHERE emptch_emp_id = ? AND emptch_tch_id = ?", (employe_id, tache_id))
    employe_tache = cursor.fetchone()
    if not employe_tache:
        conn.close()  # Fermer la connexion
        return jsonify({'message': 'L\'employé n\'est pas associé à la tâche'}), 404

    # Ajoutez l'enregistrement dans la table Temps_tmp
    cursor.execute("INSERT INTO Temps_tmp (tmp_emptch_id, tmp_heuresTravaille, tmp_dateTravaille) VALUES (?, ?, ?)",
                   (employe_tache[0], temps_ajoute, formatted_date))


    # Commit pour enregistrer les changements dans la base de données
    conn.commit()
    conn.close()  # Fermer la connexion

    return jsonify({}), 200  



@app.route('/add_employe_to_tache', methods=['POST'])
def add_employe_to_tache():
    
    if request.method == 'POST':
        # Récupération des données du formulaire
       
        tache_id = request.form['tache_id']
        employe_id = request.form.get('employe_id')
        projet_id = request.form['projet_id']
        

        # Connexion à la base de données et ajout de l'utilisateur
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        

        cursor.execute("""
            SELECT 1 FROM EmployeeTache_emptch 
            WHERE emptch_emp_id = ? AND emptch_tch_id = ?
        """, (employe_id, tache_id))

        existing_assignment = cursor.fetchone()
        if existing_assignment:
            # If the employee is already assigned to the task, flash a message
            flash("Cet employé est déjà associé à cette tâche.", "error")
            conn.close()
            return redirect(url_for('tache', proj_id=projet_id, task_id=tache_id))
        

       
        try:
            query ='INSERT INTO EmployeeTache_emptch (emptch_emp_id, emptch_tch_id) VALUES (?, ?);'
            cursor.execute(query, (employe_id, tache_id))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Cette personne est deja sur cette tache", "error")
            return redirect(url_for('tache',proj_id = projet_id, task_id= tache_id, projet=projet, tache=tache))
        finally:
            conn.close()
        

        flash("Utilisateur ajouté avec succès", "success")
        return redirect(url_for('tache',proj_id = projet_id, task_id= tache_id, projet=projet, tache=tache))

    return render_template('taches.html',proj_id = projet_id, task_id= tache_id, projet=projet, tache=tache)

@app.route('/delete_employee_tache', methods=['POST'])
def delete_employee_tache():
    # Récupérer les données du formulaire
    employee_tache_id = request.form['employee_tache_id']
    tache_id = request.form['tach']
    projet_id = request.form['proj']
    employee_tch = employee_tache_id.split(' ',1)[0]
    # Affichage dans la console pour le débogage (optionnel)
    print(f"Supprimer l'employé avec l'ID {employee_tch} de la tâche {tache_id}")

    # Connexion à la base de données
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        # Exécuter la requête SQL pour supprimer l'employé de la tâche
        query = 'DELETE FROM EmployeeTache_emptch WHERE emptch_emp_id = (Select emp_id from Employee_emp where emp_prenom = ?);'
        cursor.execute(query, (employee_tch,))  # L'ID de l'employé et l'ID de la tâche
        conn.commit()

        # Message flash pour l'utilisateur (facultatif)
        flash("Employé supprimé de la tâche avec succès.", "success")
    
    except Exception as e:
        # Si une erreur survient, message d'erreur (facultatif)
        flash("Erreur lors de la suppression de l'employé de la tâche.", "error")
        print(f"Error: {e}")
    
    finally:
        # Fermer la connexion à la base de données
        conn.close()

    # Rediriger l'utilisateur vers la page de la tâche ou autre page appropriée
    return redirect(url_for('tache', proj_id=projet_id, task_id=tache_id))

@app.route('/visualization/<int:project_id>')
def visualization(project_id):
    conn = get_db()
    cursor = conn.cursor()

    # Fetch project tasks and sub-tasks
    cursor.execute("""
        SELECT tch_id, tch_nom, tch_parent, tch_dateDebut, tch_dateFin 
        FROM Tache_tch 
        WHERE tch_proj_id = ? 
        ORDER BY tch_parent ASC, tch_dateDebut ASC
    """, (project_id,))
    tasks = cursor.fetchall()

    projet = get_projet_by_id(project_id)

    conn.close()

    # Pass data to the template
    return render_template('visualization.html', projet=projet, tasks=tasks)

@app.route('/update_task', methods=['POST'])
def update_task():
    print(request.form)
    sous_tache_id = request.form.get('task_id')
    tache_id = request.form.get('tache_id')
    new_status = request.form.get('task_status')
    projet_id = request.form.get('proj')

    # Validate inputs
    if not sous_tache_id or not new_status or not projet_id or not tache_id:
        return "Données invalides", 400

    try:
        # Connexion à la base de données avec un gestionnaire de contexte
        with get_db() as conn:
            cursor = conn.cursor()
            # Mise à jour du statut
            cursor.execute("""
                UPDATE Tache_tch
                SET tch_etat_etat = ?
                WHERE tch_id = ?
            """, (new_status, sous_tache_id))
            conn.commit()

        # Redirection après mise à jour
        return redirect(url_for('tache', proj_id=projet_id, task_id=tache_id))

    except Exception as e:
        # Log the error in production (don't expose it to users)
        app.logger.error(f"Database update failed: {e}")
        return "Erreur interne du serveur", 500
    
@app.route('/update_tasks', methods=['POST'])
def update_tasks():
    print(request.form)
    tache_id = request.form.get('tache_id')
    new_status = request.form.get('task_status')
    projet_id = request.form.get('proj')

    # Validate inputs
    if  not new_status or not projet_id or not tache_id:
        return "Données invalides", 400

    try:
        # Connexion à la base de données avec un gestionnaire de contexte
        with get_db() as conn:
            cursor = conn.cursor()
            # Mise à jour du statut
            cursor.execute("""
                UPDATE Tache_tch
                SET tch_etat_etat = ?
                WHERE tch_id = ?
            """, (new_status, tache_id))
            conn.commit()

        # Redirection après mise à jour
        return redirect(url_for('projet', id=projet_id))

    except Exception as e:
        # Log the error in production (don't expose it to users)
        app.logger.error(f"Database update failed: {e}")
        return "Erreur interne du serveur", 500


if __name__ == '__main__':        ##Permet de lancer notre site web flask
    app.run(host='0.0.0.0',debug=True)
