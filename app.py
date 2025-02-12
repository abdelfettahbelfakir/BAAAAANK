from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pymysql
from datetime import datetime

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

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Clé étrangère vers User
    type_operation = db.Column(db.String(50), nullable=False)  # Type d'opération : dépôt, retrait, etc.
    amount = db.Column(db.Float, nullable=False)  # Montant de l'opération
    date_operation = db.Column(db.DateTime, default=datetime.utcnow)  # Date de l'opération
    
    # Relation entre l'utilisateur et l'opération (un utilisateur peut avoir plusieurs opérations)
    user = db.relationship('User', backref=db.backref('operations', lazy=True))

    def __repr__(self):
        return f'<Operation {self.type_operation} of {self.amount} by {self.user.username}>'

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        if amount > 0:
            # Mettre à jour le solde de l'utilisateur
            current_user.balance += amount

            # Créer une nouvelle opération
            operation = Operation(user_id=current_user.id, type_operation='Dépôt', amount=amount)
            db.session.add(operation)
            db.session.commit()

            flash(f'Dépôt de {amount} effectué avec succès.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Le montant doit être supérieur à zéro.', 'danger')

    return render_template('deposit.html')
@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        if amount > 0 and current_user.balance >= amount:
            # Mettre à jour le solde de l'utilisateur
            current_user.balance -= amount

            # Créer une nouvelle opération
            operation = Operation(user_id=current_user.id, type_operation='Retrait', amount=amount)
            db.session.add(operation)
            db.session.commit()

            flash(f'Retrait de {amount} effectué avec succès.', 'success')
            return redirect(url_for('dashboard'))
        elif amount <= 0:
            flash('Le montant doit être supérieur à zéro.', 'danger')
        else:
            flash('Solde insuffisant pour effectuer le retrait.', 'danger')

    return render_template('withdraw.html')
@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        to_email = request.form['to_email']
        amount = float(request.form['amount'])

        # Vérifier si l'utilisateur existe
        to_user = User.query.filter_by(email=to_email).first()

        if to_user and amount > 0 and current_user.balance >= amount:
            # Mettre à jour les soldes des utilisateurs
            current_user.balance -= amount
            to_user.balance += amount

            # Créer deux nouvelles opérations (une pour l'expéditeur et une pour le destinataire)
            operation_from = Operation(user_id=current_user.id, type_operation='Transfert', amount=amount)
            operation_to = Operation(user_id=to_user.id, type_operation='Réception', amount=amount)
            db.session.add(operation_from)
            db.session.add(operation_to)
            db.session.commit()

            flash(f'Transfert de {amount} vers {to_user.username} effectué avec succès.', 'success')
            return redirect(url_for('dashboard'))
        elif amount <= 0:
            flash('Le montant doit être supérieur à zéro.', 'danger')
        elif not to_user:
            flash('L\'utilisateur destinataire n\'existe pas.', 'danger')
        else:
            flash('Solde insuffisant pour effectuer le transfert.', 'danger')

    return render_template('transfer.html')


# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
