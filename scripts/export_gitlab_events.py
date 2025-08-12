#!/usr/bin/env python3
"""
🎯 Script d'Export des Événements GitLab
Export les événements GitLab vers Excel pour analyse DevSecOps
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Ajouter les dossiers au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.exporters.excel_exporter import export_events_to_excel
from gitlab_tools.extractors.events_extractor import extract_events


def main():
    """Export des événements GitLab vers Excel"""
    print("📊 EXPORT DES ÉVÉNEMENTS GITLAB")
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

        # Extraire les événements
        print("\n📊 Extraction des événements...")
        events_df = extract_events(gl, include_archived=False)

        if events_df.empty:
            print("❌ Aucun événement trouvé")
            gitlab_client.disconnect()
            return False

        # Exporter vers Excel
        print(f"\n📁 Export de {len(events_df)} événements vers Excel...")
        file_path = export_events_to_excel(events_df, "gitlab_events.xlsx")

        if file_path:
            print(f"✅ Export réussi: {file_path}")

            # Afficher quelques statistiques
            print("\n📈 Statistiques:")
            print(f"   • Total événements: {len(events_df)}")
            if 'nom_action' in events_df.columns:
                print(f"   • Types d'actions: {events_df['nom_action'].nunique()}")
                top_actions = events_df['nom_action'].value_counts().head(3)
                for action, count in top_actions.items():
                    print(f"     - {action}: {count}")
            if 'id_projet' in events_df.columns:
                print(f"   • Projets concernés: {events_df['id_projet'].nunique()}")
            if 'id_auteur' in events_df.columns:
                print(f"   • Utilisateurs actifs: {events_df['id_auteur'].nunique()}")

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
