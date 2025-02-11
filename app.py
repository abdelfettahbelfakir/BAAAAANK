from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymysql

# Créez l'application Flask
app = Flask(__name__)

# Configuration de la base de données MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/baank_db'  # Remplacez par vos informations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactive le suivi des modifications

# Initialisation des extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Vue de redirection si l'utilisateur essaie d'accéder à une page protégée

# Modèle User pour Flask-Login et SQLAlchemy
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)  # Balance ajoutée avec une valeur par défaut de 0.00

    def __repr__(self):
        return f'<User {self.username}>'

# Initialiser la base de données (créer les tables si elles n'existent pas)
with app.app_context():
    db.create_all()

# Fonction de récupération de l'utilisateur pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route d'inscription (enregistrement)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Vérification si l'utilisateur existe déjà
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email déjà utilisé. Veuillez vous connecter au lieu de cela.', 'danger')
            return redirect(url_for('login'))

        # Création du nouvel utilisateur avec un solde de départ
        new_user = User(username=username, email=email, password=hashed_password, balance=0.00)
        db.session.add(new_user)
        db.session.commit()

        flash('Votre compte a été créé avec succès !', 'success')
        login_user(new_user)  # Connexion immédiate de l'utilisateur après l'inscription
        return redirect(url_for('dashboard'))  # Redirige vers le tableau de bord

    return render_template('register.html')  # Afficher le formulaire d'inscription

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Chercher l'utilisateur dans la base de données
        user = User.query.filter_by(email=email).first()

        # Vérification des informations d'identification
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)  # Connecter l'utilisateur
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))  # Rediriger vers le tableau de bord
        else:
            flash('Échec de la connexion. Vérifiez votre email et votre mot de passe.', 'danger')

    return render_template('login.html')  # Afficher le formulaire de connexion

# Route du tableau de bord (protégée, nécessite une connexion)
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Bienvenue sur votre tableau de bord, {current_user.username}! Votre solde actuel est {current_user.balance} €."

# Route de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Déconnecter l'utilisateur
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))  # Rediriger vers la page de connexion

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
