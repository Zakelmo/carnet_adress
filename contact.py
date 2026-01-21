"""
Module de gestion d'un contact individuel (Patient)
Adapté pour un cabinet médical
"""

class Contact:
    """Classe représentant un contact patient avec informations médicales et professionnelles"""
    
    def __init__(self, nom, email, telephone, date_naissance=None, 
                 groupe_sanguin=None, allergies=None, notes=None, 
                 numero_secu=None, categorie=None, adresse=None, 
                 ville=None, code_postal=None, pays=None, 
                 titre_poste=None, entreprise=None):
        """
        Initialise un nouveau contact patient
        
        Args:
            nom (str): Le nom du patient
            email (str): L'adresse email du patient
            telephone (str): Le numéro de téléphone du patient
            date_naissance (str): Date de naissance (format: YYYY-MM-DD)
            groupe_sanguin (str): Groupe sanguin (A+, B+, AB+, O+, A-, B-, AB-, O-)
            allergies (str): Allergies connues du patient
            notes (str): Notes médicales additionnelles
            numero_secu (str): Numéro de sécurité sociale
            categorie (str): Catégorie du contact (Patient, Entreprise, Fournisseur, etc.)
            adresse (str): Adresse complète
            ville (str): Ville
            code_postal (str): Code postal
            pays (str): Pays
            titre_poste (str): Titre du poste / Profession
            entreprise (str): Nom de l'entreprise
        """
        self.nom = nom
        self.email = email
        self.telephone = telephone
        self.date_naissance = date_naissance
        self.groupe_sanguin = groupe_sanguin
        self.allergies = allergies
        self.notes = notes
        self.numero_secu = numero_secu
        self.categorie = categorie or 'Patient'
        self.adresse = adresse
        self.ville = ville
        self.code_postal = code_postal
        self.pays = pays
        self.titre_poste = titre_poste
        self.entreprise = entreprise
    
    def __str__(self):
        """Retourne une représentation textuelle du contact"""
        base = f"Nom: {self.nom}, Email: {self.email}, Téléphone: {self.telephone}"
        if self.date_naissance:
            base += f", Né(e) le: {self.date_naissance}"
        if self.groupe_sanguin:
            base += f", Groupe: {self.groupe_sanguin}"
        return base
    
    def __repr__(self):
        """Retourne une représentation pour le débogage"""
        return f"Contact('{self.nom}', '{self.email}', '{self.telephone}')"
    
    def get_medical_info(self):
        """Retourne les informations médicales du patient"""
        return {
            'date_naissance': self.date_naissance,
            'groupe_sanguin': self.groupe_sanguin,
            'allergies': self.allergies,
            'notes': self.notes,
            'numero_secu': self.numero_secu
        }
