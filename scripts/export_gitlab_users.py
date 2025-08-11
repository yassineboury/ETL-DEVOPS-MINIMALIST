#!/usr/bin/env python3
"""
Script d'export des utilisateurs GitLab vers Excel
Version simplifiée pour structure organisée
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter les dossiers au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.extractors.users_extractor import extract_human_users
from gitlab_tools.exporters.excel_exporter import export_users_to_excel

def main():
    """Export principal des utilisateurs GitLab"""
    print("🚀 KENOBI DEVOPS - Export Utilisateurs GitLab")
    print("=" * 60)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    try:
        # 1. Connexion à GitLab
        print("🔗 Connexion à GitLab ONCF...")
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()
        
        if not gl:
            print("❌ Impossible de se connecter à GitLab")
            return False
        
        print("✅ Connexion GitLab établie")
        
        # 2. Extraction des utilisateurs humains
        print("\n👥 Extraction des utilisateurs humains...")
        users_df = extract_human_users(gl, include_blocked=True)
        
        if users_df.empty:
            print("❌ Aucun utilisateur trouvé")
            gitlab_client.disconnect()
            return False
        
        # 4. Export vers Excel
        print(f"\n📁 Export de {len(users_df)} utilisateurs vers Excel...")
        
        # Export complet (actifs + bloqués + désactivés)
        file_path = export_users_to_excel(
            users_df, 
            filename="gitlab_users.xlsx"
        )
        
        # 5. Fermer la connexion
        gitlab_client.disconnect()
        
        # 6. Résumé
        print("\n" + "=" * 60)
        print("🎉 EXPORT TERMINÉ AVEC SUCCÈS!")
        print(f"📊 {len(users_df)} utilisateurs humains exportés")
        
        print(f"\n📁 Fichier créé:")
        if file_path:
            print(f"   ✅ Utilisateurs GitLab: {Path(file_path).name}")
        
        print(f"\n📂 Dossier: {project_root}/exports/gitlab/")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur durant l'export: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
