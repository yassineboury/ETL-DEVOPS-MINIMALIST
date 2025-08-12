#!/usr/bin/env python3
"""
Script d'export des projets GitLab vers Excel
Version pour extraire les projets avec les champs spécifiés
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Ajouter les dossiers au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.exporters.excel_exporter import export_projects_to_excel
from gitlab_tools.extractors.projects_extractor import (
    extract_projects,
)


def main():
    """Export principal des projets GitLab"""
    print("🚀 KENOBI DEVOPS - Export Projets GitLab")
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

        # 2. Extraction des projets
        print("\n📁 Extraction des projets GitLab...")

        # Option: Tous les projets (actifs + archivés)
        projects_df = extract_projects(gl, include_archived=True)

        # Alternative: Seulement les projets actifs
        # projects_df = extract_active_projects(gl)

        if projects_df.empty:
            print("❌ Aucun projet trouvé")
            gitlab_client.disconnect()
            return False

        # 3. Export vers Excel
        print(f"\n📁 Export de {len(projects_df)} projets vers Excel...")

        file_path = export_projects_to_excel(
            projects_df,
            filename="gitlab_projects.xlsx"
        )

        # 4. Fermer la connexion
        gitlab_client.disconnect()

        # 5. Résumé
        print("\n" + "=" * 60)
        print("🎉 EXPORT TERMINÉ AVEC SUCCÈS!")
        print(f"📊 {len(projects_df)} projets exportés")

        # Statistiques rapides
        if 'etat' in projects_df.columns:
            states = projects_df['etat'].value_counts()
            print(f"   • États: {states.to_dict()}")

        if 'archivé' in projects_df.columns:
            archived = projects_df['archivé'].value_counts()
            print(f"   • Archivage: {archived.to_dict()}")

        print("\n📁 Fichier créé:")
        if file_path:
            print(f"   ✅ Projets GitLab: {Path(file_path).name}")

        print(f"\n📂 Dossier: {project_root}/exports/gitlab/")

        return True

    except Exception as e:
        print(f"❌ Erreur durant l'export: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
