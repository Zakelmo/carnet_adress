"""
Module de gestion du carnet d'adresses avec base de données SQLite
"""

import sqlite3
from contact import Contact


class AddressBook:
    """Classe représentant un carnet d'adresses avec SQLite"""
    
    def __init__(self, db_name="contacts.db", username=None):
        """
        Initialise un carnet d'adresses avec une base de données SQLite
        
        Args:
            db_name (str): Nom de la base de données
            username (str): Nom de l'utilisateur (pour filtrer les contacts)
        """
        self.db_name = db_name
        self.username = username
        self.contacts = []
        self.initialiser_db()
        self.charger_contacts()
    
    def initialiser_db(self):
        """Crée les tables contacts et communications si elles n'existent pas"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Table contacts avec champs médicaux et professionnels
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telephone TEXT NOT NULL,
                    username TEXT NOT NULL,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_naissance TEXT,
                    groupe_sanguin TEXT,
                    allergies TEXT,
                    notes TEXT,
                    numero_secu TEXT,
                    categorie TEXT DEFAULT 'Patient',
                    adresse TEXT,
                    ville TEXT,
                    code_postal TEXT,
                    pays TEXT,
                    titre_poste TEXT,
                    entreprise TEXT
                )
            """)
            
            # Table communications pour l'historique des messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS communications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_nom TEXT NOT NULL,
                    type TEXT NOT NULL,
                    destinataire TEXT NOT NULL,
                    sujet TEXT,
                    message TEXT NOT NULL,
                    statut TEXT NOT NULL,
                    sent_by TEXT,
                    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_id TEXT
                )
            """)
            
            # Table appointments pour la gestion des rendez-vous
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_nom TEXT NOT NULL,
                    contact_email TEXT,
                    contact_telephone TEXT,
                    date_rdv TEXT NOT NULL,
                    heure_debut TEXT NOT NULL,
                    heure_fin TEXT NOT NULL,
                    motif TEXT,
                    notes TEXT,
                    statut TEXT DEFAULT 'confirmé',
                    created_by TEXT,
                    created_for TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date_rdv, heure_debut)
                )
            """)
            
            # Vérifier si les colonnes médicales existent déjà dans contacts
            cursor.execute("PRAGMA table_info(contacts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Ajouter les colonnes manquantes si nécessaire
            nouvelles_colonnes = [
                ('date_naissance', 'TEXT'),
                ('groupe_sanguin', 'TEXT'),
                ('allergies', 'TEXT'),
                ('notes', 'TEXT'),
                ('numero_secu', 'TEXT'),
                ('categorie', 'TEXT'),
                ('adresse', 'TEXT'),
                ('ville', 'TEXT'),
                ('code_postal', 'TEXT'),
                ('pays', 'TEXT'),
                ('titre_poste', 'TEXT'),
                ('entreprise', 'TEXT')
            ]
            
            for col_name, col_type in nouvelles_colonnes:
                if col_name not in columns:
                    cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type}")
                    print(f"✓ Colonne '{col_name}' ajoutée à la table contacts")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠ Erreur lors de l'initialisation de la base de données: {e}")
    
    def charger_contacts(self):
        """Charge les contacts depuis la base de données"""
        self.contacts = []
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if self.username:
                cursor.execute(
                    """SELECT nom, email, telephone, date_naissance, groupe_sanguin, 
                       allergies, notes, numero_secu, categorie, adresse, ville, 
                       code_postal, pays, titre_poste, entreprise
                       FROM contacts WHERE username = ? ORDER BY nom""",
                    (self.username,)
                )
            else:
                cursor.execute("""SELECT nom, email, telephone, date_naissance, 
                               groupe_sanguin, allergies, notes, numero_secu, 
                               categorie, adresse, ville, code_postal, pays, 
                               titre_poste, entreprise
                               FROM contacts ORDER BY nom""")
            
            for row in cursor.fetchall():
                nom, email, telephone, date_naissance, groupe_sanguin, allergies, notes, numero_secu, categorie, adresse, ville, code_postal, pays, titre_poste, entreprise = row
                contact = Contact(nom, email, telephone, date_naissance, 
                                groupe_sanguin, allergies, notes, numero_secu,
                                categorie, adresse, ville, code_postal, pays,
                                titre_poste, entreprise)
                self.contacts.append(contact)
            
            conn.close()
        except Exception as e:
            print(f"⚠ Erreur lors du chargement des contacts: {e}")
    
    def ajouter_contact(self, nom, email, telephone, date_naissance=None,
                       groupe_sanguin=None, allergies=None, notes=None, numero_secu=None,
                       categorie=None, adresse=None, ville=None, code_postal=None,
                       pays=None, titre_poste=None, entreprise=None):
        """
        Ajoute un nouveau contact à la base de données
        
        Args:
            nom (str): Le nom du contact
            email (str): L'adresse email du contact
            telephone (str): Le numéro de téléphone du contact
            date_naissance (str): Date de naissance (optionnel)
            groupe_sanguin (str): Groupe sanguin (optionnel)
            allergies (str): Allergies (optionnel)
            notes (str): Notes médicales (optionnel)
            numero_secu (str): Numéro de sécurité sociale (optionnel)
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO contacts 
                (nom, email, telephone, username, date_naissance, groupe_sanguin, 
                 allergies, notes, numero_secu, categorie, adresse, ville, 
                 code_postal, pays, titre_poste, entreprise) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (nom, email, telephone, self.username or "default", 
                 date_naissance, groupe_sanguin, allergies, notes, numero_secu,
                 categorie or 'Patient', adresse, ville, code_postal, pays,
                 titre_poste, entreprise)
            )
            
            conn.commit()
            conn.close()
            
            # Recharger les contacts
            self.charger_contacts()
            print(f"✓ Contact '{nom}' ajouté avec succès!")
            
        except Exception as e:
            print(f"⚠ Erreur lors de l'ajout du contact: {e}")
    
    def supprimer_contact(self, nom):
        """
        Supprime un contact de la base de données par son nom
        
        Args:
            nom (str): Le nom du contact à supprimer
        
        Returns:
            bool: True si le contact a été supprimé, False sinon
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if self.username:
                cursor.execute(
                    "DELETE FROM contacts WHERE nom = ? AND username = ?",
                    (nom, self.username)
                )
            else:
                cursor.execute("DELETE FROM contacts WHERE nom = ?", (nom,))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                # Recharger les contacts
                self.charger_contacts()
                print(f"✓ Contact '{nom}' supprimé avec succès!")
                return True
            else:
                print(f"✗ Contact '{nom}' introuvable!")
                return False
                
        except Exception as e:
            print(f"⚠ Erreur lors de la suppression du contact: {e}")
            return False
    
    def modifier_contact(self, ancien_nom, nouveau_nom, email, telephone,
                        date_naissance=None, groupe_sanguin=None, allergies=None, 
                        notes=None, numero_secu=None, categorie=None, adresse=None,
                        ville=None, code_postal=None, pays=None, titre_poste=None,
                        entreprise=None):
        """
        Modifie un contact existant
        
        Args:
            ancien_nom (str): Le nom actuel du contact
            nouveau_nom (str): Le nouveau nom du contact
            email (str): La nouvelle adresse email
            telephone (str): Le nouveau numéro de téléphone
            date_naissance (str): Date de naissance (optionnel)
            groupe_sanguin (str): Groupe sanguin (optionnel)
            allergies (str): Allergies (optionnel)
            notes (str): Notes médicales (optionnel)
            numero_secu (str): Numéro de sécurité sociale (optionnel)
        
        Returns:
            bool: True si le contact a été modifié, False sinon
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if self.username:
                cursor.execute(
                    """UPDATE contacts SET nom = ?, email = ?, telephone = ?, 
                       date_naissance = ?, groupe_sanguin = ?, allergies = ?, 
                       notes = ?, numero_secu = ?, categorie = ?, adresse = ?,
                       ville = ?, code_postal = ?, pays = ?, titre_poste = ?,
                       entreprise = ?
                       WHERE nom = ? AND username = ?""",
                    (nouveau_nom, email, telephone, date_naissance, groupe_sanguin,
                     allergies, notes, numero_secu, categorie, adresse, ville,
                     code_postal, pays, titre_poste, entreprise, ancien_nom, self.username)
                )
            else:
                cursor.execute(
                    """UPDATE contacts SET nom = ?, email = ?, telephone = ?,
                       date_naissance = ?, groupe_sanguin = ?, allergies = ?, 
                       notes = ?, numero_secu = ?, categorie = ?, adresse = ?,
                       ville = ?, code_postal = ?, pays = ?, titre_poste = ?,
                       entreprise = ?
                       WHERE nom = ?""",
                    (nouveau_nom, email, telephone, date_naissance, groupe_sanguin,
                     allergies, notes, numero_secu, categorie, adresse, ville,
                     code_postal, pays, titre_poste, entreprise, ancien_nom)
                )
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                # Recharger les contacts
                self.charger_contacts()
                print(f"✓ Contact modifié avec succès!")
                return True
            else:
                print(f"✗ Contact '{ancien_nom}' introuvable!")
                return False
                
        except Exception as e:
            print(f"⚠ Erreur lors de la modification du contact: {e}")
            return False
    
    def rechercher_contacts(self, terme):
        """
        Recherche des contacts par nom, email ou téléphone
        
        Args:
            terme (str): Le terme de recherche
        
        Returns:
            list: Liste des contacts trouvés
        """
        resultats = []
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            terme_recherche = f"%{terme}%"
            
            if self.username:
                cursor.execute(
                    """SELECT nom, email, telephone, date_naissance, groupe_sanguin, 
                       allergies, notes, numero_secu, categorie, adresse, ville,
                       code_postal, pays, titre_poste, entreprise
                       FROM contacts 
                       WHERE (nom LIKE ? OR email LIKE ? OR telephone LIKE ?) 
                       AND username = ?
                       ORDER BY nom""",
                    (terme_recherche, terme_recherche, terme_recherche, self.username)
                )
            else:
                cursor.execute(
                    """SELECT nom, email, telephone, date_naissance, groupe_sanguin, 
                       allergies, notes, numero_secu, categorie, adresse, ville,
                       code_postal, pays, titre_poste, entreprise
                       FROM contacts 
                       WHERE nom LIKE ? OR email LIKE ? OR telephone LIKE ?
                       ORDER BY nom""",
                    (terme_recherche, terme_recherche, terme_recherche)
                )
            
            for row in cursor.fetchall():
                nom, email, telephone, date_naissance, groupe_sanguin, allergies, notes, numero_secu, categorie, adresse, ville, code_postal, pays, titre_poste, entreprise = row
                contact = Contact(nom, email, telephone, date_naissance, 
                                groupe_sanguin, allergies, notes, numero_secu,
                                categorie, adresse, ville, code_postal, pays,
                                titre_poste, entreprise)
                resultats.append(contact)
            
            conn.close()
            
        except Exception as e:
            print(f"⚠ Erreur lors de la recherche: {e}")
        
        return resultats
    
    def afficher_contacts(self):
        """Affiche tous les contacts du carnet"""
        if not self.contacts:
            print("\n📭 Le carnet d'adresses est vide!")
            return
        
        print("\n" + "="*60)
        print("📖 CARNET D'ADRESSES")
        print("="*60)
        
        for i, contact in enumerate(self.contacts, 1):
            print(f"{i}. {contact}")
        
        print("="*60 + "\n")
    
    def rechercher_contact(self, nom):
        """
        Recherche un contact par son nom exact
        
        Args:
            nom (str): Le nom du contact à rechercher
        
        Returns:
            Contact: Le contact trouvé ou None
        """
        for contact in self.contacts:
            if contact.nom.lower() == nom.lower():
                return contact
        return None
    
    def patient_existe(self, nom=None, email=None, telephone=None):
        """
        Vérifie si un patient existe dans le système par nom, email ou téléphone
        
        Args:
            nom (str): Le nom du patient (optionnel)
            email (str): L'email du patient (optionnel)
            telephone (str): Le téléphone du patient (optionnel)
        
        Returns:
            tuple: (bool, dict) - (existe, informations_patient ou None)
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Construire la requête selon les paramètres fournis
            conditions = []
            params = []
            
            if nom:
                conditions.append("LOWER(nom) = LOWER(?)")
                params.append(nom)
            
            if email:
                conditions.append("LOWER(email) = LOWER(?)")
                params.append(email)
            
            if telephone:
                conditions.append("telephone = ?")
                params.append(telephone)
            
            if not conditions:
                return False, None
            
            query = f"SELECT nom, email, telephone FROM contacts WHERE {' OR '.join(conditions)}"
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return True, {
                    'nom': result[0],
                    'email': result[1],
                    'telephone': result[2]
                }
            else:
                return False, None
                
        except Exception as e:
            print(f"⚠ Erreur lors de la vérification du patient: {e}")
            return False, None
    
    def nombre_contacts(self):
        """Retourne le nombre total de contacts"""
        return len(self.contacts)
