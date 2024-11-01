from flask import Flask, request, url_for, redirect, render_template, session, flash ##import de la classe flask et de certaines fonctions utiles
from datetime import date

app = Flask(__name__,template_folder='templates', static_folder='static') ##Instanciation de la classe flask

app.config['SECRET_KEY'] = 'gros secret' 

# users hardcoder
users = {"admin": "password123"}

@app.route('/', methods=['GET', 'POST'])        ##Définition de l'url d'accueil
def home():           ##Fonction pour gérer la réaction de la page d'accueil, le titre est dynamique
  return redirect(url_for('login'))

@app.route('/accueil', methods=['GET', 'POST'])        ##Définition de l'url d'accueil
def accueil():           ##Fonction pour gérer la réaction de la page d'accueil, le titre est dynamique
  return render_template('accueil.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if the username exists and password matches
        if username in users and users[username] == password:
            session['username'] = username  # Start a session
            flash('Login successful!', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':        ##Permet de lancer notre site web flask
    app.run(debug=True)

