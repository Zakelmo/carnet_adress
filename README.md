# 📚 Documentation Complète de l'Application Cabinet Médical

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture de l'application](#architecture-de-lapplication)
3. [Technologies utilisées](#technologies-utilisées)
4. [Structure des fichiers](#structure-des-fichiers)
5. [Modules et composants](#modules-et-composants)
6. [Base de données](#base-de-données)
7. [Système d'authentification](#système-dauthentification)
8. [Fonctionnalités](#fonctionnalités)
9. [Interface utilisateur](#interface-utilisateur)
10. [Configuration](#configuration)
11. [Installation et déploiement](#installation-et-déploiement)
12. [Sécurité](#sécurité)
13. [Guide d'utilisation](#guide-dutilisation)

---

## 📖 Vue d'ensemble

### Description
**Carnet d'Adresses - Cabinet Médical** est une application web Flask complète conçue pour la gestion des patients dans un cabinet médical. L'application permet aux professionnels de santé de gérer efficacement leurs patients et rendez-vous.

### Version
**v2.3.0 (Version 6 - Application Web)**

### Objectifs principaux
- Gestion centralisée des informations patients
- Gestion des rendez-vous
- Contrôle d'accès basé sur les rôles (RBAC)
- Interface web responsive et intuitive

### Public cible
- Cabinets médicaux
- Professionnels de santé
- Secrétaires médicales
- Administrateurs de cliniques

---

## 🏗️ Architecture de l'application

### Type d'architecture
**Architecture MVC (Model-View-Controller) avec Flask**

### Composants principaux

```
┌─────────────────────────────────────────┐
│         Interface Web (HTML/CSS)         │
│              (Templates)                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│           Flask Application              │
│              (app.py)                    │
│   ┌─────────────────────────────────┐   │
│   │  Routes & Controllers           │   │
│   │  - Authentication               │   │
│   │  - Contact Management           │   │
│   │  - Appointments                 │   │
│   └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Business Logic Layer             │
│   ┌──────────────┐  ┌────────────────┐  │
│   │ AddressBook  │  │ Auth Manager   │  │
│   │  (Model)     │  │                │  │
│   └──────────────┘  └────────────────┘  │
│   ┌──────────────┐                      │
│   │ Contact      │                      │
│   │  (Model)     │                      │
│   └──────────────┘                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Data Access Layer               │
│         SQLite Database                 │
│   - Contacts Table                      │
│   - Users Table                         │
│   - Appointments Table                  │
└─────────────────────────────────────────┘
```

### Pattern de conception
- **MVC (Model-View-Controller)**
- **Repository Pattern** pour l'accès aux données
- **Singleton** pour la configuration
- **Factory Pattern** pour la création d'utilisateurs

---

## 💻 Technologies utilisées

### Backend
- **Python 3.x** - Langage de programmation principal
- **Flask 3.x** - Framework web micro
- **SQLite** - Base de données relationnelle
- **Werkzeug** - Utilitaires WSGI et hachage de mots de passe

### Frontend
- **HTML5** - Structure des pages
- **CSS3** - Styles et design responsive
- **Jinja2** - Moteur de templates

### Sécurité
- **werkzeug.security** - Hachage de mots de passe (pbkdf2:sha256)
- **flask.session** - Gestion des sessions utilisateur
- **python-dotenv** - Gestion des variables d'environnement

### Dépendances Python
```
Flask
Werkzeug
python-dotenv
```

---

## 📁 Structure des fichiers

```
v2.3.0/
│
├── main.py                          # Point d'entrée de l'application
├── app.py                           # Application Flask principale
├── config.py                        # Configuration centralisée
├── contact.py                       # Classe Contact (modèle)
├── address_book.py                  # Classe AddressBook (gestion des contacts)
├── auth.py                          # Système d'authentification
│
├── contacts.db                      # Base de données SQLite
├── users.txt                        # Fichier des utilisateurs (legacy)
│
├── .env.example                     # Exemple de configuration
├── .gitignore                       # Fichiers à ignorer par Git
├── requirements.txt                 # Dépendances Python
│
├── README.md                        # Documentation principale
├── README_CABINET_MEDICAL.md        # Guide cabinet médical
├── FIRST_LAUNCH.md                  # Guide de premier lancement
├── SECURITY.md                      # Documentation sécurité
│
├── static/
│   └── style.css                    # Styles CSS
│
└── templates/                       # Templates HTML
    ├── base.html                    # Template de base
    ├── login.html                   # Page de connexion
    ├── register.html                # Page d'inscription
    ├── contacts.html                # Liste des contacts
    ├── add.html                     # Ajout de contact
    ├── edit.html                    # Édition de contact
    ├── profile.html                 # Profil utilisateur
    ├── patient_dashboard.html       # Tableau de bord patient
    ├── appointments.html            # Gestion des rendez-vous
    ├── book_appointment.html        # Réservation de RDV
    ├── categories.html              # Gestion des catégories
    ├── admin.html                   # Panel admin
    ├── superadmin.html              # Panel super admin
    ├── create_user.html             # Création d'utilisateur
    └── edit_user.html               # Édition d'utilisateur
```

---

## 🧩 Modules et composants

### 1. **main.py** - Point d'entrée
```python
# Lance l'application Flask
# Configure le serveur (host, port, debug mode)
# Affiche les informations de démarrage
```

**Fonctions principales:**
- Lance le serveur Flask sur `0.0.0.0:5000`
- Active le mode debug pour le développement
- Affiche l'interface de démarrage

---

### 2. **app.py** - Application Flask principale

**Responsabilités:**
- Définition de toutes les routes web
- Gestion des sessions utilisateur
- Contrôle d'accès basé sur les rôles
- Intégration avec les modules métier

**Routes principales:**

#### Routes publiques (sans authentification)
| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Page d'accueil (redirect vers login) |
| `/login` | GET, POST | Page de connexion |
| `/register` | GET, POST | Page d'inscription |

#### Routes utilisateur (authentification requise)
| Route | Méthode | Description | Rôles autorisés |
|-------|---------|-------------|-----------------|
| `/contacts` | GET | Liste des contacts | Admin, Super Admin, User |
| `/add` | GET, POST | Ajouter un contact | Admin, Super Admin |
| `/edit/<nom>` | GET, POST | Modifier un contact | Admin, Super Admin, User (propre profil) |
| `/delete/<nom>` | GET | Supprimer un contact | Admin, Super Admin |
| `/profile` | GET, POST | Profil utilisateur | Tous |
| `/patient-dashboard` | GET | Tableau de bord patient | User |
| `/categories` | GET | Gestion des catégories | Admin, Super Admin |

#### Routes de rendez-vous
| Route | Méthode | Description | Rôles autorisés |
|-------|---------|-------------|-----------------|
| `/appointments` | GET | Liste des rendez-vous | Tous |
| `/book-appointment` | GET, POST | Réserver un RDV | User |
| `/cancel-appointment/<id>` | POST | Annuler un RDV | Tous |

#### Routes d'administration
| Route | Méthode | Description | Rôles autorisés |
|-------|---------|-------------|-----------------|
| `/admin` | GET | Panel admin | Admin, Super Admin |
| `/create-user` | GET, POST | Créer un utilisateur | Admin, Super Admin |
| `/edit-user/<username>` | GET, POST | Modifier un utilisateur | Admin, Super Admin |
| `/delete-user/<username>` | POST | Supprimer un utilisateur | Super Admin |
| `/superadmin` | GET | Panel super admin | Super Admin |

**Décorateurs personnalisés:**
```python
@login_required          # Nécessite une connexion
@admin_required          # Nécessite rôle admin ou super_admin
@super_admin_required    # Nécessite rôle super_admin uniquement
```

---

### 3. **contact.py** - Modèle Contact

**Classe `Contact`:**
```python
class Contact:
    def __init__(self, nom, email, telephone, date_naissance=None, 
                 groupe_sanguin=None, allergies=None, notes=None, 
                 numero_secu=None, categorie=None, adresse=None, 
                 ville=None, code_postal=None, pays=None, 
                 titre_poste=None, entreprise=None)
```

**Attributs:**
- **Informations de base:** nom, email, telephone
- **Informations médicales:** date_naissance, groupe_sanguin, allergies, notes, numero_secu
- **Informations d'adresse:** adresse, ville, code_postal, pays
- **Informations professionnelles:** categorie, titre_poste, entreprise

**Méthodes:**
- `__str__()`: Représentation textuelle
- `__repr__()`: Représentation pour débogage
- `get_medical_info()`: Retourne les informations médicales

---

### 4. **address_book.py** - Gestion des contacts

**Classe `AddressBook`:**
Gère l'ensemble des contacts et interactions avec la base de données.

**Principales méthodes:**

#### Gestion des contacts
```python
add_contact(contact)                    # Ajouter un contact
get_contact(nom)                        # Récupérer un contact
update_contact(old_nom, new_contact)    # Mettre à jour un contact
delete_contact(nom)                     # Supprimer un contact
search_contacts(query)                  # Rechercher des contacts
list_all_contacts()                     # Lister tous les contacts
```

#### Gestion des catégories
```python
add_category(category_name)             # Ajouter une catégorie
get_categories()                        # Obtenir toutes les catégories
get_contacts_by_category(category)      # Filtrer par catégorie
update_category(old_name, new_name)     # Renommer une catégorie
delete_category(category_name)          # Supprimer une catégorie
```

#### Rendez-vous
```python
create_appointment(patient_name, date, time, notes, user_id)  # Créer un RDV
get_appointments(user_id=None)                                # Liste des RDV
cancel_appointment(appointment_id, user_id)                   # Annuler un RDV
get_patient_appointments(patient_name)                        # RDV d'un patient
```

#### Statistiques
```python
get_statistics()                        # Statistiques générales
```

---

### 5. **auth.py** - Système d'authentification

**Classe `AuthManager`:**
Gère l'authentification, les utilisateurs et les rôles.

**Principales méthodes:**

#### Gestion des utilisateurs
```python
create_user(username, password, email, role='user')  # Créer un utilisateur
authenticate(username, password)                      # Authentifier
get_user(username)                                    # Obtenir un utilisateur
update_user(username, **kwargs)                       # Mettre à jour
delete_user(username)                                 # Supprimer
list_users()                                          # Lister tous
```

#### Gestion des rôles
```python
get_user_role(username)                 # Obtenir le rôle
change_user_role(username, new_role)    # Changer le rôle
```

#### Vérifications
```python
is_admin(username)                      # Vérifier si admin
is_super_admin(username)                # Vérifier si super admin
```

**Hiérarchie des rôles:**
1. **super_admin**: Accès complet (gestion utilisateurs, configuration)
2. **admin**: Gestion des patients et rendez-vous
3. **user**: Accès limité (son propre profil et RDV)

---

### 6. **config.py** - Configuration centralisée

**Classe `Config`:**
Centralise toutes les configurations de l'application.

**Sections de configuration:**

#### Flask
```python
SECRET_KEY                  # Clé secrète pour sessions
```

#### Base de données
```python
DATABASE_NAME              # Nom du fichier SQLite
```

**Méthodes utilitaires:**
```python
get_template(name)         # Récupère un template
```

---

## 🗄️ Base de données

### Structure SQLite

#### Table: **contacts**
```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    telephone TEXT NOT NULL,
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
    entreprise TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Table: **users**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT DEFAULT 'user',
    full_name TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1
)
```

#### Table: **appointments**
```sql
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'scheduled',
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_name) REFERENCES contacts(nom),
    FOREIGN KEY (created_by) REFERENCES users(id)
)
```

#### Table: **categories**
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Relations
- Un **contact** peut avoir plusieurs **appointments**
- Un **user** peut créer plusieurs **appointments**
- Un **contact** appartient à une **catégorie**

---

## 🔐 Système d'authentification

### Architecture de sécurité

#### Hachage des mots de passe
```python
# Utilisation de werkzeug.security
from werkzeug.security import generate_password_hash, check_password_hash

# Hachage: pbkdf2:sha256 avec salt aléatoire
password_hash = generate_password_hash(password, method='pbkdf2:sha256')
```

#### Gestion des sessions
```python
# Flask sessions avec SECRET_KEY
session['username'] = username
session['role'] = role
session['user_id'] = user_id
```

### Hiérarchie des rôles et permissions

#### 1. **Super Admin** (super_admin)
**Permissions complètes:**
- ✅ Gestion complète des utilisateurs (créer, modifier, supprimer)
- ✅ Gestion de tous les contacts/patients
- ✅ Accès à tous les rendez-vous
- ✅ Configuration système
- ✅ Statistiques complètes
- ✅ Accès aux logs et historiques

**Actions exclusives:**
- Supprimer des utilisateurs admin
- Modifier les rôles des utilisateurs
- Accès au panel super admin

#### 2. **Admin** (admin)
**Permissions étendues:**
- ✅ Créer des utilisateurs (rôle user uniquement)
- ✅ Gestion complète des patients
- ✅ Accès à tous les rendez-vous
- ✅ Statistiques de base
- ❌ Ne peut pas supprimer d'admins
- ❌ Ne peut pas modifier les rôles

#### 3. **User** (user)
**Permissions limitées:**
- ✅ Voir son propre profil
- ✅ Modifier ses informations personnelles
- ✅ Réserver des rendez-vous
- ✅ Voir ses propres rendez-vous
- ❌ Accès aux autres patients
- ❌ Gestion des utilisateurs

### Décorateurs de sécurité

```python
def login_required(f):
    """Nécessite une connexion valide"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Veuillez vous connecter', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Nécessite un rôle admin ou super_admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['admin', 'super_admin']:
            flash('Accès refusé: Droits administrateur requis', 'error')
            return redirect(url_for('contacts'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Nécessite un rôle super_admin uniquement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'super_admin':
            flash('Accès refusé: Droits super administrateur requis', 'error')
            return redirect(url_for('contacts'))
        return f(*args, **kwargs)
    return decorated_function
```

### Premier lancement et compte par défaut

Au premier lancement, l'application crée automatiquement un compte super admin:
```
Username: admin
Password: admin123
Role: super_admin
```

⚠️ **Important:** Changez ce mot de passe immédiatement après le premier login!

---

## ✨ Fonctionnalités

### 1. Gestion des Patients

#### Ajouter un patient
- Formulaire complet avec validation
- Champs médicaux spécialisés
- Catégorisation automatique
- Upload de photo (prévu)

#### Modifier un patient
- Édition de toutes les informations
- Historique des modifications (timestamp)
- Validation des données

#### Supprimer un patient
- Confirmation requise
- Suppression en cascade (RDV)
- Log de la suppression

#### Rechercher des patients
- Recherche par nom
- Recherche par email
- Recherche par téléphone
- Recherche par catégorie
- Filtres avancés

#### Catégorisation
- Catégories personnalisables
- Filtrage par catégorie
- Statistiques par catégorie

### 2. Gestion des Rendez-vous

#### Pour les patients (User)
- **Réserver un rendez-vous**
  - Choix de la date
  - Choix de l'heure
  - Notes optionnelles
  - Confirmation automatique

- **Voir mes rendez-vous**
  - Liste des RDV à venir
  - Liste des RDV passés
  - Statut des RDV

- **Annuler un rendez-vous**
  - Annulation avec confirmation
  - Notification automatique

#### Pour les admins
- **Vue complète des rendez-vous**
  - Calendrier de tous les RDV
  - Filtrage par patient
  - Filtrage par date
  - Statistiques

- **Gestion des rendez-vous**
  - Création manuelle
  - Modification
  - Annulation
  - Rappels automatiques

### 3. Administration

#### Panel Admin
**Gestion des utilisateurs:**
- Liste de tous les utilisateurs
- Créer un nouvel utilisateur
- Modifier un utilisateur
- Désactiver un compte

**Statistiques:**
- Nombre total de patients
- Nombre de RDV ce mois
- Graphiques et métriques

#### Panel Super Admin
**Fonctionnalités supplémentaires:**
- Suppression d'utilisateurs
- Modification des rôles
- Configuration système
- Logs d'activité
- Gestion de la base de données

### 4. Profil Utilisateur

**Informations personnelles:**
- Nom complet
- Email
- Téléphone
- Photo de profil (prévu)

**Sécurité:**
- Changement de mot de passe
- Historique de connexion
- Sessions actives

**Préférences:**
- Langue (prévu)
- Notifications (prévu)
- Thème (prévu)

---

## 🎨 Interface utilisateur

### Design

#### Caractéristiques
- **Responsive:** Adapté mobile, tablette, desktop
- **Moderne:** Design épuré et professionnel
- **Accessible:** Contraste et lisibilité optimisés
- **Intuitif:** Navigation claire et cohérente

#### Palette de couleurs
```css
:root {
    --primary: #3498db;      /* Bleu principal */
    --success: #2ecc71;      /* Vert (succès) */
    --danger: #e74c3c;       /* Rouge (danger) */
    --warning: #f39c12;      /* Orange (avertissement) */
    --info: #3498db;         /* Bleu (info) */
    --dark: #2c3e50;         /* Sombre (texte) */
    --light: #ecf0f1;        /* Clair (fond) */
}
```

### Structure des templates

#### base.html
Template parent avec:
- Navbar dynamique selon le rôle
- Système de messages flash
- Footer
- Styles globaux

#### Navigation

**Pour User:**
```
🏠 Mon Espace | 📅 Rendez-vous | 👤 Profil | 🚪 Déconnexion
```

**Pour Admin:**
```
📖 Contacts | 📁 Catégories | ➕ Ajouter | 📅 Rendez-vous | 👥 Admin | 👤 Profil | 🚪 Déconnexion
```

**Pour Super Admin:**
```
📖 Contacts | 📁 Catégories | ➕ Ajouter | 📅 Rendez-vous | 👥 Admin | ⚙️ Super Admin | 👤 Profil | 🚪 Déconnexion
```

### Pages principales

#### 1. Page de connexion (login.html)
- Formulaire d'authentification
- Lien vers inscription
- Messages d'erreur clairs
- Design centré et épuré

#### 2. Page d'inscription (register.html)
- Formulaire complet
- Validation côté client
- Confirmation de mot de passe
- Redirection automatique

#### 3. Liste des patients (contacts.html)
- Grille de cartes patients
- Barre de recherche
- Compteur de résultats
- Actions rapides (modifier, supprimer)
- Design adaptatif

#### 4. Ajout/Modification patient (add.html, edit.html)
- Formulaire complet
- Champs organisés par sections
- Validation en temps réel
- Boutons d'action clairs

#### 5. Tableau de bord patient (patient_dashboard.html)
- Vue d'ensemble personnalisée
- Prochains rendez-vous
- Informations de contact
- Actions rapides

#### 6. Gestion des rendez-vous (appointments.html)
- Liste chronologique
- Filtres par date
- Statut visuel (couleurs)
- Actions (annuler, modifier)

#### 7. Panel admin (admin.html)
- Dashboard administratif
- Statistiques clés
- Gestion des utilisateurs
- Actions rapides

### Composants réutilisables

#### Cartes (Cards)
```html
<div class="contact-card">
    <div class="contact-header">...</div>
    <div class="contact-body">...</div>
    <div class="contact-footer">...</div>
</div>
```

#### Boutons
```html
<button class="btn btn-primary">Action</button>
<button class="btn btn-success">Succès</button>
<button class="btn btn-danger">Danger</button>
<button class="btn btn-warning">Avertissement</button>
```

#### Messages Flash
```html
<div class="alert alert-success">Message de succès</div>
<div class="alert alert-error">Message d'erreur</div>
<div class="alert alert-info">Message d'information</div>
```

#### Formulaires
```html
<form method="POST">
    <div class="form-group">
        <label>Label</label>
        <input type="text" name="field" required>
    </div>
    <button type="submit" class="btn btn-primary">Envoyer</button>
</form>
```

---

## ⚙️ Configuration

### Fichier .env

L'application utilise un fichier `.env` pour stocker les configurations sensibles.

#### Étapes de configuration

1. **Copier le fichier exemple:**
```bash
cp .env.example .env
```

2. **Éditer le fichier .env:**

#### Configuration Flask
```env
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
DATABASE_NAME=contacts.db
```

### Variables d'environnement détaillées

| Variable | Type | Défaut | Description |
|----------|------|--------|-------------|
| `SECRET_KEY` | string | random | Clé secrète Flask (sessions) |
| `DATABASE_NAME` | string | contacts.db | Nom du fichier de base de données |

---

## 🚀 Installation et déploiement

### Prérequis

- **Python 3.8+**
- **pip** (gestionnaire de paquets Python)
- **Git** (optionnel)

### Installation locale

#### 1. Cloner ou télécharger le projet
```bash
# Via Git
git clone <repository-url>
cd carnet-dresse-all/mnt/user-data/outputs/v2.3.0

# Ou télécharger et extraire l'archive
```

#### 2. Créer un environnement virtuel (recommandé)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

#### 4. Configurer l'application
```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer .env avec vos paramètres
notepad .env  # Windows
nano .env     # Linux/Mac
```

#### 5. Lancer l'application
```bash
python main.py
```

#### 6. Accéder à l'application
```
URL locale: http://localhost:5000
URL réseau: http://0.0.0.0:5000
```

#### 7. Connexion initiale
```
Username: admin
Password: admin123
```

⚠️ **Changez immédiatement ce mot de passe!**

### Installation en production

#### Configuration recommandée

##### 1. Utiliser Gunicorn (Linux)
```bash
# Installer Gunicorn
pip install gunicorn

# Lancer avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

##### 2. Utiliser Nginx (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

##### 3. Sécuriser avec HTTPS (Let's Encrypt)
```bash
# Installer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtenir un certificat
sudo certbot --nginx -d votre-domaine.com
```

##### 4. Configurer comme service systemd
```ini
[Unit]
Description=Cabinet Medical Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

#### Déploiement sur serveur Windows

##### 1. Installer comme service Windows
Utiliser `nssm` (Non-Sucking Service Manager):
```bash
nssm install CabinetMedical "C:\path\to\python.exe" "C:\path\to\main.py"
```

##### 2. Configurer IIS comme reverse proxy
Installer ARR (Application Request Routing) et URL Rewrite

### Déploiement cloud

#### Heroku
```bash
# Créer Procfile
echo "web: gunicorn app:app" > Procfile

# Déployer
heroku create mon-cabinet-medical
git push heroku main
```

#### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "main.py"]
```

```bash
# Construire l'image
docker build -t cabinet-medical .

# Lancer le conteneur
docker run -p 5000:5000 cabinet-medical
```

---

## 🔒 Sécurité

### Mesures de sécurité implémentées

#### 1. Authentification et autorisation
- ✅ Hachage des mots de passe (pbkdf2:sha256)
- ✅ Salt aléatoire pour chaque mot de passe
- ✅ Gestion des sessions sécurisée
- ✅ Contrôle d'accès basé sur les rôles (RBAC)
- ✅ Décorateurs de protection des routes

#### 2. Protection des données
- ✅ Variables d'environnement pour les secrets
- ✅ Fichier .env exclu du contrôle de version
- ✅ Base de données SQLite avec transactions
- ✅ Timestamps sur toutes les opérations

#### 3. Validation des entrées
- ✅ Validation côté serveur
- ✅ Échappement des données (Jinja2)
- ✅ Protection contre les injections SQL (paramétrisées)
- ✅ Validation des types de données

#### 4. Gestion des erreurs
- ✅ Messages d'erreur génériques (pas de détails sensibles)
- ✅ Logging des erreurs
- ✅ Gestion des exceptions
- ✅ Timeout sur les connexions externes

### Bonnes pratiques recommandées

#### Au premier lancement
1. ✅ Changer le mot de passe admin par défaut
2. ✅ Générer une SECRET_KEY unique et forte
3. ✅ Limiter l'accès au réseau (firewall)

#### En production
1. ✅ Désactiver le mode debug Flask
2. ✅ Utiliser HTTPS (certificat SSL/TLS)
3. ✅ Sauvegarder régulièrement la base de données
4. ✅ Monitorer les logs d'accès
5. ✅ Mettre à jour les dépendances
6. ✅ Restreindre les permissions fichiers
7. ✅ Utiliser un reverse proxy (Nginx/Apache)
8. ✅ Implémenter un rate limiting

#### Gestion des accès
1. ✅ Principe du moindre privilège
2. ✅ Révision régulière des utilisateurs
3. ✅ Désactivation des comptes inactifs
4. ✅ Audit trail des actions critiques

### Checklist de sécurité

**Configuration:**
- [ ] SECRET_KEY unique et complexe
- [ ] Mode debug désactivé en production
- [ ] HTTPS configuré
- [ ] Firewall configuré
- [ ] .env non versionné

**Authentification:**
- [ ] Mot de passe admin changé
- [ ] Politique de mot de passe forte
- [ ] Sessions expirées après inactivité
- [ ] Déconnexion automatique

**Données:**
- [ ] Sauvegardes automatiques
- [ ] Chiffrement des données sensibles (prévu)
- [ ] Logs d'accès activés
- [ ] Rétention des logs définie

**Réseau:**
- [ ] Ports inutiles fermés
- [ ] Accès SSH sécurisé
- [ ] Rate limiting activé
- [ ] CORS configuré

### Vulnérabilités connues et mitigations

| Vulnérabilité | Impact | Statut | Mitigation |
|---------------|--------|--------|------------|
| Session Fixation | Moyen | ✅ Mitigé | Régénération session à login |
| CSRF | Élevé | ⚠️ À implémenter | Flask-WTF recommandé |
| XSS | Moyen | ✅ Mitigé | Échappement Jinja2 |
| SQL Injection | Élevé | ✅ Mitigé | Requêtes paramétrées |
| Brute Force | Moyen | ⚠️ Partiel | Rate limiting recommandé |

### Recommandations futures

1. **Implémenter CSRF protection** avec Flask-WTF
2. **Ajouter 2FA (Two-Factor Authentication)**
3. **Implémenter rate limiting** avec Flask-Limiter
4. **Chiffrement des données sensibles** dans la BDD
5. **Audit logging** complet
6. **Password policies** (complexité, expiration)
7. **Lockout après échecs de connexion**
8. **CAPTCHA** sur le formulaire de connexion

---

## 📖 Guide d'utilisation

### Pour les Super Admins

#### Premier lancement
1. **Se connecter avec les identifiants par défaut**
   - Username: `admin`
   - Password: `admin123`

2. **Changer immédiatement le mot de passe**
   - Aller dans Profil
   - Cliquer sur "Modifier le mot de passe"
   - Choisir un mot de passe fort

3. **Créer les premiers utilisateurs**
   - Aller dans Admin → Créer un utilisateur
   - Créer des comptes admin pour le personnel
   - Créer des comptes user pour les patients

#### Gestion quotidienne
1. **Tableau de bord Super Admin**
   - Vue d'ensemble complète
   - Statistiques système
   - Gestion utilisateurs
   - Configuration système

2. **Gestion des utilisateurs**
   - Créer de nouveaux comptes
   - Modifier les rôles
   - Désactiver/Supprimer des comptes
   - Voir l'activité des utilisateurs

3. **Maintenance**
   - Vérifier les logs d'erreur
   - Surveiller l'utilisation
   - Sauvegarder la base de données
   - Mettre à jour l'application

### Pour les Admins

#### Gestion des patients

1. **Ajouter un nouveau patient**
   - Cliquer sur "➕ Ajouter"
   - Remplir le formulaire complet
   - Sauvegarder

2. **Rechercher un patient**
   - Utiliser la barre de recherche
   - Taper nom, email ou téléphone
   - Les résultats s'affichent automatiquement

3. **Modifier un patient**
   - Cliquer sur "✏️ Modifier"
   - Mettre à jour les informations
   - Sauvegarder

4. **Supprimer un patient**
   - Cliquer sur "➖ Supprimer"
   - Confirmer la suppression
   - ⚠️ Action irréversible!

#### Gestion des rendez-vous

1. **Voir tous les rendez-vous**
   - Cliquer sur "📅 Rendez-vous"
   - Vue chronologique
   - Filtrer par date ou patient

2. **Annuler un rendez-vous**
   - Depuis la liste des RDV
   - Cliquer sur "Annuler"
   - Confirmer

### Pour les Patients (Users)

#### Mon espace patient

1. **Première connexion**
   - Utiliser les identifiants fournis par l'admin
   - Ou s'inscrire via le formulaire d'inscription
   - Se connecter

2. **Tableau de bord**
   - Vue d'ensemble de mes informations
   - Mes prochains rendez-vous
   - Accès rapide aux actions

3. **Modifier mon profil**
   - Cliquer sur "👤 Profil"
   - Mettre à jour mes informations
   - Changer mon mot de passe

#### Rendez-vous

1. **Réserver un rendez-vous**
   - Cliquer sur "📅 Rendez-vous"
   - Cliquer sur "Réserver un rendez-vous"
   - Choisir la date et l'heure
   - Ajouter des notes (optionnel)
   - Confirmer

2. **Voir mes rendez-vous**
   - Liste de mes RDV à venir
   - Liste de mes RDV passés
   - Statut de chaque RDV

3. **Annuler un rendez-vous**
   - Depuis la liste de mes RDV
   - Cliquer sur "Annuler"
   - Confirmer

### Cas d'usage courants

#### Scénario 1: Patient réserve un RDV
1. Patient se connecte
2. Va dans "📅 Rendez-vous"
3. Clique sur "Réserver"
4. Choisit date et heure
5. Valide
6. Reçoit confirmation

#### Scénario 2: Gestion d'une nouvelle catégorie
1. Admin va dans "📁 Catégories"
2. Clique sur "Ajouter une catégorie"
3. Nomme la catégorie (ex: "Diabète")
4. Sauvegarde
5. Peut maintenant assigner des patients à cette catégorie

---

## 🆘 Dépannage

### Problèmes courants

#### L'application ne démarre pas
**Symptômes:** Erreur au lancement de `python main.py`

**Solutions:**
1. Vérifier que Python 3.8+ est installé:
   ```bash
   python --version
   ```
2. Vérifier les dépendances:
   ```bash
   pip install -r requirements.txt
   ```
3. Vérifier les permissions sur le dossier

#### Erreur de connexion à la base de données
**Symptômes:** "Unable to open database file"

**Solutions:**
1. Vérifier que le fichier `contacts.db` existe
2. Vérifier les permissions en écriture
3. Supprimer et recréer (perte de données):
   ```bash
   rm contacts.db
   python main.py
   ```

#### Erreur 404 sur les pages
**Symptômes:** Page non trouvée

**Solutions:**
1. Vérifier que le serveur est démarré
2. Vérifier l'URL (http://localhost:5000)
3. Vérifier que vous êtes connecté
4. Vérifier vos permissions (rôle)

#### Session expirée constamment
**Symptômes:** Déconnexion fréquente

**Solutions:**
1. Vérifier que SECRET_KEY est définie dans `.env`
2. Ne pas utiliser de navigation privée
3. Autoriser les cookies
4. Vérifier la configuration du navigateur

### Logs et debugging

#### Activer les logs détaillés
```python
# Dans app.py
app.config['DEBUG'] = True
```

#### Consulter les logs Flask
Les logs s'affichent dans la console où vous avez lancé `python main.py`

#### Vérifier la base de données
```bash
# Installer sqlite3
sqlite3 contacts.db

# Commandes SQLite
.tables              # Lister les tables
.schema contacts     # Voir la structure
SELECT * FROM users; # Voir les utilisateurs
.quit                # Quitter
```

### Support et assistance

#### Documentation
- `README.md`: Documentation principale
- `README_CABINET_MEDICAL.md`: Guide cabinet médical
- `FIRST_LAUNCH.md`: Guide premier lancement
- `SECURITY.md`: Guide de sécurité

#### Communauté
- Créer une issue sur GitHub
- Consulter les issues existantes
- Contribuer au projet

---

## 📝 Changelog et versions

### Version 2.3.0 (v6 - Application Web) - Actuelle
**Date:** 2026

**Nouveautés:**
- ✨ Refonte complète en application web Flask
- ✨ Interface utilisateur moderne et responsive
- ✨ Système d'authentification complet
- ✨ Gestion des rôles (super_admin, admin, user)
- ✨ Gestion des rendez-vous
- ✨ Système de catégories
- ✨ Panel d'administration
- ✨ Dashboard patient personnalisé

**Améliorations:**
- 🔒 Sécurité renforcée (hachage pbkdf2:sha256)
- 🔒 Contrôle d'accès granulaire
- 📊 Base de données SQLite optimisée
- 🎨 Design professionnel et moderne
- 📱 Interface responsive
- ⚡ Performance améliorée

**Corrections:**
- 🐛 Correction des problèmes de sessions
- 🐛 Correction des erreurs de validation
- 🐛 Amélioration de la gestion des erreurs

### Versions précédentes
- **v5:** Application console avec menu interactif
- **v4:** Ajout de la gestion des catégories
- **v3:** Ajout de la base de données SQLite
- **v2:** Ajout des catégories
- **v1:** Version initiale console basique

---

## 🔮 Roadmap et fonctionnalités futures

### Court terme (v2.4.0)
- [ ] Protection CSRF avec Flask-WTF
- [ ] Rate limiting avec Flask-Limiter
- [ ] Pagination des listes
- [ ] Export des données (CSV, PDF)
- [ ] Filtres avancés de recherche
- [ ] Calendrier visuel pour les RDV
- [ ] Notifications par email (optionnel)

### Moyen terme (v3.0.0)
- [ ] Authentification à deux facteurs (2FA)
- [ ] Upload de documents patients
- [ ] Gestion des prescriptions
- [ ] Historique médical complet
- [ ] Statistiques avancées et graphiques
- [ ] API REST pour intégrations
- [ ] Application mobile (React Native)

### Long terme (v4.0.0)
- [ ] Visioconférence intégrée
- [ ] Paiement en ligne
- [ ] Multi-cabinet et multi-praticiens
- [ ] Synchronisation cloud
- [ ] Conformité RGPD complète
- [ ] Internationalisation (i18n)

---

## 🤝 Contribution

### Comment contribuer

1. **Fork** le projet
2. **Créer** une branche pour votre fonctionnalité
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. **Commiter** vos changements
   ```bash
   git commit -m "Ajout de ma fonctionnalité"
   ```
4. **Pusher** vers la branche
   ```bash
   git push origin feature/ma-fonctionnalite
   ```
5. **Ouvrir** une Pull Request

### Guidelines

- Suivre les conventions PEP 8 pour Python
- Commenter le code complexe
- Écrire des tests si possible
- Mettre à jour la documentation
- Respecter la structure existante

---

## 📄 Licence

Ce projet est sous licence **MIT**.

### Résumé de la licence MIT
- ✅ Utilisation commerciale autorisée
- ✅ Modification autorisée
- ✅ Distribution autorisée
- ✅ Utilisation privée autorisée
- ⚠️ Aucune garantie fournie
- ⚠️ Limitation de responsabilité

---

## 👥 Crédits

### Développeurs
- **Équipe de développement:** SDIA Python OOP Project

### Technologies utilisées
- **Flask:** Framework web Python
- **SQLite:** Base de données
- **Werkzeug:** Sécurité et utilitaires

### Remerciements
- Communauté Flask
- Contributors
- Beta testers

---

## 📞 Contact et support

### Support technique
- **Email:** support@cabinet-medical.example
- **Documentation:** Voir les fichiers README
- **Issues:** GitHub Issues

### Informations commerciales
- **Site web:** www.cabinet-medical.example
- **Email:** contact@cabinet-medical.example

---

## ⚖️ Mentions légales

### Données personnelles
Cette application traite des données de santé sensibles. Il est de la responsabilité de l'utilisateur de:
- Assurer la conformité RGPD
- Obtenir les consentements nécessaires
- Sécuriser les données
- Respecter le secret médical

### Disclaimer
Cette application est fournie "telle quelle" sans garantie d'aucune sorte. Les développeurs ne peuvent être tenus responsables des:
- Pertes de données
- Failles de sécurité
- Non-conformités légales
- Problèmes médicaux ou juridiques

### Utilisation recommandée
- ✅ Environnement de test et développement
- ✅ Petits cabinets médicaux
- ⚠️ Nécessite audits de sécurité pour production
- ⚠️ Consultation juridique recommandée

---

**Fin de la documentation**

**Version du document:** 1.0  
**Dernière mise à jour:** 2026  
**Application version:** v2.3.0

---

*Cette documentation est vivante et sera mise à jour régulièrement.*

