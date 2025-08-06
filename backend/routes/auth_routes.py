import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from backend.database import db
from backend.models import User
from backend.schemas import (
    user_register_schema, user_login_schema, user_schema,
    ForgotPasswordRequestSchema, ResetPasswordSchema
)
from sqlalchemy.exc import IntegrityError
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Blueprint pour les routes d'authentification
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

def send_reset_email(user_email: str, token: str):
    """
    Simule l'envoi d'un email de réinitialisation de mot de passe à l'utilisateur.
    Construit le lien de réinitialisation en utilisant l'URL frontend configurée.
    """
    frontend_reset_url = current_app.config.get(
        'FRONTEND_RESET_PASSWORD_URL',
        'http://localhost:3000/reset-password' # URL par défaut pour le développement
    )
    reset_link = f"{frontend_reset_url}?token={token}"
    logger.info(f"Préparation de l'email de réinitialisation pour {user_email}. Lien: {reset_link}")
    print(f"SIMULATION EMAIL: Envoyé à {user_email} avec le lien: {reset_link}") # Affichage console pour le débogage
    logger.debug(f"Email de réinitialisation simulé pour {user_email}")
    # TODO: Intégrer un véritable service d'envoi d'emails ici

# Route pour enregistrer un nouvel utilisateur
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Gère l'enregistrement d'un nouvel utilisateur.
    Valide les données, crée l'utilisateur dans la base de données et renvoie un token JWT.
    """
    json_data = request.get_json()
    if not json_data:
        logger.warning("Tentative d'enregistrement sans données JSON.")
        return jsonify({"msg": "Données JSON requises"}), 400

    try:
        # Validation des données entrantes avec Marshmallow
        validated_data = user_register_schema.load(json_data)
    except ValidationError as err:
        logger.warning(f"Erreurs de validation lors de l'enregistrement: {err.messages}")
        return jsonify({"msg": "Erreurs de validation", "errors": err.messages}), 400

    username = validated_data['username']
    email = validated_data['email']
    password = validated_data['password']

    try:
        # Vérification si le nom d'utilisateur ou l'email existe déjà
        if User.query.filter_by(username=username).first():
            logger.warning(f"Tentative d'enregistrement avec un nom d'utilisateur existant: {username}")
            return jsonify({"msg": "Nom d'utilisateur déjà existant"}), 409
        if User.query.filter_by(email=email).first():
            logger.warning(f"Tentative d'enregistrement avec un email existant: {email}")
            return jsonify({"msg": "Email déjà existant"}), 409

        # Création et ajout du nouvel utilisateur à la base de données
        logger.info(f"Initiation de la création de l'utilisateur: {username}")
        new_user = User(username=username, email=email)
        new_user.set_password(password) # Hache le mot de passe
        db.session.add(new_user)
        db.session.commit() # Sauvegarde l'utilisateur dans la base de données
        logger.info(f"Utilisateur '{username}' créé avec succès, ID: {new_user.id}")

        # Génération d'un token JWT pour l'utilisateur fraîchement enregistré
        access_token = create_access_token(identity=str(new_user.id))
        return jsonify({
            "msg": "Utilisateur enregistré avec succès",
            "user": user_schema.dump(new_user), # Sérialise l'objet utilisateur pour la réponse
            "access_token": access_token
        }), 201

    except IntegrityError:
        # Gère les erreurs d'intégrité de la base de données (doublons non capturés avant le commit)
        db.session.rollback()
        logger.error(f"Erreur d'intégrité de la base de données lors de l'enregistrement pour {username}/{email}")
        return jsonify({"msg": "Nom d'utilisateur ou email déjà existant"}), 409
    except Exception as e:
        db.session.rollback()
        logger.critical(f"Erreur inattendue lors de l'enregistrement de l'utilisateur: {e}", exc_info=True)
        return jsonify({"msg": "Erreur interne du serveur"}), 500

# Route pour authentifier un utilisateur et renvoyer un token JWT
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Gère la connexion de l'utilisateur.
    Valide les identifiants, authentifie l'utilisateur et renvoie un token d'accès JWT.
    """
    json_data = request.get_json()
    if not json_data:
        logger.warning("Tentative de connexion sans données JSON.")
        return jsonify({"msg": "Données JSON requises"}), 400

    try:
        # Validation des données entrantes avec Marshmallow
        validated_data = user_login_schema.load(json_data)
    except ValidationError as err:
        logger.warning(f"Erreurs de validation lors de la connexion: {err.messages}")
        return jsonify({"msg": "Erreurs de validation", "errors": err.messages}), 400

    username = validated_data['username']
    password = validated_data['password']

    # Recherche de l'utilisateur par nom d'utilisateur
    user = User.query.filter_by(username=username).first()

    # Vérification du mot de passe
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id)) # Génère un token JWT
        logger.info(f"Utilisateur '{username}' connecté avec succès.")
        return jsonify(access_token=access_token), 200
    else:
        logger.warning(f"Échec de connexion pour l'utilisateur '{username}' (identifiants invalides).")
        return jsonify({"msg": "Nom d'utilisateur ou mot de passe invalide"}), 401

