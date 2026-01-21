"""
Point d'entrée principal pour l'application web Flask
Version 6: Application Web

Ce fichier est un wrapper simple qui lance l'application Flask.
L'application réelle est définie dans app.py
"""

if __name__ == '__main__':
    # Importer et lancer l'application Flask
    from app import app
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║          📱 CARNET D'ADRESSES - VERSION WEB               ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    
    🚀 Lancement du serveur Flask...
    
    📍 URL: http://localhost:5000
    📍 URL réseau: http://0.0.0.0:5000
    
    🔧 Mode debug: Activé
    🔄 Rechargement automatique: Activé
    
    ⚠️  Pour arrêter le serveur: Ctrl+C
    
    ═══════════════════════════════════════════════════════════════
    """)
    
    # Lancer l'application Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
