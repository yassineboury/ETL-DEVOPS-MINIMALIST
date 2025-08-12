#!/usr/bin/env python3
"""
👥 EXTRACTION GROUPES GITLAB SEULEMENT
Script simple pour extraire uniquement les groupes GitLab vers Excel
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le projet au path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.extractors.groups_extractor import GroupsExtractor
from gitlab_tools.exporters.excel_exporter import export_groups_to_excel


def extract_groups_to_excel():
    """
    Extraction simple des groupes GitLab vers Excel
    """
    print("👥 EXTRACTION GROUPES GITLAB")
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
        
        # 3. Extraction des groupes
        print("👥 Extraction des groupes...")
        groups_extractor = GroupsExtractor(gl)
        groups_df = groups_extractor.extract()
        
        if groups_df.empty:
            print("❌ Aucun groupe trouvé")
            return False
            
        groups_count = len(groups_df)
        print(f"✅ {groups_count} groupes extraits")
        
        # Statistiques rapides
        if 'is_top_level' in groups_df.columns:
            top_level_count = groups_df['is_top_level'].sum()
            sub_groups_count = groups_count - top_level_count
            print(f"📊 Groupes racine: {top_level_count}, Sous-groupes: {sub_groups_count}")

        if 'total_members' in groups_df.columns:
            total_members = groups_df['total_members'].sum()
            print(f"👥 Total membres: {total_members}")
            
        # 4. Export vers Excel
        print("📊 Export vers Excel...")
        excel_file = export_groups_to_excel(groups_df, filename="gitlab_groups.xlsx")
        
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
    print("🚀 Lancement de l'extraction groupes...")
    success = extract_groups_to_excel()
    
    if success:
        print("\n🎉 Extraction terminée avec succès!")
    else:
        print("\n❌ Extraction échouée")
    
    sys.exit(0 if success else 1)
