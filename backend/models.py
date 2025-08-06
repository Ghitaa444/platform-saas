from backend.database import db
from datetime import datetime, timedelta 
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint

class User(db.Model):
    
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    containers = db.relationship('Container', backref='owner', lazy=True, cascade="all, delete-orphan")

    # Colonnes pour la fonctionnalité de réinitialisation de mot de passe
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expires_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        # Hache le mot de passe et le stocke.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Vérifie un mot de passe haché par rapport à une entrée en clair.
        return check_password_hash(self.password_hash, password)
    
    def set_reset_token(self, token: str, expires_in_minutes: int = 30):
        # Définit le token de réinitialisation et son expiration.
        self.reset_token = token
        self.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

    def clear_reset_token(self):
        # Efface le token de réinitialisation et son expiration.
        self.reset_token = None
        self.reset_token_expires_at = None

    def __repr__(self):
        # Représentation en chaîne de caractères pour le débogage.
        return f'<User {self.username}>'

class Container(db.Model):
    # Définit le modèle de base de données pour les conteneurs Docker associés aux utilisateurs.
    __tablename__ = 'container'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Clé étrangère vers la table 'user'
    name = db.Column(db.String(100), nullable=False) 
    image = db.Column(db.String(200), nullable=False) 
    docker_container_id = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(50), default='created') 
    ports = db.Column(db.String(255), nullable=True) 
    environment = db.Column(db.JSON, nullable=True, default=dict) 

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Contrainte d'unicité pour s'assurer qu'un utilisateur n'a pas deux conteneurs avec le même nom.
    __table_args__ = (UniqueConstraint('user_id', 'name', name='_user_container_name_uc'),)
    
    def __repr__(self):
        # Représentation en chaîne de caractères pour le débogage.
        return f'<Container {self.name} by User {self.user_id}>'