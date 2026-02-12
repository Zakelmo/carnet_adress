"""
Application Web Flask pour la gestion de contacts avec contrôle d'accès basé sur les rôles
Version 6: Interface Web avec Flask et RBAC
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from address_book import AddressBook
from auth import AuthManager, Role
from communication_email import EmailService
from communication_whatsapp import WhatsAppService
from config import Config
import os
import sqlite3

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialiser le gestionnaire d'authentification
auth_manager = AuthManager()

# Initialiser les services de communication
email_service = EmailService()
whatsapp_service = WhatsAppService()


# Décorateurs pour vérifier les rôles
def login_required(f):
    """Décorateur pour vérifier que l'utilisateur est connecté"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Décorateur pour vérifier que l'utilisateur a un rôle spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Vous devez être connecté pour accéder à cette page.', 'error')
                return redirect(url_for('login'))
            
            user_role = auth_manager.get_user_role(session['username'])
            if user_role not in roles:
                flash('Vous n\'avez pas les permissions nécessaires pour accéder à cette page.', 'error')
                return redirect(url_for('contacts'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def index():
    """Page d'accueil - redirige vers dashboard/contacts selon le rôle"""
    if 'username' in session:
        user_role = session.get('role', Role.USER)
        if user_role == Role.USER:
            return redirect(url_for('patient_dashboard'))
        else:
            return redirect(url_for('contacts'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    # Détecter si c'est la première visite (aucun utilisateur)
    if auth_manager.nombre_users() == 0:
        session['show_register_hint'] = True
    else:
        session.pop('show_register_hint', None)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if auth_manager.authentifier(username, password):
            session['username'] = username
            session['role'] = auth_manager.get_user_role(username)
            session['category'] = auth_manager.get_user_category(username)
            session.pop('show_register_hint', None)
            flash(f'Bienvenue {username}! ({Role.get_role_name(session["role"])})', 'success')
            
            # Rediriger selon le rôle
            user_role = session['role']
            if user_role == Role.USER:
                return redirect(url_for('patient_dashboard'))
            else:
                return redirect(url_for('contacts'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect!', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription - Pour patients existants ou premier Super Admin"""
    # Vérifier si des utilisateurs existent déjà
    is_first_user = auth_manager.nombre_users() == 0
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()
        
        # Validation de base
        if password != confirm:
            flash('Les mots de passe ne correspondent pas!', 'error')
        elif len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères!', 'error')
        else:
            if is_first_user:
                # Premier utilisateur = Super Admin
                succes, message = auth_manager.creer_compte(
                    username, 
                    password, 
                    role=Role.SUPER_ADMIN,
                    created_by_role=None
                )
                if succes:
                    flash('Super Administrateur créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
                    return redirect(url_for('login'))
                else:
                    flash(message, 'error')
            else:
                # Auto-inscription pour patients existants
                patient_nom = request.form.get('patient_nom', '').strip()
                patient_email = request.form.get('patient_email', '').strip()
                patient_telephone = request.form.get('patient_telephone', '').strip()
                
                if not patient_nom or not patient_email or not patient_telephone:
                    flash('Tous les champs patient sont obligatoires pour l\'auto-inscription!', 'error')
                else:
                    # Vérifier que le patient existe
                    carnet = AddressBook()
                    patient_existe, patient_data = carnet.patient_existe(
                        nom=patient_nom,
                        email=patient_email,
                        telephone=patient_telephone
                    )
                    
                    if patient_existe:
                        # Récupérer la catégorie du contact
                        contact = carnet.rechercher_contact(patient_nom)
                        category = contact.categorie if contact else 'Patient'
                        
                        # Créer le compte utilisateur
                        patient_info = {
                            'nom': patient_nom,
                            'email': patient_email,
                            'telephone': patient_telephone
                        }
                        succes, message = auth_manager.creer_compte(
                            username, 
                            password, 
                            role=Role.USER,
                            created_by_role=None,  # Auto-inscription
                            patient_info=patient_info,
                            category=category
                        )
                        
                        if succes:
                            flash('Compte créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
                            return redirect(url_for('login'))
                        else:
                            flash(message, 'error')
                    else:
                        flash('Aucun patient trouvé avec ces informations. Veuillez contacter le cabinet pour être enregistré d\'abord.', 'error')
    
    return render_template('register.html', is_first_user=is_first_user)


@app.route('/logout')
def logout():
    """Déconnexion"""
    session.pop('username', None)
    session.pop('role', None)
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('login'))


@app.route('/contacts')
@login_required
def contacts():
    """Page principale - liste des contacts"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    
    # Pour les USER: rediriger vers le dashboard
    if user_role == Role.USER:
        return redirect(url_for('patient_dashboard'))
    
    # ADMIN/SUPER_ADMIN peuvent voir tous les contacts et faire des recherches
    carnet = AddressBook(username=username)
    search = request.args.get('search', '').strip()
    if search:
        contacts_list = carnet.rechercher_contacts(search)
    else:
        contacts_list = carnet.contacts
    
    return render_template('contacts.html', 
                         contacts=contacts_list, 
                         username=username,
                         user_role=user_role,
                         search=search)


@app.route('/add', methods=['GET', 'POST'])
@role_required(Role.ADMIN, Role.SUPER_ADMIN)  # Seuls ADMIN et SUPER_ADMIN peuvent ajouter des patients
def add_contact():
    """Ajouter un contact - Réservé aux Admin/Super Admin"""
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        telephone = request.form.get('telephone', '').strip()
        date_naissance = request.form.get('date_naissance', '').strip() or None
        groupe_sanguin = request.form.get('groupe_sanguin', '').strip() or None
        allergies = request.form.get('allergies', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        numero_secu = request.form.get('numero_secu', '').strip() or None
        categorie = request.form.get('categorie', '').strip() or None
        adresse = request.form.get('adresse', '').strip() or None
        ville = request.form.get('ville', '').strip() or None
        code_postal = request.form.get('code_postal', '').strip() or None
        pays = request.form.get('pays', '').strip() or None
        titre_poste = request.form.get('titre_poste', '').strip() or None
        entreprise = request.form.get('entreprise', '').strip() or None
        
        if nom and email and telephone:
            username = session['username']
            carnet = AddressBook(username=username)
            carnet.ajouter_contact(nom, email, telephone, date_naissance, 
                                  groupe_sanguin, allergies, notes, numero_secu,
                                  categorie, adresse, ville, code_postal, pays,
                                  titre_poste, entreprise)
            flash(f'Contact "{nom}" ajouté avec succès!', 'success')
            return redirect(url_for('contacts'))
        else:
            flash('Les champs nom, email et téléphone sont obligatoires!', 'error')
    
    return render_template('add.html')


@app.route('/edit/<nom>', methods=['GET', 'POST'])
@login_required
def edit_contact(nom):
    """Modifier un contact - USER peut modifier seulement ses propres informations"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    
    # Pour USER, chercher dans toute la base de données
    # Pour ADMIN, utiliser le carnet normal
    if user_role == Role.USER:
        # Chercher le patient dans toute la base
        import sqlite3
        contact = None
        try:
            conn = sqlite3.connect(Config.DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nom, email, telephone, date_naissance, groupe_sanguin, 
                       allergies, notes, numero_secu, categorie, adresse, ville,
                       code_postal, pays, titre_poste, entreprise
                FROM contacts 
                WHERE nom = ?
            """, (nom,))
            
            row = cursor.fetchone()
            if row:
                from contact import Contact
                contact = Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                row[8], row[9], row[10], row[11], row[12], row[13], row[14])
            conn.close()
        except Exception as e:
            print(f"Erreur lors de la récupération du contact: {e}")
    else:
        carnet = AddressBook(username=username)
        contact = carnet.rechercher_contact(nom)
    
    if not contact:
        flash(f'Contact "{nom}" introuvable!', 'error')
        if user_role == Role.USER:
            return redirect(url_for('patient_dashboard'))
        else:
            return redirect(url_for('contacts'))
    
    # Vérifier les permissions pour USER
    if user_role == Role.USER:
        # USER ne peut modifier que son propre profil patient
        # Vérifier que le contact correspond au nom d'utilisateur
        # On accepte si le nom d'utilisateur est contenu dans le nom du contact
        # ou si le contact a été créé par cet utilisateur
        if username.lower() not in contact.nom.lower().replace(' ', '_') and username.lower() not in contact.email.lower():
            flash('Vous ne pouvez modifier que vos propres informations!', 'error')
            return redirect(url_for('patient_dashboard'))
    
    if request.method == 'POST':
        # USER ne peut PAS modifier nom, email, téléphone (infos d'identification)
        # Seul Admin peut modifier ces champs critiques
        if user_role == Role.USER:
            # USER peut seulement mettre à jour les infos médicales
            nouveau_nom = contact.nom  # Garde le nom actuel
            email = contact.email  # Garde l'email actuel
            telephone = contact.telephone  # Garde le téléphone actuel
            date_naissance = request.form.get('date_naissance', '').strip() or None
            groupe_sanguin = request.form.get('groupe_sanguin', '').strip() or None
            allergies = request.form.get('allergies', '').strip() or None
            notes = request.form.get('notes', '').strip() or None
            numero_secu = request.form.get('numero_secu', '').strip() or None
            categorie = contact.categorie  # Garde la catégorie actuelle
            adresse = contact.adresse  # Garde l'adresse actuelle
            ville = contact.ville
            code_postal = contact.code_postal
            pays = contact.pays
            titre_poste = contact.titre_poste
            entreprise = contact.entreprise
        else:
            # ADMIN/SUPER_ADMIN peuvent tout modifier
            nouveau_nom = request.form.get('nom', '').strip()
            email = request.form.get('email', '').strip()
            telephone = request.form.get('telephone', '').strip()
            date_naissance = request.form.get('date_naissance', '').strip() or None
            groupe_sanguin = request.form.get('groupe_sanguin', '').strip() or None
            allergies = request.form.get('allergies', '').strip() or None
            notes = request.form.get('notes', '').strip() or None
            numero_secu = request.form.get('numero_secu', '').strip() or None
            categorie = request.form.get('categorie', '').strip() or None
            adresse = request.form.get('adresse', '').strip() or None
            ville = request.form.get('ville', '').strip() or None
            code_postal = request.form.get('code_postal', '').strip() or None
            pays = request.form.get('pays', '').strip() or None
            titre_poste = request.form.get('titre_poste', '').strip() or None
            entreprise = request.form.get('entreprise', '').strip() or None
        
        if nouveau_nom and email and telephone:
            # Pour USER, utiliser une modification directe en base de données
            if user_role == Role.USER:
                try:
                    import sqlite3
                    conn = sqlite3.connect(Config.DATABASE_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE contacts 
                        SET date_naissance = ?, groupe_sanguin = ?, allergies = ?, 
                            notes = ?, numero_secu = ?, categorie = ?, adresse = ?,
                            ville = ?, code_postal = ?, pays = ?, titre_poste = ?,
                            entreprise = ?
                        WHERE nom = ?
                    """, (date_naissance, groupe_sanguin, allergies, notes, numero_secu,
                          categorie, adresse, ville, code_postal, pays, titre_poste,
                          entreprise, nom))
                    conn.commit()
                    conn.close()
                    flash(f'Vos informations ont été mises à jour avec succès!', 'success')
                    return redirect(url_for('patient_dashboard'))
                except Exception as e:
                    flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
            else:
                # ADMIN modifie via AddressBook
                carnet = AddressBook(username=username)
                carnet.modifier_contact(nom, nouveau_nom, email, telephone,
                                       date_naissance, groupe_sanguin, allergies, 
                                       notes, numero_secu, categorie, adresse,
                                       ville, code_postal, pays, titre_poste, entreprise)
                flash(f'Contact modifié avec succès!', 'success')
                return redirect(url_for('contacts'))
        else:
            flash('Les champs nom, email et téléphone sont obligatoires!', 'error')
    
    return render_template('edit.html', contact=contact, user_role=user_role)


@app.route('/delete/<nom>')
@role_required(Role.ADMIN, Role.SUPER_ADMIN)  # Seuls ADMIN et SUPER_ADMIN peuvent supprimer
def delete_contact(nom):
    """Supprimer un contact - Réservé aux Admin/Super Admin"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    
    # Admins peuvent supprimer des contacts
    carnet = AddressBook(username=username)
    
    if carnet.supprimer_contact(nom):
        flash(f'Contact "{nom}" supprimé avec succès!', 'success')
    else:
        flash(f'Erreur lors de la suppression du contact!', 'error')
    
    return redirect(url_for('contacts'))


@app.route('/categories')
@role_required(Role.ADMIN, Role.SUPER_ADMIN)
def categories():
    """Page des catégories - Affiche les contacts groupés par catégorie"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    
    # Récupérer tous les contacts groupés par catégorie
    import sqlite3
    categories_data = {}
    
    try:
        conn = sqlite3.connect(Config.DATABASE_NAME)
        cursor = conn.cursor()
        
        # Compter les contacts par catégorie
        cursor.execute("""
            SELECT categorie, COUNT(*) as count
            FROM contacts
            GROUP BY categorie
            ORDER BY count DESC
        """)
        
        category_counts = {}
        for row in cursor.fetchall():
            cat = row[0] or 'Patient'
            category_counts[cat] = row[1]
        
        # Récupérer les contacts de chaque catégorie
        cursor.execute("""
            SELECT categorie, nom, email, telephone, ville, entreprise, titre_poste
            FROM contacts
            ORDER BY categorie, nom
        """)
        
        for row in cursor.fetchall():
            cat = row[0] or 'Patient'
            if cat not in categories_data:
                categories_data[cat] = []
            
            categories_data[cat].append({
                'nom': row[1],
                'email': row[2],
                'telephone': row[3],
                'ville': row[4],
                'entreprise': row[5],
                'titre_poste': row[6]
            })
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la récupération des catégories: {e}")
    
    # Définir les icônes et couleurs pour chaque catégorie
    category_info = {
        'Patient': {'icon': '👤', 'color': '#667eea'},
        'Pharmacie': {'icon': '💊', 'color': '#28a745'},
        'Fournisseur': {'icon': '📦', 'color': '#fd7e14'},
        'Partenaire': {'icon': '🤜', 'color': '#6f42c1'},
        'Laboratoire': {'icon': '🔬', 'color': '#20c997'},
        'Assurance': {'icon': '🛡️', 'color': '#e83e8c'},
        'Autre': {'icon': '📋', 'color': '#6c757d'}
    }
    
    return render_template('categories.html',
                         username=username,
                         user_role=user_role,
                         categories_data=categories_data,
                         category_counts=category_counts,
                         category_info=category_info)


# ============= ROUTES ADMIN =============

@app.route('/admin')
@role_required(Role.ADMIN, Role.SUPER_ADMIN)
def admin_panel():
    """Panneau d'administration"""
    username = session['username']
    user_role = session['role']
    users_list = auth_manager.lister_users(user_role)
    
    return render_template('admin.html', 
                         users=users_list, 
                         username=username,
                         user_role=user_role,
                         Role=Role)


@app.route('/admin/create_user', methods=['GET', 'POST'])
@role_required(Role.ADMIN, Role.SUPER_ADMIN)
def create_user():
    """Créer un nouvel utilisateur"""
    user_role = session['role']
    username = session['username']
    
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_password = request.form.get('password', '').strip()
        new_role = request.form.get('role', Role.USER)
        
        # Validation du rôle
        if new_role not in Role.all_roles():
            flash('Rôle invalide!', 'error')
            return redirect(url_for('create_user'))
        
        # Pour les utilisateurs normaux (USER), récupérer les infos du contact et sa catégorie
        patient_info = None
        category = 'Patient'
        if new_role == Role.USER:
            patient_nom = request.form.get('patient_nom', '').strip()
            patient_email = request.form.get('patient_email', '').strip()
            patient_telephone = request.form.get('patient_telephone', '').strip()
            
            if not patient_nom or not patient_email or not patient_telephone:
                flash('Pour créer un compte utilisateur, les informations du contact (nom, email, téléphone) sont obligatoires!', 'error')
                return render_template('create_user.html', 
                                     available_roles=[Role.USER, Role.ADMIN] if user_role == Role.SUPER_ADMIN else [Role.USER],
                                     Role=Role,
                                     user_role=user_role)
            
            patient_info = {
                'nom': patient_nom,
                'email': patient_email,
                'telephone': patient_telephone
            }
            
            # Récupérer la catégorie du contact
            carnet_temp = AddressBook()
            contact = carnet_temp.rechercher_contact(patient_nom)
            if contact:
                category = contact.categorie
        
        succes, message = auth_manager.creer_compte(
            new_username, 
            new_password, 
            new_role, 
            created_by_role=user_role,
            patient_info=patient_info,
            category=category
        )
        
        if succes:
            flash(f'Utilisateur "{new_username}" créé avec succès!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash(message, 'error')
    
    # Déterminer quels rôles peuvent être créés
    available_roles = []
    if user_role == Role.SUPER_ADMIN:
        # Vérifier si un super admin existe déjà
        has_super_admin = any(
            data['role'] == Role.SUPER_ADMIN 
            for data in auth_manager.users.values()
        )
        
        if has_super_admin:
            # Exclure super_admin de la liste
            available_roles = [Role.USER, Role.ADMIN]
        else:
            # Permettre la création du premier super admin
            available_roles = Role.all_roles()
    elif user_role == Role.ADMIN:
        available_roles = [Role.USER]
    
    # Récupérer la liste des patients pour la sélection
    carnet = AddressBook(username=username)
    patients_list = carnet.contacts
    
    return render_template('create_user.html', 
                         available_roles=available_roles,
                         Role=Role,
                         user_role=user_role,
                         patients=patients_list)


@app.route('/admin/edit_user/<target_username>', methods=['GET', 'POST'])
@role_required(Role.ADMIN, Role.SUPER_ADMIN)
def edit_user(target_username):
    """Modifier un utilisateur"""
    username = session['username']
    user_role = session['role']
    
    if not auth_manager.utilisateur_existe(target_username):
        flash('Utilisateur introuvable!', 'error')
        return redirect(url_for('admin_panel'))
    
    target_role = auth_manager.get_user_role(target_username)
    
    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        new_role = request.form.get('role', target_role)
        
        # Validation
        if new_role not in Role.all_roles():
            flash('Rôle invalide!', 'error')
            return redirect(url_for('edit_user', target_username=target_username))
        
        succes, message = auth_manager.modifier_user(
            target_username,
            new_password=new_password if new_password else None,
            new_role=new_role,
            modified_by_username=username
        )
        
        if succes:
            flash(message, 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash(message, 'error')
    
    # Déterminer quels rôles peuvent être assignés
    available_roles = []
    if user_role == Role.SUPER_ADMIN:
        available_roles = Role.all_roles()
    elif user_role == Role.ADMIN:
        available_roles = [Role.USER]
    
    return render_template('edit_user.html',
                         target_username=target_username,
                         target_role=target_role,
                         available_roles=available_roles,
                         Role=Role,
                         user_role=user_role)


@app.route('/admin/delete_user/<target_username>')
@role_required(Role.ADMIN, Role.SUPER_ADMIN)
def delete_user(target_username):
    """Supprimer un utilisateur"""
    username = session['username']
    
    succes, message = auth_manager.supprimer_user(target_username, username)
    
    if succes:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('admin_panel'))


# ============= ROUTES SUPER ADMIN =============

@app.route('/superadmin')
@role_required(Role.SUPER_ADMIN)
def superadmin_panel():
    """Panneau Super Administrateur"""
    username = session['username']
    
    # Obtenir des statistiques sur la base de données
    carnet = AddressBook()
    stats = carnet.statistiques()
    
    # Statistiques utilisateurs
    users_list = auth_manager.lister_users(Role.SUPER_ADMIN)
    users_by_role = {}
    for role in Role.all_roles():
        users_by_role[role] = len([u for u in users_list if u['role'] == role])
    
    return render_template('superadmin.html',
                         username=username,
                         db_stats=stats,
                         users_by_role=users_by_role,
                         total_users=len(users_list),
                         Role=Role)


@app.route('/superadmin/backup_db')
@role_required(Role.SUPER_ADMIN)
def backup_database():
    """Créer une sauvegarde de la base de données"""
    import shutil
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'contacts_backup_{timestamp}.db'
        shutil.copy('contacts.db', backup_name)
        flash(f'Base de données sauvegardée: {backup_name}', 'success')
    except Exception as e:
        flash(f'Erreur lors de la sauvegarde: {str(e)}', 'error')
    
    return redirect(url_for('superadmin_panel'))


@app.route('/superadmin/clear_db', methods=['POST'])
@role_required(Role.SUPER_ADMIN)
def clear_database():
    """Effacer toute la base de données (DANGEREUX)"""
    confirmation = request.form.get('confirmation', '').strip()
    
    if confirmation == 'DELETE ALL DATA':
        try:
            import sqlite3
            conn = sqlite3.connect('contacts.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM contacts')
            conn.commit()
            conn.close()
            flash('Toutes les données ont été supprimées!', 'success')
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'error')
    else:
        flash('Confirmation incorrecte. Tapez exactement "DELETE ALL DATA"', 'error')
    
    return redirect(url_for('superadmin_panel'))


# ============= ROUTE USER DASHBOARD =============

@app.route('/dashboard')
@login_required
def patient_dashboard():
    """Dashboard personnel pour les utilisateurs (USER) - Gère différentes catégories"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    
    # Rediriger les ADMIN/SUPER_ADMIN vers la page contacts
    if user_role in [Role.ADMIN, Role.SUPER_ADMIN]:
        return redirect(url_for('contacts'))
    
    # Récupérer la catégorie de l'utilisateur
    user_category = auth_manager.get_user_category(username)
    
    # Récupérer les informations du contact lié à ce compte utilisateur
    import sqlite3
    contact_info = None
    try:
        conn = sqlite3.connect(Config.DATABASE_NAME)
        cursor = conn.cursor()
        
        # Chercher le contact qui correspond au username
        cursor.execute("""
            SELECT nom, email, telephone, date_naissance, groupe_sanguin, 
                   allergies, notes, numero_secu, categorie, adresse, ville,
                   code_postal, pays, titre_poste, entreprise
            FROM contacts 
            ORDER BY id DESC
        """)
        
        all_contacts = cursor.fetchall()
        
        # Chercher par correspondance username
        if all_contacts:
            from contact import Contact
            for row in all_contacts:
                # Créer un objet Contact avec tous les champs
                contact = Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                row[8], row[9], row[10], row[11], row[12], row[13], row[14])
                # Vérifier si c'est le bon contact (par username ou email)
                if username.lower() in row[0].lower().replace(' ', '_') or username.lower() in row[1].lower():
                    contact_info = contact
                    break
            
            # Si pas trouvé par correspondance, prendre le premier
            if not contact_info and all_contacts:
                row = all_contacts[0]
                contact_info = Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                     row[8], row[9], row[10], row[11], row[12], row[13], row[14])
        
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la récupération du contact: {e}")
    
    # Récupérer l'historique des communications pour ce contact
    historique_recent = []
    if contact_info:
        try:
            conn = sqlite3.connect(Config.DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type, destinataire, sujet, message, statut, date_envoi
                FROM communications
                WHERE contact_nom = ?
                ORDER BY date_envoi DESC
                LIMIT 5
            """, (contact_info.nom,))
            
            for row in cursor.fetchall():
                historique_recent.append({
                    'type': row[0],
                    'destinataire': row[1],
                    'sujet': row[2],
                    'message': row[3],
                    'statut': row[4],
                    'date_envoi': row[5]
                })
            conn.close()
        except Exception as e:
            print(f"Erreur lors de la récupération de l'historique: {e}")
    
    # Récupérer les rendez-vous à venir (seulement pour les patients)
    appointments_upcoming = []
    if contact_info and user_category == 'Patient':
        try:
            conn = sqlite3.connect(Config.DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, date_rdv, heure_debut, heure_fin, motif, notes, statut
                FROM appointments
                WHERE (created_for = ? OR contact_nom = ? OR LOWER(contact_nom) = LOWER(?)) 
                  AND statut = 'confirmé'
                  AND date_rdv >= date('now')
                ORDER BY date_rdv ASC, heure_debut ASC
                LIMIT 5
            """, (username, contact_info.nom, contact_info.nom))
            
            for row in cursor.fetchall():
                appointments_upcoming.append({
                    'id': row[0],
                    'date_rdv': row[1],
                    'heure_debut': row[2],
                    'heure_fin': row[3],
                    'motif': row[4],
                    'notes': row[5],
                    'statut': row[6]
                })
            conn.close()
        except Exception as e:
            print(f"Erreur lors de la récupération des rendez-vous: {e}")
    
    return render_template('patient_dashboard.html',
                         username=username,
                         user_role=user_role,
                         user_category=user_category,
                         contact=contact_info,
                         patient=contact_info,
                         historique_recent=historique_recent,
                         appointments_upcoming=appointments_upcoming)


# ============= ROUTE PROFILE =============

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Page de profil utilisateur - modifier mot de passe et infos contact"""
    username = session['username']
    user_role = session['role']
    
    # Pour USER, récupérer la catégorie et les informations du contact
    user_category = auth_manager.get_user_category(username) if user_role == Role.USER else None
    contact_info = None
    if user_role == Role.USER:
        # Chercher le contact dans toute la base de données
        import sqlite3
        try:
            conn = sqlite3.connect(Config.DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nom, email, telephone, date_naissance, groupe_sanguin, 
                       allergies, notes, numero_secu, categorie, adresse, ville,
                       code_postal, pays, titre_poste, entreprise
                FROM contacts 
                ORDER BY id DESC
            """)
            
            all_contacts = cursor.fetchall()
            if all_contacts:
                from contact import Contact
                for row in all_contacts:
                    contact = Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                    row[8], row[9], row[10], row[11], row[12], row[13], row[14])
                    if username.lower() in row[0].lower().replace(' ', '_') or username.lower() in row[1].lower():
                        contact_info = contact
                        break
                
                if not contact_info and all_contacts:
                    row = all_contacts[0]
                    contact_info = Contact(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                                         row[8], row[9], row[10], row[11], row[12], row[13], row[14])
            
            conn.close()
        except Exception as e:
            print(f"Erreur lors de la récupération du contact: {e}")
    
    if request.method == 'POST':
        action = request.form.get('action', 'password')
        
        if action == 'password':
            # Modification du mot de passe
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if new_password != confirm_password:
                flash('Les mots de passe ne correspondent pas!', 'error')
            elif len(new_password) < 8:
                flash('Le mot de passe doit contenir au moins 8 caractères!', 'error')
            else:
                succes, message = auth_manager.modifier_user(
                    username,
                    new_password=new_password,
                    modified_by_username=username
                )
                
                if succes:
                    flash('Mot de passe modifié avec succès!', 'success')
                else:
                    flash(message, 'error')
        
        elif action in ['contact_info', 'patient_info'] and user_role == Role.USER and contact_info:
            # Modification des informations contact (USER uniquement)
            # Les champs modifiables dépendent de la catégorie
            if user_category == 'Patient':
                date_naissance = request.form.get('date_naissance', '').strip() or None
                groupe_sanguin = request.form.get('groupe_sanguin', '').strip() or None
                allergies = request.form.get('allergies', '').strip() or None
                notes = request.form.get('notes', '').strip() or None
                numero_secu = request.form.get('numero_secu', '').strip() or None
                
                carnet = AddressBook(username=username)
                carnet.modifier_contact(
                    contact_info.nom,
                    contact_info.nom,  # Nom inchangé
                    contact_info.email,  # Email inchangé
                    contact_info.telephone,  # Téléphone inchangé
                    date_naissance,
                    groupe_sanguin,
                    allergies,
                    notes,
                    numero_secu,
                    contact_info.categorie,
                    contact_info.adresse,
                    contact_info.ville,
                    contact_info.code_postal,
                    contact_info.pays,
                    contact_info.titre_poste,
                    contact_info.entreprise
                )
            else:
                # Pour les autres catégories, permettre la modification des infos professionnelles
                adresse = request.form.get('adresse', '').strip() or None
                ville = request.form.get('ville', '').strip() or None
                code_postal = request.form.get('code_postal', '').strip() or None
                pays = request.form.get('pays', '').strip() or None
                titre_poste = request.form.get('titre_poste', '').strip() or None
                entreprise = request.form.get('entreprise', '').strip() or None
                notes = request.form.get('notes', '').strip() or None
                
                carnet = AddressBook(username=username)
                carnet.modifier_contact(
                    contact_info.nom,
                    contact_info.nom,  # Nom inchangé
                    contact_info.email,  # Email inchangé
                    contact_info.telephone,  # Téléphone inchangé
                    contact_info.date_naissance,
                    contact_info.groupe_sanguin,
                    contact_info.allergies,
                    notes,
                    contact_info.numero_secu,
                    contact_info.categorie,
                    adresse,
                    ville,
                    code_postal,
                    pays,
                    titre_poste,
                    entreprise
                )
            
            flash('Vos informations ont été mises à jour avec succès!', 'success')
            
            # Recharger les informations
            carnet = AddressBook(username=username)
            contacts_list = carnet.contacts
            contact_info = contacts_list[0] if contacts_list else None
    
    return render_template('profile.html',
                         username=username,
                         user_role=user_role,
                         user_category=user_category,
                         role_name=Role.get_role_name(user_role),
                         contact=contact_info,
                         patient=contact_info)


# ============= ROUTES COMMUNICATIONS =============

@app.route('/communications')
@login_required
def communications():
    """Page principale des communications"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    
    # Vérifier la configuration
    email_configured = Config.is_email_configured()
    whatsapp_configured = Config.is_whatsapp_configured()
    
    # Obtenir l'historique récent
    historique = []
    try:
        import sqlite3
        conn = sqlite3.connect(Config.DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contact_nom, type, destinataire, sujet, statut, date_envoi
            FROM communications
            ORDER BY date_envoi DESC
            LIMIT 20
        """)
        for row in cursor.fetchall():
            historique.append({
                'contact_nom': row[0],
                'type': row[1],
                'destinataire': row[2],
                'sujet': row[3],
                'statut': row[4],
                'date_envoi': row[5]
            })
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique: {e}")
    
    return render_template('communications.html',
                         username=username,
                         user_role=user_role,
                         email_configured=email_configured,
                         whatsapp_configured=whatsapp_configured,
                         historique=historique,
                         templates=Config.MESSAGE_TEMPLATES)


@app.route('/communications/send_email/<nom>', methods=['GET', 'POST'])
@login_required
def send_email(nom):
    """Envoyer un email à un contact"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    carnet = AddressBook(username=username)
    contact = carnet.rechercher_contact(nom)
    
    if not contact:
        flash(f'Contact "{nom}" introuvable!', 'error')
        return redirect(url_for('contacts'))
    
    if request.method == 'POST':
        sujet = request.form.get('sujet', '').strip()
        message = request.form.get('message', '').strip()
        template_name = request.form.get('template', '').strip()
        
        if template_name:
            # Utiliser un template
            variables = {
                'date': request.form.get('date', ''),
                'heure': request.form.get('heure', ''),
                'message': request.form.get('custom_message', '')
            }
            succes, msg = email_service.envoyer_email_template(
                contact.email,
                contact.nom,
                template_name,
                variables,
                sent_by=username,
                contact_nom=contact.nom
            )
        else:
            # Message personnalisé
            if not sujet or not message:
                flash('Le sujet et le message sont obligatoires!', 'error')
                return render_template('send_email.html', contact=contact, 
                                     templates=Config.MESSAGE_TEMPLATES,
                                     user_role=user_role)
            
            succes, msg = email_service.envoyer_email(
                contact.email,
                contact.nom,
                sujet,
                message,
                sent_by=username,
                contact_nom=contact.nom
            )
        
        if succes:
            flash(msg, 'success')
            return redirect(url_for('contacts'))
        else:
            flash(msg, 'error')
    
    return render_template('send_email.html', 
                         contact=contact,
                         templates=Config.MESSAGE_TEMPLATES,
                         user_role=user_role)


@app.route('/communications/send_whatsapp/<nom>', methods=['GET', 'POST'])
@login_required
def send_whatsapp(nom):
    """Envoyer un message WhatsApp à un contact"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    carnet = AddressBook(username=username)
    contact = carnet.rechercher_contact(nom)
    
    if not contact:
        flash(f'Contact "{nom}" introuvable!', 'error')
        return redirect(url_for('contacts'))
    
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        template_name = request.form.get('template', '').strip()
        
        if template_name:
            # Utiliser un template
            variables = {
                'date': request.form.get('date', ''),
                'heure': request.form.get('heure', ''),
                'message': request.form.get('custom_message', '')
            }
            succes, msg = whatsapp_service.envoyer_message_template(
                contact.telephone,
                contact.nom,
                template_name,
                variables,
                sent_by=username,
                contact_nom=contact.nom
            )
        else:
            # Message personnalisé
            if not message:
                flash('Le message est obligatoire!', 'error')
                return render_template('send_whatsapp.html', contact=contact,
                                     templates=Config.MESSAGE_TEMPLATES,
                                     user_role=user_role)
            
            succes, msg = whatsapp_service.envoyer_message(
                contact.telephone,
                contact.nom,
                message,
                sent_by=username,
                contact_nom=contact.nom
            )
        
        if succes:
            flash(msg, 'success')
            return redirect(url_for('contacts'))
        else:
            flash(msg, 'error')
    
    return render_template('send_whatsapp.html',
                         contact=contact,
                         templates=Config.MESSAGE_TEMPLATES,
                         user_role=user_role)


@app.route('/communications/history/<nom>')
@login_required
def communication_history(nom):
    """Voir l'historique des communications avec un contact"""
    username = session['username']
    user_role = session.get('role', Role.USER)
    
    # Récupérer l'historique
    historique = []
    try:
        import sqlite3
        conn = sqlite3.connect(Config.DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT type, destinataire, sujet, message, statut, sent_by, date_envoi
            FROM communications
            WHERE contact_nom = ?
            ORDER BY date_envoi DESC
        """, (nom,))
        
        for row in cursor.fetchall():
            historique.append({
                'type': row[0],
                'destinataire': row[1],
                'sujet': row[2],
                'message': row[3],
                'statut': row[4],
                'sent_by': row[5],
                'date_envoi': row[6]
            })
        conn.close()
    except Exception as e:
        flash(f"Erreur lors de la récupération de l'historique: {e}", 'error')
    
    return render_template('communication_history.html',
                         contact_nom=nom,
                         historique=historique,
                         username=username,
                         user_role=user_role)


@app.route('/communications/send_bulk', methods=['GET', 'POST'])
@role_required(Role.ADMIN, Role.SUPER_ADMIN)
def send_bulk_communication():
    """Envoyer des communications groupées (Admin/Super Admin uniquement)"""
    username = session['username']
    user_role = session['role']
    
    if request.method == 'POST':
        comm_type = request.form.get('type', '').strip()  # email ou whatsapp
        message = request.form.get('message', '').strip()
        sujet = request.form.get('sujet', '').strip()
        contact_ids = request.form.getlist('contacts[]')
        
        if not contact_ids:
            flash('Veuillez sélectionner au moins un contact!', 'error')
            return redirect(url_for('send_bulk_communication'))
        
        # Récupérer les contacts sélectionnés
        carnet = AddressBook(username=username)
        destinataires = []
        
        for contact_nom in contact_ids:
            contact = carnet.rechercher_contact(contact_nom)
            if contact:
                if comm_type == 'email':
                    destinataires.append((contact.email, contact.nom, contact.nom))
                elif comm_type == 'whatsapp':
                    destinataires.append((contact.telephone, contact.nom, contact.nom))
        
        # Envoyer les messages
        if comm_type == 'email' and sujet and message:
            resultats = email_service.envoyer_emails_groupes(
                destinataires, sujet, message, sent_by=username
            )
            flash(f"Emails envoyés: {resultats['succes']}/{resultats['total']}", 'success')
        elif comm_type == 'whatsapp' and message:
            resultats = whatsapp_service.envoyer_messages_groupes(
                destinataires, message, sent_by=username
            )
            flash(f"Messages WhatsApp envoyés: {resultats['succes']}/{resultats['total']}", 'success')
        else:
            flash('Données manquantes pour l\'envoi!', 'error')
        
        return redirect(url_for('communications'))
    
    # GET: Afficher le formulaire avec la liste des contacts
    carnet = AddressBook(username=username)
    contacts_list = carnet.contacts
    
    return render_template('send_bulk.html',
                         contacts=contacts_list,
                         username=username,
                         user_role=user_role,
                         templates=Config.MESSAGE_TEMPLATES)


@app.route('/appointments')
@login_required
def appointments():
    """Page de gestion des rendez-vous - accessible à tous les utilisateurs"""
    username = session.get('username')
    user_role = session.get('role', 'user')
    
    # Récupérer tous les rendez-vous
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    if user_role == 'user':
        # Les patients voient uniquement leurs propres RDV
        # D'abord essayer de trouver le nom du patient associé à ce compte
        patient_nom = username
        try:
            cursor.execute("""
                SELECT nom FROM contacts 
                WHERE LOWER(email) = LOWER((SELECT email FROM contacts WHERE LOWER(nom) = LOWER(?)))
                OR LOWER(nom) = LOWER(?)
            """, (username, username))
            result = cursor.fetchone()
            if result:
                patient_nom = result[0]
        except Exception:
            pass
        
        cursor.execute("""
            SELECT id, contact_nom, contact_email, contact_telephone, 
                   date_rdv, heure_debut, heure_fin, motif, notes, statut, 
                   created_by, date_creation, created_for
            FROM appointments 
            WHERE created_for = ? OR contact_nom = ? OR LOWER(contact_nom) = LOWER(?)
            ORDER BY 
                CASE WHEN date_rdv >= date('now') THEN 0 ELSE 1 END,
                date_rdv ASC, 
                heure_debut ASC
        """, (username, patient_nom, patient_nom))
    else:
        # Admin et Super Admin voient tous les RDV
        # Les RDV à venir d'abord, puis par date croissante
        cursor.execute("""
            SELECT id, contact_nom, contact_email, contact_telephone, 
                   date_rdv, heure_debut, heure_fin, motif, notes, statut, 
                   created_by, date_creation, created_for
            FROM appointments 
            ORDER BY 
                CASE WHEN date_rdv >= date('now') THEN 0 ELSE 1 END,
                date_rdv ASC, 
                heure_debut ASC
        """)
    
    appointments_list = []
    for row in cursor.fetchall():
        appointments_list.append({
            'id': row[0],
            'contact_nom': row[1],
            'contact_email': row[2],
            'contact_telephone': row[3],
            'date_rdv': row[4],
            'heure_debut': row[5],
            'heure_fin': row[6],
            'motif': row[7],
            'notes': row[8],
            'statut': row[9],
            'created_by': row[10],
            'date_creation': row[11],
            'created_for': row[12]
        })
    
    conn.close()
    
    return render_template('appointments.html',
                         appointments=appointments_list,
                         username=username,
                         user_role=user_role)


@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    """Page pour réserver un rendez-vous - accessible à tous"""
    username = session.get('username')
    user_role = session.get('role', 'user')
    
    # Vérifier la catégorie de l'utilisateur
    user_category = auth_manager.get_user_category(username) if user_role == Role.USER else None
    
    # Les utilisateurs non-patients ne peuvent pas réserver de rendez-vous pour eux-mêmes
    if user_role == Role.USER and user_category != 'Patient':
        flash(f"Les utilisateurs de catégorie '{user_category}' ne peuvent pas réserver de rendez-vous. Cette fonctionnalité est réservée aux patients.", 'error')
        return redirect(url_for('patient_dashboard'))
    
    if request.method == 'POST':
        contact_nom = request.form.get('contact_nom')
        contact_email = request.form.get('contact_email')
        contact_telephone = request.form.get('contact_telephone')
        date_rdv = request.form.get('date_rdv')
        heure_debut = request.form.get('heure_debut')
        motif = request.form.get('motif', '')
        notes = request.form.get('notes', '')
        
        if not all([contact_nom, date_rdv, heure_debut]):
            flash('Veuillez remplir tous les champs obligatoires!', 'error')
            return redirect(url_for('book_appointment'))
        
        # Validation de la date (ne pas permettre les RDV dans le passé)
        from datetime import datetime, timedelta, date
        try:
            debut = datetime.strptime(heure_debut, '%H:%M')
            fin = debut + timedelta(minutes=30)
            heure_fin = fin.strftime('%H:%M')
            
            # Vérifier que la date n'est pas dans le passé
            rdv_date = datetime.strptime(date_rdv, '%Y-%m-%d').date()
            today = date.today()
            if rdv_date < today:
                flash('Impossible de réserver un rendez-vous dans le passé!', 'error')
                return redirect(url_for('book_appointment'))
            
            # Vérifier les heures d'ouverture (8h00 - 18h00)
            if debut.hour < 8 or debut.hour >= 18:
                flash('Les rendez-vous doivent être entre 8h00 et 18h00!', 'error')
                return redirect(url_for('book_appointment'))
                
        except ValueError:
            flash('Format de date ou d\'heure invalide!', 'error')
            return redirect(url_for('book_appointment'))
        
        # Vérifier si le créneau est déjà pris (chevauchement)
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        
        # Requête pour détecter les chevauchements:
        # Un RDV existe déjà si: 
        # - Il est sur la même date ET
        # - Son heure de début est avant notre heure de fin ET
        # - Son heure de fin est après notre heure de début
        cursor.execute("""
            SELECT id, heure_debut, heure_fin FROM appointments 
            WHERE date_rdv = ? 
            AND statut != 'annulé'
            AND heure_debut < ? 
            AND heure_fin > ?
        """, (date_rdv, heure_fin, heure_debut))
        
        conflict = cursor.fetchone()
        if conflict:
            conn.close()
            flash(f'Ce créneau horaire chevauche un rendez-vous existant ({conflict[1]} - {conflict[2]})!', 'error')
            return redirect(url_for('book_appointment'))
        
        # Pour les patients (USER), vérifier que le contact correspond à leur profil
        created_for = username
        if user_role == Role.USER:
            # Récupérer le nom du patient associé à ce compte
            try:
                cursor.execute("""
                    SELECT c.nom FROM contacts c
                    JOIN users_patients_link upl ON c.id = upl.contact_id
                    WHERE upl.username = ?
                """, (username,))
                result = cursor.fetchone()
                if result:
                    created_for = result[0]
                else:
                    # Fallback: chercher le patient par correspondance de nom
                    cursor.execute("""
                        SELECT nom FROM contacts 
                        WHERE LOWER(nom) = LOWER(?) OR LOWER(email) = LOWER(?)
                    """, (contact_nom, contact_email))
                    result = cursor.fetchone()
                    if result:
                        created_for = result[0]
            except Exception:
                pass  # La table de liaison peut ne pas exister
        
        # Créer le rendez-vous
        try:
            cursor.execute("""
                INSERT INTO appointments 
                (contact_nom, contact_email, contact_telephone, date_rdv, 
                 heure_debut, heure_fin, motif, notes, statut, created_by, created_for)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'confirmé', ?, ?)
            """, (contact_nom, contact_email, contact_telephone, date_rdv,
                  heure_debut, heure_fin, motif, notes, username, created_for))
            
            conn.commit()
            
            # Envoyer une confirmation par email si configuré
            if Config.is_email_configured():
                try:
                    # 1. Email de confirmation au patient
                    if contact_email:
                        email_service.envoyer_email_template(
                            contact_email,
                            contact_nom,
                            'confirmation',
                            {'date': date_rdv, 'heure': heure_debut},
                            sent_by=username,
                            contact_nom=contact_nom
                        )
                    
                    # 2. Email de notification au Cabinet Médical
                    cabinet_email = Config.DEFAULT_SENDER_EMAIL
                    if cabinet_email:
                        sujet_cabinet = f"📅 Nouveau rendez-vous réservé - {contact_nom}"
                        motif_display = motif if motif else "Non spécifié"
                        notes_display = notes if notes else "Aucune"
                        
                        corps_cabinet = f"""Bonjour,

Un nouveau rendez-vous vient d'être réservé :

📋 Informations du rendez-vous :
• Patient : {contact_nom}
• Email : {contact_email or 'Non fourni'}
• Téléphone : {contact_telephone or 'Non fourni'}
• Date : {date_rdv}
• Heure : {heure_debut} - {heure_fin}
• Motif : {motif_display}
• Notes : {notes_display}
• Réservé par : {username} ({user_role})

N'oubliez pas de confirmer ce rendez-vous si nécessaire.

Cordialement,
Système de Gestion des Rendez-vous"""
                        
                        email_service.envoyer_email(
                            cabinet_email,
                            Config.DEFAULT_SENDER_NAME,
                            sujet_cabinet,
                            corps_cabinet,
                            sent_by=username,
                            contact_nom="Cabinet Médical"
                        )
                except Exception as e:
                    print(f"Erreur lors de l'envoi des emails de confirmation: {e}")
            
            flash('Rendez-vous réservé avec succès!', 'success')
            conn.close()
            return redirect(url_for('appointments'))
            
        except sqlite3.IntegrityError:
            conn.close()
            flash(f'❌ Le créneau {heure_debut} le {date_rdv} vient d\'être réservé par quelqu\'un d\'autre. Veuillez choisir un autre créneau.', 'error')
            # Rediriger vers la page de réservation avec la date pré-sélectionnée
            return redirect(url_for('book_appointment'))
            
        except Exception as e:
            conn.close()
            flash(f'Erreur lors de la réservation: {str(e)}', 'error')
            return redirect(url_for('book_appointment'))
    
    # GET: Afficher le formulaire avec les contacts disponibles
    carnet = AddressBook(username=username if user_role in ['admin', 'super_admin'] else None)
    contacts_list = carnet.contacts
    
    # Pour les patients, récupérer leurs informations de contact
    patient_info = None
    if user_role == Role.USER:
        try:
            conn = sqlite3.connect(Config.DATABASE_NAME)
            cursor = conn.cursor()
            # Chercher le patient qui correspond au nom d'utilisateur
            cursor.execute("""
                SELECT nom, email, telephone 
                FROM contacts 
                WHERE LOWER(nom) = LOWER(?) OR LOWER(nom) = LOWER(?)
                LIMIT 1
            """, (username, username.replace('_', ' ')))
            result = cursor.fetchone()
            if result:
                patient_info = {
                    'nom': result[0],
                    'email': result[1],
                    'telephone': result[2]
                }
            conn.close()
        except Exception as e:
            print(f"Erreur lors de la récupération des infos patient: {e}")
    
    return render_template('book_appointment.html',
                         contacts=contacts_list,
                         username=username,
                         user_role=user_role,
                         patient_info=patient_info)


@app.route('/get_available_slots', methods=['POST'])
@login_required
def get_available_slots():
    """API pour récupérer les créneaux disponibles pour une date donnée"""
    date_rdv = request.json.get('date_rdv')
    
    if not date_rdv:
        return jsonify({'error': 'Date manquante'}), 400
    
    # Validation de la date (ne pas montrer de créneaux pour les dates passées)
    from datetime import datetime, date, timedelta
    try:
        rdv_date = datetime.strptime(date_rdv, '%Y-%m-%d').date()
        if rdv_date < date.today():
            return jsonify({
                'error': 'La date est dans le passé',
                'available_slots': [],
                'taken_slots': []
            }), 400
    except ValueError:
        return jsonify({'error': 'Format de date invalide'}), 400
    
    # Horaires de travail: 8h00 à 18h00, par créneaux de 30 minutes
    all_slots = []
    for hour in range(8, 18):
        all_slots.append(f"{hour:02d}:00")
        all_slots.append(f"{hour:02d}:30")
    
    # Récupérer les créneaux déjà pris avec leurs heures de fin
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT heure_debut, heure_fin FROM appointments 
        WHERE date_rdv = ? AND statut != 'annulé'
    """, (date_rdv,))
    
    taken_appointments = cursor.fetchall()
    conn.close()
    
    taken_slots = [row[0] for row in taken_appointments]
    
    # Calculer les créneaux disponibles en vérifiant les chevauchements
    available_slots = []
    for slot in all_slots:
        slot_time = datetime.strptime(slot, '%H:%M')
        slot_end = slot_time + timedelta(minutes=30)
        slot_end_str = slot_end.strftime('%H:%M')
        
        # Vérifier si ce créneau chevauche un rendez-vous existant
        is_available = True
        for appt_start, appt_end in taken_appointments:
            appt_start_time = datetime.strptime(appt_start, '%H:%M')
            appt_end_time = datetime.strptime(appt_end, '%H:%M')
            
            # Chevauchement si: slot_debut < appt_fin ET slot_fin > appt_debut
            if slot_time < appt_end_time and slot_end > appt_start_time:
                is_available = False
                break
        
        if is_available:
            available_slots.append(slot)
    
    return jsonify({
        'available_slots': available_slots,
        'taken_slots': taken_slots
    })


@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Annuler un rendez-vous"""
    username = session.get('username')
    user_role = session.get('role', 'user')
    
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    
    # Récupérer les informations du RDV pour vérification et notification
    cursor.execute("""
        SELECT contact_nom, contact_email, date_rdv, heure_debut, statut
        FROM appointments 
        WHERE id = ?
    """, (appointment_id,))
    
    appointment = cursor.fetchone()
    if not appointment:
        conn.close()
        flash('Rendez-vous introuvable!', 'error')
        return redirect(url_for('appointments'))
    
    contact_nom, contact_email, date_rdv, heure_debut, current_status = appointment
    
    # Vérifier si l'utilisateur a le droit d'annuler ce RDV
    if user_role == 'user':
        # Pour les patients, vérifier par nom de contact ou created_for
        cursor.execute("""
            SELECT id FROM appointments 
            WHERE id = ? AND (created_for = ? OR contact_nom = ? OR LOWER(contact_nom) = LOWER(?))
        """, (appointment_id, username, username, username))
        
        if not cursor.fetchone():
            conn.close()
            flash('Vous n\'êtes pas autorisé à annuler ce rendez-vous!', 'error')
            return redirect(url_for('appointments'))
    
    # Vérifier si le RDV est déjà annulé
    if current_status == 'annulé':
        conn.close()
        flash('Ce rendez-vous est déjà annulé!', 'warning')
        return redirect(url_for('appointments'))
    
    # Vérifier que le RDV n'est pas dans le passé
    from datetime import datetime
    try:
        rdv_datetime = datetime.strptime(f"{date_rdv} {heure_debut}", "%Y-%m-%d %H:%M")
        if rdv_datetime < datetime.now():
            conn.close()
            flash('Impossible d\'annuler un rendez-vous passé!', 'error')
            return redirect(url_for('appointments'))
    except ValueError:
        pass  # Si format invalide, on continue quand même
    
    # Annuler le rendez-vous
    # Note: On modifie aussi l'heure pour éviter le conflit avec la contrainte UNIQUE
    from datetime import datetime
    cancelled_time = f"ANNULE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{appointment_id}"
    cursor.execute("""
        UPDATE appointments 
        SET statut = 'annulé',
            heure_debut = ?,
            heure_fin = ?
        WHERE id = ?
    """, (cancelled_time, cancelled_time, appointment_id))
    
    conn.commit()
    conn.close()
    
    # Envoyer une notification d'annulation par email si configuré
    if Config.is_email_configured():
        try:
            # 1. Email au patient
            if contact_email:
                sujet_patient = f"Annulation de votre rendez-vous du {date_rdv}"
                corps_patient = f"""Bonjour {contact_nom},

Votre rendez-vous du {date_rdv} à {heure_debut} a été annulé.

Pour réserver un nouveau rendez-vous, veuillez contacter le cabinet.

Cordialement,
{Config.DEFAULT_SENDER_NAME}"""
                
                email_service.envoyer_email(
                    contact_email,
                    contact_nom,
                    sujet_patient,
                    corps_patient,
                    sent_by=username,
                    contact_nom=contact_nom
                )
            
            # 2. Email de notification au Cabinet Médical
            cabinet_email = Config.DEFAULT_SENDER_EMAIL
            if cabinet_email:
                sujet_cabinet = f"🔔 Annulation d'un rendez-vous - {contact_nom}"
                corps_cabinet = f"""Bonjour,

Une annulation de rendez-vous vient d'être effectuée :

📋 Informations du rendez-vous annulé :
• Patient : {contact_nom}
• Date : {date_rdv}
• Heure : {heure_debut}
• Annulé par : {username} ({user_role})

Ce rendez-vous est maintenant libre et peut être réservé par un autre patient.

Cordialement,
Système de Gestion des Rendez-vous"""
                
                email_service.envoyer_email(
                    cabinet_email,
                    Config.DEFAULT_SENDER_NAME,
                    sujet_cabinet,
                    corps_cabinet,
                    sent_by=username,
                    contact_nom="Cabinet Médical"
                )
        except Exception as e:
            print(f"Erreur lors de l'envoi des emails d'annulation: {e}")
    
    flash('Rendez-vous annulé avec succès!', 'success')
    return redirect(url_for('appointments'))


if __name__ == '__main__':
    # Créer le dossier templates s'il n'existe pas
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
