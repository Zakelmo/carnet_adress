"""
Fichier de configuration pour l'application Cabinet Médical
Gestion des paramètres email et WhatsApp
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()


class Config:
    """Configuration centralisée de l'application"""
    
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    
    # Configuration Base de données
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'contacts.db')
    
    # Configuration Email (SMTP)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
    
    # Email par défaut de l'expéditeur
    DEFAULT_SENDER_EMAIL = os.getenv('DEFAULT_SENDER_EMAIL', SMTP_USERNAME)
    DEFAULT_SENDER_NAME = os.getenv('DEFAULT_SENDER_NAME', 'Cabinet Médical')
    
    # Configuration WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    
    # Limites d'envoi (protection anti-spam)
    MAX_EMAILS_PER_HOUR = int(os.getenv('MAX_EMAILS_PER_HOUR', 50))
    MAX_WHATSAPP_PER_HOUR = int(os.getenv('MAX_WHATSAPP_PER_HOUR', 30))
    
    # Templates de messages par défaut
    MESSAGE_TEMPLATES = {
        'rappel_rdv': {
            'sujet': 'Rappel de rendez-vous',
            'corps': '''Bonjour {nom},

Ceci est un rappel pour votre rendez-vous prévu le {date} à {heure}.

Merci de confirmer votre présence.

Cordialement,
{cabinet_name}'''
        },
        'resultats': {
            'sujet': 'Résultats d\'examens disponibles',
            'corps': '''Bonjour {nom},

Vos résultats d\'examens sont disponibles.
Merci de contacter le cabinet pour plus d\'informations.

Cordialement,
{cabinet_name}'''
        },
        'confirmation': {
            'sujet': 'Confirmation de rendez-vous',
            'corps': '''Bonjour {nom},

Votre rendez-vous a été confirmé pour le {date} à {heure}.

À bientôt,
{cabinet_name}'''
        },
        'information': {
            'sujet': 'Information importante',
            'corps': '''Bonjour {nom},

{message}

Cordialement,
{cabinet_name}'''
        }
    }
    
    @staticmethod
    def is_email_configured():
        """Vérifie si la configuration email est complète"""
        return bool(Config.SMTP_USERNAME and Config.SMTP_PASSWORD)
    
    @staticmethod
    def is_whatsapp_configured():
        """Vérifie si la configuration WhatsApp est complète"""
        return bool(Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN)
    
    @staticmethod
    def get_template(template_name):
        """Récupère un template de message"""
        return Config.MESSAGE_TEMPLATES.get(template_name, None)
