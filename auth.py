"""
Module d'authentification des utilisateurs avec gestion des rôles
"""

import hashlib
import os


class Role:
    """Classe pour définir les rôles disponibles"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    
    @staticmethod
    def all_roles():
        """Retourne tous les rôles disponibles"""
        return [Role.USER, Role.ADMIN, Role.SUPER_ADMIN]
    
    @staticmethod
    def get_role_name(role):
        """Retourne le nom en français du rôle"""
        names = {
            Role.USER: "Utilisateur",
            Role.ADMIN: "Administrateur",
            Role.SUPER_ADMIN: "Super Administrateur"
        }
        return names.get(role, "Inconnu")


class AuthManager:
    """Classe pour gérer l'authentification et les rôles des utilisateurs"""
    
    def __init__(self, fichier_users="users.txt"):
        """
        Initialise le gestionnaire d'authentification
        
        Args:
            fichier_users (str): Nom du fichier stockant les utilisateurs
        """
        self.fichier_users = fichier_users
        self.users = {}  # Format: {username: {'password_hash': str, 'role': str}}
        self.charger_users()
        self.creer_super_admin_initial()
    
    def hash_password(self, password):
        """
        Hash un mot de passe avec SHA-256
        
        Args:
            password (str): Mot de passe en clair
        
        Returns:
            str: Hash du mot de passe
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def charger_users(self):
        """Charge les utilisateurs depuis le fichier"""
        if not os.path.exists(self.fichier_users):
            return
        
        try:
            with open(self.fichier_users, 'r', encoding='utf-8') as f:
                for ligne in f:
                    ligne = ligne.strip()
                    if ligne:
                        parties = ligne.split('|')
                        if len(parties) == 3:
                            username, password_hash, role = parties
                            self.users[username] = {
                                'password_hash': password_hash,
                                'role': role
                            }
                        elif len(parties) == 2:  # Migration ancien format
                            username, password_hash = parties
                            self.users[username] = {
                                'password_hash': password_hash,
                                'role': Role.USER
                            }
        except Exception as e:
            print(f"⚠ Erreur lors du chargement des utilisateurs: {e}")
    
    def sauvegarder_users(self):
        """Sauvegarde les utilisateurs dans le fichier"""
        try:
            with open(self.fichier_users, 'w', encoding='utf-8') as f:
                for username, data in self.users.items():
                    f.write(f"{username}|{data['password_hash']}|{data['role']}\n")
        except Exception as e:
            print(f"⚠ Erreur lors de la sauvegarde des utilisateurs: {e}")
    
    def creer_super_admin_initial(self):
        """
        Vérifie si un super admin existe.
        Si aucun n'existe, l'utilisateur devra en créer un via l'interface web.
        """
        # Vérifier si un super admin existe déjà
        for username, data in self.users.items():
            if data['role'] == Role.SUPER_ADMIN:
                return
        
        # Aucun super admin n'existe - Message d'information
        print("\n" + "="*60)
        print("ℹ️  PREMIÈRE UTILISATION")
        print("="*60)
        print("Aucun Super Administrateur trouvé.")
        print("Visitez http://localhost:5000/register pour créer le premier compte.")
        print("="*60 + "\n")
    
    def creer_compte(self, username, password, role=Role.USER, created_by_role=None, patient_info=None):
        """
        Crée un nouveau compte utilisateur
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            role (str): Rôle de l'utilisateur
            created_by_role (str): Rôle de la personne qui crée le compte
            patient_info (dict): Informations du patient (nom, email, telephone) - requis pour USER
        
        Returns:
            tuple: (succès (bool), message (str))
        """
        if not username or not password:
            return False, "Le nom d'utilisateur et le mot de passe sont obligatoires!"
        
        if username in self.users:
            return False, "Ce nom d'utilisateur existe déjà!"
        
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères!"
        
        # RÈGLE: Un seul Super Admin autorisé dans le système
        if role == Role.SUPER_ADMIN:
            # Vérifier si un super admin existe déjà
            for user_data in self.users.values():
                if user_data['role'] == Role.SUPER_ADMIN:
                    return False, "Un Super Administrateur existe déjà! Un seul Super Admin est autorisé par système."
        
        # RÈGLE NOUVELLE: Pour créer un compte USER, le patient doit déjà être enregistré
        # Cela s'applique aussi bien pour l'auto-inscription (created_by_role=None) que pour la création par Admin
        if role == Role.USER:
            if not patient_info:
                return False, "Les informations du patient sont requises pour créer un compte utilisateur!"
            
            # Vérifier que le patient existe dans la base de données
            from address_book import AddressBook
            carnet = AddressBook()
            patient_existe, patient_data = carnet.patient_existe(
                nom=patient_info.get('nom'),
                email=patient_info.get('email'),
                telephone=patient_info.get('telephone')
            )
            
            if not patient_existe:
                return False, "Ce patient n'existe pas dans le système. Veuillez d'abord enregistrer le patient avant de créer un compte utilisateur."
        
        # Vérification des permissions de création
        if created_by_role == Role.ADMIN and role == Role.ADMIN:
            return False, "Les administrateurs ne peuvent pas créer d'autres administrateurs!"
        
        if created_by_role == Role.ADMIN and role == Role.SUPER_ADMIN:
            return False, "Les administrateurs ne peuvent pas créer de super administrateurs!"
        
        if created_by_role == Role.USER:
            return False, "Les utilisateurs ne peuvent pas créer de comptes!"
        
        password_hash = self.hash_password(password)
        self.users[username] = {
            'password_hash': password_hash,
            'role': role
        }
        self.sauvegarder_users()
        
        return True, "Compte créé avec succès!"
    
    def authentifier(self, username, password):
        """
        Authentifie un utilisateur
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
        
        Returns:
            bool: True si l'authentification réussit, False sinon
        """
        if username not in self.users:
            return False
        
        password_hash = self.hash_password(password)
        return self.users[username]['password_hash'] == password_hash
    
    def get_user_role(self, username):
        """
        Récupère le rôle d'un utilisateur
        
        Args:
            username (str): Nom d'utilisateur
        
        Returns:
            str: Le rôle de l'utilisateur ou None
        """
        if username in self.users:
            return self.users[username]['role']
        return None
    
    def modifier_user(self, username, new_password=None, new_role=None, modified_by_username=None):
        """
        Modifie un utilisateur existant
        
        Args:
            username (str): Nom d'utilisateur à modifier
            new_password (str): Nouveau mot de passe (optionnel)
            new_role (str): Nouveau rôle (optionnel)
            modified_by_username (str): Utilisateur qui effectue la modification
        
        Returns:
            tuple: (succès (bool), message (str))
        """
        if username not in self.users:
            return False, "Utilisateur introuvable!"
        
        modifier_role = self.get_user_role(modified_by_username)
        
        # Utilisateur peut seulement modifier son propre mot de passe
        if modifier_role == Role.USER and username != modified_by_username:
            return False, "Vous ne pouvez modifier que votre propre compte!"
        
        # Utilisateur ne peut pas changer son rôle
        if modifier_role == Role.USER and new_role is not None:
            return False, "Vous ne pouvez pas modifier votre rôle!"
        
        # Admin ne peut pas modifier les super admins
        if modifier_role == Role.ADMIN and self.users[username]['role'] == Role.SUPER_ADMIN:
            return False, "Les administrateurs ne peuvent pas modifier les super administrateurs!"
        
        # Mettre à jour le mot de passe si fourni
        if new_password:
            if len(new_password) < 8:
                return False, "Le mot de passe doit contenir au moins 8 caractères!"
            self.users[username]['password_hash'] = self.hash_password(new_password)
        
        # Mettre à jour le rôle si fourni
        if new_role and new_role in Role.all_roles():
            self.users[username]['role'] = new_role
        
        self.sauvegarder_users()
        return True, "Utilisateur modifié avec succès!"
    
    def supprimer_user(self, username, deleted_by_username):
        """
        Supprime un utilisateur
        
        Args:
            username (str): Nom d'utilisateur à supprimer
            deleted_by_username (str): Utilisateur qui effectue la suppression
        
        Returns:
            tuple: (succès (bool), message (str))
        """
        if username not in self.users:
            return False, "Utilisateur introuvable!"
        
        deleter_role = self.get_user_role(deleted_by_username)
        
        # Utilisateurs ne peuvent pas supprimer de comptes
        if deleter_role == Role.USER:
            return False, "Vous n'avez pas la permission de supprimer des comptes!"
        
        # Admin ne peut pas supprimer les super admins
        if deleter_role == Role.ADMIN and self.users[username]['role'] == Role.SUPER_ADMIN:
            return False, "Les administrateurs ne peuvent pas supprimer les super administrateurs!"
        
        # Ne peut pas se supprimer soi-même
        if username == deleted_by_username:
            return False, "Vous ne pouvez pas supprimer votre propre compte!"
        
        del self.users[username]
        self.sauvegarder_users()
        return True, "Utilisateur supprimé avec succès!"
    
    def lister_users(self, requester_role):
        """
        Liste tous les utilisateurs (selon les permissions)
        
        Args:
            requester_role (str): Rôle de celui qui demande la liste
        
        Returns:
            list: Liste des utilisateurs avec leurs informations
        """
        if requester_role not in [Role.ADMIN, Role.SUPER_ADMIN]:
            return []
        
        users_list = []
        for username, data in self.users.items():
            users_list.append({
                'username': username,
                'role': data['role'],
                'role_name': Role.get_role_name(data['role'])
            })
        
        return sorted(users_list, key=lambda x: x['username'])
    
    def utilisateur_existe(self, username):
        """
        Vérifie si un utilisateur existe
        
        Args:
            username (str): Nom d'utilisateur
        
        Returns:
            bool: True si l'utilisateur existe
        """
        return username in self.users
    
    def nombre_users(self):
        """Retourne le nombre d'utilisateurs enregistrés"""
        return len(self.users)
    
    def can_create_user(self, role):
        """Vérifie si un rôle peut créer des utilisateurs"""
        return role in [Role.ADMIN, Role.SUPER_ADMIN]
    
    def can_modify_users(self, role):
        """Vérifie si un rôle peut modifier des utilisateurs"""
        return role in [Role.ADMIN, Role.SUPER_ADMIN]
    
    def can_delete_users(self, role):
        """Vérifie si un rôle peut supprimer des utilisateurs"""
        return role in [Role.ADMIN, Role.SUPER_ADMIN]
    
    def can_manage_database(self, role):
        """Vérifie si un rôle peut gérer la base de données"""
        return role == Role.SUPER_ADMIN
