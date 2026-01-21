"""
Module de communication par email pour le cabinet médical
Permet l'envoi d'emails aux patients avec templates et historique
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import sqlite3
from config import Config


class EmailService:
    """Service d'envoi d'emails pour le cabinet médical"""
    
    def __init__(self, db_name=None):
        """
        Initialise le service d'email
        
        Args:
            db_name (str): Nom de la base de données pour l'historique
        """
        self.db_name = db_name or Config.DATABASE_NAME
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.smtp_username = Config.SMTP_USERNAME
        self.smtp_password = Config.SMTP_PASSWORD
        self.smtp_use_tls = Config.SMTP_USE_TLS
        self.sender_email = Config.DEFAULT_SENDER_EMAIL
        self.sender_name = Config.DEFAULT_SENDER_NAME
        
    def verifier_configuration(self):
        """
        Vérifie si la configuration email est complète (mode simulation - toujours OK)
        
        Returns:
            tuple: (bool, str) - (configuré, message)
        """
        # Mode simulation: toujours configuré
        return True, "Configuration email OK (mode simulation)"
    
    def envoyer_email(self, destinataire_email, destinataire_nom, sujet, corps, 
                      pieces_jointes=None, sent_by=None, contact_nom=None):
        """
        SIMULATION - Envoie un email à un destinataire (mode simulation)
        
        Args:
            destinataire_email (str): Email du destinataire
            destinataire_nom (str): Nom du destinataire
            sujet (str): Sujet de l'email
            corps (str): Corps du message (texte ou HTML)
            pieces_jointes (list): Liste de chemins de fichiers à joindre
            sent_by (str): Nom d'utilisateur de l'expéditeur
            contact_nom (str): Nom du contact pour l'historique
        
        Returns:
            tuple: (bool, str) - (succès, message)
        """
        # SIMULATION: Pas d'envoi réel, juste enregistrement dans l'historique
        try:
            # Enregistrer dans l'historique
            self._enregistrer_communication(
                contact_nom=contact_nom or destinataire_nom,
                type_communication='email',
                destinataire=destinataire_email,
                sujet=sujet,
                message=corps,
                statut='envoyé',
                sent_by=sent_by
            )
            
            return True, f"✅ Email envoyé avec succès à {destinataire_nom} ({destinataire_email})"
            
        except Exception as e:
            return False, f"Erreur lors de la simulation: {str(e)}"
    
    def envoyer_email_template(self, destinataire_email, destinataire_nom, 
                               template_name, variables=None, sent_by=None, 
                               contact_nom=None):
        """
        Envoie un email en utilisant un template prédéfini
        
        Args:
            destinataire_email (str): Email du destinataire
            destinataire_nom (str): Nom du destinataire
            template_name (str): Nom du template à utiliser
            variables (dict): Variables à injecter dans le template
            sent_by (str): Nom d'utilisateur de l'expéditeur
            contact_nom (str): Nom du contact pour l'historique
        
        Returns:
            tuple: (bool, str) - (succès, message)
        """
        template = Config.get_template(template_name)
        if not template:
            return False, f"Template '{template_name}' introuvable"
        
        # Variables par défaut
        default_vars = {
            'nom': destinataire_nom,
            'cabinet_name': self.sender_name
        }
        
        # Fusionner avec les variables fournies
        if variables:
            default_vars.update(variables)
        
        # Remplacer les variables dans le template
        try:
            sujet = template['sujet'].format(**default_vars)
            corps = template['corps'].format(**default_vars)
        except KeyError as e:
            return False, f"Variable manquante dans le template: {str(e)}"
        
        return self.envoyer_email(
            destinataire_email, 
            destinataire_nom, 
            sujet, 
            corps, 
            sent_by=sent_by,
            contact_nom=contact_nom
        )
    
    def envoyer_emails_groupes(self, destinataires, sujet, corps, sent_by=None):
        """
        Envoie un email à plusieurs destinataires
        
        Args:
            destinataires (list): Liste de tuples (email, nom, contact_nom)
            sujet (str): Sujet de l'email
            corps (str): Corps du message
            sent_by (str): Nom d'utilisateur de l'expéditeur
        
        Returns:
            dict: Résultats avec compteurs de succès/échecs
        """
        resultats = {
            'total': len(destinataires),
            'succes': 0,
            'echecs': 0,
            'details': []
        }
        
        for dest in destinataires:
            email, nom, contact_nom = dest
            succes, message = self.envoyer_email(
                email, nom, sujet, corps, sent_by=sent_by, contact_nom=contact_nom
            )
            
            if succes:
                resultats['succes'] += 1
            else:
                resultats['echecs'] += 1
            
            resultats['details'].append({
                'destinataire': email,
                'nom': nom,
                'succes': succes,
                'message': message
            })
        
        return resultats
    
    def _enregistrer_communication(self, contact_nom, type_communication, 
                                   destinataire, sujet, message, statut, sent_by):
        """
        Enregistre une communication dans l'historique
        
        Args:
            contact_nom (str): Nom du contact
            type_communication (str): Type (email ou whatsapp)
            destinataire (str): Email ou numéro de téléphone
            sujet (str): Sujet du message
            message (str): Contenu du message
            statut (str): Statut (envoyé, échec, etc.)
            sent_by (str): Utilisateur ayant envoyé le message
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO communications 
                (contact_nom, type, destinataire, sujet, message, statut, sent_by, date_envoi)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (contact_nom, type_communication, destinataire, sujet, message, 
                  statut, sent_by, datetime.now()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠ Erreur lors de l'enregistrement de la communication: {e}")
    
    def get_historique(self, contact_nom=None, limite=50):
        """
        Récupère l'historique des emails envoyés
        
        Args:
            contact_nom (str): Filtrer par nom de contact (optionnel)
            limite (int): Nombre maximum de résultats
        
        Returns:
            list: Liste des communications
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if contact_nom:
                cursor.execute("""
                    SELECT contact_nom, type, destinataire, sujet, message, 
                           statut, sent_by, date_envoi
                    FROM communications
                    WHERE contact_nom = ? AND type = 'email'
                    ORDER BY date_envoi DESC
                    LIMIT ?
                """, (contact_nom, limite))
            else:
                cursor.execute("""
                    SELECT contact_nom, type, destinataire, sujet, message, 
                           statut, sent_by, date_envoi
                    FROM communications
                    WHERE type = 'email'
                    ORDER BY date_envoi DESC
                    LIMIT ?
                """, (limite,))
            
            resultats = []
            for row in cursor.fetchall():
                resultats.append({
                    'contact_nom': row[0],
                    'type': row[1],
                    'destinataire': row[2],
                    'sujet': row[3],
                    'message': row[4],
                    'statut': row[5],
                    'sent_by': row[6],
                    'date_envoi': row[7]
                })
            
            conn.close()
            return resultats
            
        except Exception as e:
            print(f"⚠ Erreur lors de la récupération de l'historique: {e}")
            return []
