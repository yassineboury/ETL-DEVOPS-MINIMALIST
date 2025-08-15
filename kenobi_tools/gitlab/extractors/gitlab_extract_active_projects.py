"""
Extracteur de projets actifs GitLab
Module pour extraire les informations des projets actifs GitLab (non archivés)
Refactorisé pour utiliser common_project_utils et éliminer la duplication
"""
import pandas as pd
import gitlab as python_gitlab
from typing import Dict, Any

from .common_project_utils import extract_all_projects
from ...utils.constants import STATUS_YES, STATUS_NO, PROJETS_ARCHIVES_PATH


def extract_active_projects(gl_client: python_gitlab.Gitlab) -> pd.DataFrame:
    """
    Extrait uniquement les projets actifs (non archivés)

    Args:
        gl_client: Client GitLab authentifié

    Returns:
        DataFrame avec les projets actifs uniquement
    """
    print("🔍 Extraction des projets actifs uniquement...")
    
    # Extraire tous les projets (actifs seulement, archived=False par défaut)
    all_projects_df = extract_all_projects(gl_client, include_archived=False)
    
    if all_projects_df.empty:
        print("⚠️ Aucun projet trouvé")
        return pd.DataFrame()
    
    # Filtrer pour exclure les projets dans projets-archives/
    active_projects = []
    
    for index, project in all_projects_df.iterrows():
        # Exclure les projets dans le dossier projets-archives/
        if 'nom_complet' in project and str(project['nom_complet']).startswith(PROJETS_ARCHIVES_PATH):
            continue
            
        # Exclure les projets officiellement archivés (sécurité supplémentaire)
        if 'etat' in project and project['etat'] == 'Archivé':
            continue
            
        active_projects.append(project)
    
    active_df = pd.DataFrame(active_projects)
    
    if not active_df.empty:
        print(f"✅ {len(active_df)} projets actifs extraits")
        print("📋 Données brutes prêtes pour Power BI")
    else:
        print("⚠️ Aucun projet actif trouvé")
    
    return active_df


# Fonction get_project_statistics supprimée - Power BI s'occupe des statistiques


if __name__ == "__main__":
    """Extraction et export Excel des projets actifs GitLab - VERSION REFACTORISÉE"""
    import sys
    from pathlib import Path

    # Ajouter les chemins pour les imports
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    from ..client.gitlab_client import GitLabClient

    print("🧪 Extraction et export Excel des projets actifs GitLab - VERSION SIMPLIFIÉE")
    print("=" * 60)

    try:
        # Créer le client GitLab  
        client = GitLabClient()
        gl = client.connect()

        # Extraction directe des projets actifs
        print("\n📊 Extraction des projets actifs...")
        active_projects = extract_active_projects(gl)

        if not active_projects.empty:
            print(f"   ✅ {len(active_projects)} projets actifs extraits")
            print("   📋 Données prêtes pour Power BI")
        else:
            print("   ⚠️ Aucun projet actif trouvé")

        client.disconnect()

        # Export Excel immédiat
        print("\n📁 Export Excel:")
        if not active_projects.empty:
            try:
                # Import de l'exporteur Excel
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
                
                # Créer l'exporteur et générer le fichier Excel
                exporter = GitLabExcelExporter()
                excel_path = exporter.export_projects(active_projects, "gitlab_active_projects.xlsx")
                
                if excel_path:
                    print(f"✅ Fichier Excel généré: {excel_path}")
                    print("\n🎉 Export terminé avec succès!")
                else:
                    print("❌ Erreur lors de la génération du fichier Excel")
                    sys.exit(1)
            except Exception as excel_error:
                print(f"❌ Erreur export Excel: {excel_error}")
                sys.exit(1)
        else:
            print("❌ Aucun projet actif à exporter")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        sys.exit(1)
