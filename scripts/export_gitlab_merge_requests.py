#!/usr/bin/env python3
"""
🎯 Script d'Export des Merge Requests GitLab
Export les Merge Requests GitLab vers Excel pour analyse DevSecOps
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Ajouter les dossiers au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.exporters.excel_exporter import export_merge_requests_to_excel
from gitlab_tools.extractors.merge_requests_extractor import extract_merge_requests


def main():
    """Export des Merge Requests GitLab vers Excel"""
    print("📊 EXPORT DES MERGE REQUESTS GITLAB")
    print("=" * 50)

    try:
        # Charger les variables d'environnement
        load_dotenv()

        # Créer le client GitLab
        print("🔗 Connexion à GitLab...")
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()

        if not gl:
            print("❌ Impossible de se connecter à GitLab")
            return False

        print("✅ Connexion établie")

        # Extraire les Merge Requests
        print("\n📊 Extraction des Merge Requests...")
        mrs_df = extract_merge_requests(gl, include_archived=False)

        if mrs_df.empty:
            print("❌ Aucune Merge Request trouvée")
            gitlab_client.disconnect()
            return False

        # Exporter vers Excel
        print(f"\n📁 Export de {len(mrs_df)} Merge Requests vers Excel...")
        file_path = export_merge_requests_to_excel(mrs_df, "gitlab_merge_requests.xlsx")

        if file_path:
            print(f"✅ Export réussi: {file_path}")

            # Afficher quelques statistiques
            print("\n📈 Statistiques:")
            print(f"   • Total MR: {len(mrs_df)}")
            if 'etat' in mrs_df.columns:
                print(f"   • États: {mrs_df['etat'].nunique()}")
                top_states = mrs_df['etat'].value_counts().head(3)
                for state, count in top_states.items():
                    print(f"     - {state}: {count}")
            if 'id_projet' in mrs_df.columns:
                print(f"   • Projets concernés: {mrs_df['id_projet'].nunique()}")
            if 'id_auteur' in mrs_df.columns:
                print(f"   • Auteurs uniques: {mrs_df['id_auteur'].nunique()}")

            # Fermer la connexion
            gitlab_client.disconnect()
            return True
        else:
            print("❌ Erreur lors de l'export")
            gitlab_client.disconnect()
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