# Route protégée pour récupérer le profil de l'utilisateur connecté
@auth_bp.route('/profile', methods=['GET'])
@jwt_required() # Cette route nécessite un token JWT valide
def profile():
    """
    Récupère les informations du profil de l'utilisateur connecté.
    Nécessite un token JWT valide dans l'en-tête Authorization.
    """
    current_user_id = get_jwt_identity() # Récupère l'identité (ID utilisateur) du token JWT
    user = User.query.get(current_user_id)

    if not user:
        logger.error(f"Profil utilisateur non trouvé pour l'ID: {current_user_id} (peut-être supprimé ?).")
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    logger.info(f"Accès au profil de l'utilisateur: {user.username} (ID: {current_user_id})")
    return jsonify(user_schema.dump(user)), 200 # Sérialise et renvoie les données du profil

# Route pour initier la procédure de mot de passe oublié (envoi d'un lien de réinitialisation)
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password_request():
    """
    Gère la demande de mot de passe oublié.
    L'utilisateur fournit son email. Si l'email existe, un lien de réinitialisation est envoyé.
    La réponse est générique pour éviter l'énumération des utilisateurs.
    """
    json_data = request.get_json()
    if not json_data:
        logger.warning("Demande de mot de passe oublié sans données JSON.")
        return jsonify({"msg": "Données JSON requises"}), 400

    try:
        # Validation de l'email fourni
        data = ForgotPasswordRequestSchema().load(json_data) # Utilise le nouveau schéma
    except ValidationError as err:
        logger.warning(f"Erreurs de validation lors de la demande de mot de passe oublié: {err.messages}")
        return jsonify(err.messages), 400

    email = data.get('email')
    user = User.query.filter_by(email=email).first()

    # Si l'utilisateur existe, générer et envoyer le token de réinitialisation
    if user:
        try:
            token = secrets.token_urlsafe(32) # Génération du token
            user.reset_token = token
            user.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=30) # Token valide 30 min
            db.session.commit()

            send_reset_email(user.email, token) # Appel de la fonction utilitaire d'envoi d'email simulée
            logger.info(f"Lien de réinitialisation envoyé (simulé) pour l'email: {email}")
        except Exception as e:
            db.session.rollback() # Annule la transaction si quelque chose se passe mal
            logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation pour {email}: {e}", exc_info=True)
            # Ne pas exposer l'erreur à l'utilisateur final pour des raisons de sécurité
            return jsonify({"msg": "Une erreur est survenue lors de l'envoi du lien de réinitialisation."}), 500
    else:
        # Si l'email n'est pas enregistré, ne rien faire mais renvoyer le même message générique
        logger.warning(f"Demande de mot de passe oublié pour un email non enregistré: {email}")

    # Message générique pour éviter l'énumération des utilisateurs (sécurité)
    return jsonify({"msg": "Si cet e-mail est enregistré, un lien de réinitialisation a été envoyé à votre adresse."}), 200

# Route pour mettre à jour le mot de passe après validation du token de réinitialisation
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Permet à l'utilisateur de définir un nouveau mot de passe en utilisant un token de réinitialisation.
    Valide le token, sa date d'expiration, et met à jour le mot de passe de l'utilisateur.
    """
    json_data = request.get_json()
    if not json_data:
        logger.warning("Demande de réinitialisation de mot de passe sans données JSON.")
        return jsonify({"msg": "Données JSON requises"}), 400

    try:
        # Validation du token et du nouveau mot de passe
        data = ResetPasswordSchema().load(json_data) # Utilise le nouveau schéma
    except ValidationError as err:
        logger.warning(f"Erreurs de validation lors de la réinitialisation du mot de passe: {err.messages}")
        return jsonify(err.messages), 400

    token = data.get('token')
    new_password = data.get('new_password') # Assurez-vous que le schéma renvoie 'new_password'

    # Recherche l'utilisateur par le token de réinitialisation
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        logger.warning(f"Tentative de réinitialisation avec un token invalide ou déjà utilisé: {token[:5]}...")
        return jsonify({"msg": "Le lien de réinitialisation est invalide ou a déjà été utilisé."}), 400

    # Vérifie si le token a expiré
    if user.reset_token_expires_at is None or user.reset_token_expires_at < datetime.utcnow():
        # Effacer le token expiré pour le rendre inutilisable à l'avenir
        user.reset_token = None
        user.reset_token_expires_at = None
        db.session.commit()
        logger.warning(f"Tentative de réinitialisation avec un token expiré pour l'utilisateur: {user.email}")
        return jsonify({"msg": "Le lien de réinitialisation a expiré. Veuillez refaire une demande."}), 400

    try:
        # Met à jour le mot de passe de l'utilisateur et efface le token
        user.set_password(new_password) # Utilise la méthode du modèle User pour hacher le nouveau mot de passe
        user.reset_token = None
        user.reset_token_expires_at = None
        db.session.commit()
        logger.info(f"Mot de passe réinitialisé avec succès pour l'utilisateur: {user.username}")
        return jsonify({"msg": "Votre mot de passe a été réinitialisé avec succès."}), 200
    except Exception as e:
        db.session.rollback() # Annule la transaction en cas d'erreur
        logger.critical(f"Erreur inattendue lors de la réinitialisation du mot de passe: {e}", exc_info=True)
        return jsonify({"msg": "Une erreur interne du serveur est survenue lors de la réinitialisation du mot de passe."}), 500