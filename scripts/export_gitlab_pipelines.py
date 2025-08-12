#!/usr/bin/env python3
"""
Script d'extraction des pipelines GitLab
Génère un fichier Excel avec les données des pipelines CI/CD
"""

import sys
from datetime import datetime
from pathlib import Path

# Ajouter le chemin parent pour les imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.exporters.excel_exporter import export_to_excel
from gitlab_tools.extractors.pipelines_extractor import extract_pipelines


def main():
    """Fonction principale d'extraction des pipelines"""
    print("🔄 EXTRACTION DES PIPELINES GITLAB")
    print("=" * 60)

    try:
        # Créer le client GitLab
        print("🔗 Connexion à GitLab...")
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()

        # Extraire les pipelines (limité à 20 par projet pour éviter la surcharge)
        print("\n📊 Extraction des pipelines...")
        pipelines_df = extract_pipelines(gl, limit_per_project=20)

        if pipelines_df.empty:
            print("⚠️ Aucun pipeline trouvé")
            return

        # Afficher les statistiques
        print("\n📈 Statistiques extraites:")
        print(f"   • Total pipelines: {len(pipelines_df)}")

        if 'statut' in pipelines_df.columns:
            status_counts = pipelines_df['statut'].value_counts()
            print("   • Répartition par statut:")
            for status, count in status_counts.head(5).items():
                print(f"     - {status}: {count}")

        if 'environnement_cible' in pipelines_df.columns:
            env_counts = pipelines_df['environnement_cible'].value_counts()
            print("   • Répartition par environnement:")
            for env, count in env_counts.head(5).items():
                print(f"     - {env}: {count}")

        # Exporter vers Excel
        print("\n💾 Export vers Excel...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gitlab_pipelines_{timestamp}"

        output_file = export_to_excel(
            pipelines_df,
            filename=filename,
            sheet_name="Pipelines GitLab",
            subfolder="gitlab"
        )

        print(f"✅ Fichier généré: {output_file}")

        # Fermer la connexion
        gitlab_client.disconnect()

    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

    print("\n🎉 Extraction terminée avec succès!")


if __name__ == "__main__":
    main()
