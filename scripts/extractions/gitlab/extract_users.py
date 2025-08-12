#!/usr/bin/env python3
"""
🎯 EXTRACTION UTILISATEURS GITLAB SEULEMENT
Script simple pour extraire uniquement les utilisateurs GitLab vers Excel
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le projet au path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.extractors.users_extractor import extract_human_users
from gitlab_tools.exporters.excel_exporter import export_users_to_excel


def extract_users_to_excel():
    """
    Extraction simple des utilisateurs GitLab vers Excel
    """
    print("👥 EXTRACTION UTILISATEURS GITLAB")
    print("=" * 40)
    
    gitlab_client = None
    
    try:
        # 1. Charger la configuration
        print("🔑 Chargement de la configuration...")
        load_dotenv()
        
        # 2. Connexion GitLab
        print("🌐 Connexion à GitLab ONCF...")
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()
        
        if not gl:
            print("❌ Impossible de se connecter à GitLab")
            return False
            
        print("✅ Connexion GitLab établie")
        
        # 3. Extraction des utilisateurs
        print("👥 Extraction des utilisateurs humains...")
        users_df = extract_human_users(gl, include_blocked=True)
        
        if users_df.empty:
            print("❌ Aucun utilisateur trouvé")
            return False
            
        user_count = len(users_df)
        print(f"✅ {user_count} utilisateurs extraits")
        
        # Statistiques rapides
        if 'etat' in users_df.columns:
            states = users_df['etat'].value_counts()
            print(f"📊 États: {states.to_dict()}")
            
        # 4. Export vers Excel
        print("📊 Export vers Excel...")
        excel_file = export_users_to_excel(users_df, filename="gitlab_users.xlsx")
        
        if excel_file:
            file_size = Path(excel_file).stat().st_size / 1024  # KB
            print(f"✅ Fichier créé: {Path(excel_file).name} ({file_size:.1f} KB)")
            print(f"📂 Emplacement: {excel_file}")
            return True
        else:
            print("❌ Erreur lors de la création du fichier Excel")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        # Fermer la connexion
        if gitlab_client:
            try:
                gitlab_client.disconnect()
                print("🔌 Connexion fermée")
            except:
                pass


if __name__ == "__main__":
    print("🚀 Lancement de l'extraction utilisateurs...")
    success = extract_users_to_excel()
    
    if success:
        print("\n🎉 Extraction terminée avec succès!")
    else:
        print("\n❌ Extraction échouée")
    
    sys.exit(0 if success else 1)
