import logging
import secrets 
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from backend.database import db
from backend.models import User
from backend.exceptions import UserNotFoundException, InvalidCredentialsException, APIException, \
    TokenExpiredException, InvalidTokenException
class UserService:
    def __init__(self, app_logger: logging.Logger):
        self.app_logger = app_logger

    def create_user(self, username, email, password):
        """
        Crée un nouvel utilisateur dans la base de données.
        Vérifie l'unicité du nom d'utilisateur et de l'e-mail avant la création.
        """
        try:
            if User.query.filter_by(username=username).first():
                self.app_logger.warning(f"Registration failed: username '{username}' already exists.")
                raise APIException("Le nom d'utilisateur existe déjà.", 409)
            if User.query.filter_by(email=email).first():
                self.app_logger.warning(f"Registration failed: email '{email}' already exists.")
                raise APIException("L'e-mail existe déjà.", 409)

            user = User(username=username, email=email)
            user.set_password(password) 
            db.session.add(user)
            db.session.commit()
            self.app_logger.info(f"Utilisateur '{username}' créé avec succès.")
            return user
        except IntegrityError as e:
            db.session.rollback()
            self.app_logger.error(f"Erreur d'intégrité de la base de données lors de la création de l'utilisateur: {e}", exc_info=True)
            raise APIException("Un utilisateur avec ce nom d'utilisateur ou cet e-mail existe déjà.", 409)
        except Exception as e:
            db.session.rollback()
            self.app_logger.exception("Erreur inattendue lors de la création de l'utilisateur.")
            raise APIException(f"Échec de la création de l'utilisateur: {str(e)}", 500)

    def authenticate_user(self, username, password):
        """
        Authentifie un utilisateur en vérifiant son nom d'utilisateur et son mot de passe.
        """
        user = User.query.filter_by(username=username).first()
        if not user:
            self.app_logger.warning(f"Tentative d'authentification échouée pour l'utilisateur '{username}': utilisateur non trouvé.")
            raise UserNotFoundException("Nom d'utilisateur ou mot de passe invalide.")
        if not user.check_password(password):
            self.app_logger.warning(f"Tentative d'authentification échouée pour l'utilisateur '{username}': mot de passe incorrect.")
            raise InvalidCredentialsException("Nom d'utilisateur ou mot de passe invalide.")
        self.app_logger.info(f"Utilisateur '{username}' authentifié avec succès.")
        return user

    def generate_password_reset_token(self, email: str) -> str:
        """
        Génère un token unique pour la réinitialisation de mot de passe et l'associe à l'utilisateur.
        Retourne le token généré. Si l'email n'existe pas, retourne un token factice pour éviter l'énumération.
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            
            self.app_logger.warning(f"Demande de réinitialisation de mot de passe pour un e-mail non-existant: {email}")
            return secrets.token_urlsafe(32) # Retourne un token aléatoire pour ne pas révéler l'existence de l'email
        
        # Générer un token sécurisé et stockable
        token = secrets.token_urlsafe(32) 
        user.set_reset_token(token, expires_in_minutes=30) # Token valide pour 30 minutes
        db.session.commit()
        self.app_logger.info(f"Token de réinitialisation de mot de passe généré pour l'utilisateur: {user.email}")
        return token

    def reset_password(self, token: str, new_password: str):
        """
        Réinitialise le mot de passe d'un utilisateur en utilisant le token fourni.
        Vérifie la validité et l'expiration du token.
        """
        user = User.query.filter_by(reset_token=token).first()

        if not user:
            self.app_logger.warning(f"Tentative de réinitialisation de mot de passe avec un token invalide ou inexistant: {token[:5]}...")
            raise InvalidTokenException("Token de réinitialisation de mot de passe invalide ou expiré.")
        
        # Vérifier si le token est expiré
        if user.reset_token_expires_at < datetime.utcnow():
            user.clear_reset_token() 
            db.session.commit()
            self.app_logger.warning(f"Tentative de réinitialisation de mot de passe avec un token expiré pour l'utilisateur: {user.email}")
            raise TokenExpiredException("Token de réinitialisation de mot de passe invalide ou expiré.")
        
        user.set_password(new_password) 
        user.clear_reset_token() 
        db.session.commit()
        self.app_logger.info(f"Mot de passe réinitialisé avec succès pour l'utilisateur: {user.email}")