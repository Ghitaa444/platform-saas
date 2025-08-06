import logging
import os
# Ces importations sont commentées car elles ne sont pas utilisées dans la version factice.
# ou une bibliothèque tierce (ex: Flask-Mail, SendGrid, Mailgun).
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, app_logger: logging.Logger):
        self.app_logger = app_logger
        # Les détails de configuration SMTP seraient chargés ici depuis les variables d'environnement
        # self.smtp_server = os.getenv('SMTP_SERVER')
        # self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        # self.smtp_username = os.getenv('SMTP_USERNAME')
        # self.smtp_password = os.getenv('SMTP_PASSWORD')
        # self.sender_email = os.getenv('SENDER_EMAIL')

        # Vérification minimale que les variables d'environnement nécessaires sont définies si on est en prod
        # if os.getenv('FLASK_ENV') == 'production':
        #     if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password, self.sender_email]):
        #         self.app_logger.error("Les variables d'environnement SMTP ne sont pas toutes configurées pour la production.")


    def send_password_reset_email(self, recipient_email: str, reset_link: str):
        """
        Envoie un e-mail contenant le lien de réinitialisation du mot de passe.
        
        NOTE IMPORTANTE: Cette fonction est une IMPLÉMENTATION FACTICE (mock).
        Dans une application réelle, vous devriez configurer un service d'envoi d'e-mails
        avec un fournisseur tel que SendGrid, Mailgun, ou utiliser smtplib avec un serveur SMTP.
        """
        subject = "Demande de Réinitialisation de Mot de Passe pour Votre Compte"
        body = f"""
        Bonjour,

        Vous avez demandé à réinitialiser votre mot de passe.
        Veuillez cliquer sur le lien suivant pour réinitialiser votre mot de passe:

        {reset_link}

        Ce lien expirera dans 30 minutes.

        Si vous n'avez pas demandé de réinitialisation de mot de passe, veuillez ignorer cet e-mail.

        Cordialement,
        Votre Équipe Application
        """
        
        self.app_logger.info(f"Simulation d'envoi d'e-mail de réinitialisation de mot de passe à {recipient_email} avec le lien: {reset_link}")
        
        # CODE D'ENVOI D'E-MAIL RÉEL (EXEMPLE AVEC SMTP LIB) 
        # Décommentez et configurez ceci dans une application de production
        # try:
        #     msg = MIMEMultipart('alternative')
        #     msg['Subject'] = subject
        #     msg['From'] = self.sender_email
        #     msg['To'] = recipient_email

        #     # Ajoutez le corps de l'e-mail
        #     part1 = MIMEText(body, 'plain') # Version texte brut
        #     # part2 = MIMEText(html_body, 'html') # Si vous avez un corps HTML

        #     msg.attach(part1)
        #     # msg.attach(part2)

        #     with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        #         server.starttls() # Utilisez le chiffrement TLS
        #         server.login(self.smtp_username, self.smtp_password)
        #         server.sendmail(self.sender_email, recipient_email, msg.as_string())
        #     self.app_logger.info(f"E-mail de réinitialisation de mot de passe envoyé avec succès à {recipient_email}.")
        # except Exception as e:
        #     self.app_logger.error(f"Échec de l'envoi de l'e-mail de réinitialisation à {recipient_email}: {e}", exc_info=True)
        #     # Vous pourriez vouloir lever une exception ici pour signaler l'échec de l'envoi