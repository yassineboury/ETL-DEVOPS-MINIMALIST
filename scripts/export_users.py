#!/usr/bin/env python3
"""
Script d'export des utilisateurs GitLab vers Excel
Exporte tous les utilisateurs humains (actifs et bloqués) vers un fichier Excel
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter les dossiers au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "gitlab"))

from gitlab.gitlab_client import create_gitlab_client
from gitlab.gitlab_users import extract_and_export_users, extract_and_export_active_users

def main():
    """Export principal des utilisateurs"""
    print("🚀 KENOBI DEVOPS - Export Utilisateurs GitLab")
    print("=" * 60)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    try:
        # Créer le client GitLab
        print("🔗 Connexion à GitLab ONCF...")
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()
        
        if not gl:
            print("❌ Impossible de se connecter à GitLab")
            return False
        
        print("✅ Connexion GitLab établie")
        
        # Option 1: Tous les utilisateurs humains (recommandé)
        print("\n📊 Export de tous les utilisateurs humains...")
        file_path = extract_and_export_users(
            gl, 
            include_blocked=True, 
            filename="gitlab_users_complet.xlsx"
        )
        
        # Option 2: Uniquement les utilisateurs actifs
        print("\n📊 Export des utilisateurs actifs seulement...")
        active_file = extract_and_export_active_users(
            gl, 
            filename="gitlab_users_actifs.xlsx"
        )
        
        # Fermer la connexion
        gitlab_client.disconnect()
        
        # Résumé
        print("\n" + "=" * 60)
        print("🎉 EXPORT TERMINÉ AVEC SUCCÈS!")
        print("📁 Fichiers créés:")
        if file_path:
            print(f"   ✅ Tous les utilisateurs: {Path(file_path).name}")
        if active_file:
            print(f"   ✅ Utilisateurs actifs: {Path(active_file).name}")
        
        print(f"📂 Dossier: {Path(__file__).parent / 'extracts'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur durant l'export: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
