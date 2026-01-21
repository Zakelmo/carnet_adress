"""
Module de communication par WhatsApp pour le cabinet médical
Utilise l'API Twilio pour envoyer des messages WhatsApp aux patients
"""

from datetime import datetime
import sqlite3
import re
from config import Config


class WhatsAppService:
    """Service d'envoi de messages WhatsApp pour le cabinet médical"""
    
    def __init__(self, db_name=None):
        """
        Initialise le service WhatsApp
        
        Args:
            db_name (str): Nom de la base de données pour l'historique
        """
        self.db_name = db_name or Config.DATABASE_NAME
        self.account_sid = Config.TWILIO_ACCOUNT_SID
        self.auth_token = Config.TWILIO_AUTH_TOKEN
        self.whatsapp_number = Config.TWILIO_WHATSAPP_NUMBER
        self.client = None
        
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                print(f"⚠ Erreur lors de l'initialisation du client Twilio: {e}")
    
    def verifier_configuration(self):
        """
        Vérifie si la configuration WhatsApp est complète (mode simulation - toujours OK)
        
        Returns:
            tuple: (bool, str) - (configuré, message)
        """
        # Mode simulation: toujours configuré
        return True, "Configuration WhatsApp OK"
    
    def valider_numero_telephone(self, numero):
        """
        Valide et formate un numéro de téléphone pour WhatsApp
        
        Args:
            numero (str): Numéro de téléphone à valider
        
        Returns:
            tuple: (bool, str) - (valide, numéro_formaté ou message d'erreur)
        """
        # Nettoyer le numéro
        numero_clean = re.sub(r'[^\d+]', '', numero)
        
        # Vérifier si le numéro commence par +
        if not numero_clean.startswith('+'):
            # Si le numéro commence par 0 (Maroc), remplacer par +212
            if numero_clean.startswith('0'):
                numero_clean = '+212' + numero_clean[1:]
            else:
                return False, "Le numéro doit commencer par + ou 0"
        
        # Vérifier la longueur minimale
        if len(numero_clean) < 10:
            return False, "Numéro de téléphone trop court"
        
        # Format WhatsApp
        whatsapp_number = f"whatsapp:{numero_clean}"
        return True, whatsapp_number
    
    def envoyer_message(self, numero_telephone, nom_destinataire, message, 
                       sent_by=None, contact_nom=None):
        """
        SIMULATION - Envoie un message WhatsApp à un destinataire
        
        Args:
            numero_telephone (str): Numéro de téléphone du destinataire
            nom_destinataire (str): Nom du destinataire
            message (str): Contenu du message
            sent_by (str): Nom d'utilisateur de l'expéditeur
            contact_nom (str): Nom du contact pour l'historique
        
        Returns:
            tuple: (bool, str) - (succès, message)
        """
        # Valider le numéro
        numero_valide, numero_formate = self.valider_numero_telephone(numero_telephone)
        if not numero_valide:
            return False, f"Numéro invalide: {numero_formate}"
        
        try:
            # SIMULATION: Pas d'envoi réel, juste enregistrement dans l'historique
            # Enregistrer dans l'historique
            self._enregistrer_communication(
                contact_nom=contact_nom or nom_destinataire,
                type_communication='whatsapp',
                destinataire=numero_telephone,
                sujet='Message WhatsApp',
                message=message,
                statut='envoyé',
                sent_by=sent_by,
                message_id=f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            return True, f"✅ Message WhatsApp envoyé avec succès à {nom_destinataire} ({numero_telephone})"
        
        except Exception as e:
            return False, f"Erreur lors de la simulation: {str(e)}"
    
    def envoyer_message_template(self, numero_telephone, nom_destinataire, 
                                template_name, variables=None, sent_by=None,
                                contact_nom=None):
        """
        Envoie un message WhatsApp en utilisant un template prédéfini
        
        Args:
            numero_telephone (str): Numéro de téléphone du destinataire
            nom_destinataire (str): Nom du destinataire
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
            'nom': nom_destinataire,
            'cabinet_name': Config.DEFAULT_SENDER_NAME
        }
        
        # Fusionner avec les variables fournies
        if variables:
            default_vars.update(variables)
        
        # Pour WhatsApp, on utilise seulement le corps du template
        try:
            message = template['corps'].format(**default_vars)
        except KeyError as e:
            return False, f"Variable manquante dans le template: {str(e)}"
        
        return self.envoyer_message(
            numero_telephone,
            nom_destinataire,
            message,
            sent_by=sent_by,
            contact_nom=contact_nom
        )
    
    def envoyer_messages_groupes(self, destinataires, message, sent_by=None):
        """
        Envoie un message WhatsApp à plusieurs destinataires
        
        Args:
            destinataires (list): Liste de tuples (numero, nom, contact_nom)
            message (str): Contenu du message
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
            numero, nom, contact_nom = dest
            succes, msg = self.envoyer_message(
                numero, nom, message, sent_by=sent_by, contact_nom=contact_nom
            )
            
            if succes:
                resultats['succes'] += 1
            else:
                resultats['echecs'] += 1
            
            resultats['details'].append({
                'destinataire': numero,
                'nom': nom,
                'succes': succes,
                'message': msg
            })
        
        return resultats
    
    def _enregistrer_communication(self, contact_nom, type_communication, 
                                   destinataire, sujet, message, statut, 
                                   sent_by, message_id=None):
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
            message_id (str): ID du message Twilio (optionnel)
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO communications 
                (contact_nom, type, destinataire, sujet, message, statut, sent_by, 
                 date_envoi, message_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (contact_nom, type_communication, destinataire, sujet, message, 
                  statut, sent_by, datetime.now(), message_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠ Erreur lors de l'enregistrement de la communication: {e}")
    
    def get_historique(self, contact_nom=None, limite=50):
        """
        Récupère l'historique des messages WhatsApp envoyés
        
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
                           statut, sent_by, date_envoi, message_id
                    FROM communications
                    WHERE contact_nom = ? AND type = 'whatsapp'
                    ORDER BY date_envoi DESC
                    LIMIT ?
                """, (contact_nom, limite))
            else:
                cursor.execute("""
                    SELECT contact_nom, type, destinataire, sujet, message, 
                           statut, sent_by, date_envoi, message_id
                    FROM communications
                    WHERE type = 'whatsapp'
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
                    'date_envoi': row[7],
                    'message_id': row[8]
                })
            
            conn.close()
            return resultats
            
        except Exception as e:
            print(f"⚠ Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def verifier_statut_message(self, message_id):
        """
        Vérifie le statut d'un message envoyé via Twilio
        
        Args:
            message_id (str): ID du message Twilio
        
        Returns:
            tuple: (bool, str) - (succès, statut)
        """
        if not self.client:
            return False, "Client Twilio non initialisé"
        
        try:
            message = self.client.messages(message_id).fetch()
            return True, message.status
        except Exception as e:
            return False, f"Erreur: {str(e)}"
