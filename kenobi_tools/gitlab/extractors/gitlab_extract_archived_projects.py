"""
Extracteur de projets archivés GitLab
Module pour extraire les informations des projets archivés GitLab
Refactorisé pour utiliser common_project_utils et éliminer la duplication
"""
import pandas as pd
import gitlab as python_gitlab

from .common_project_utils import extract_all_projects
from ...utils.constants import PROJET_ARCHIVE_STATUS, PROJETS_ARCHIVES_PATH


def _is_project_archived(project) -> bool:
    """
    Détermine si un projet est archivé selon nos critères
    
    Args:
        project: Ligne du DataFrame représentant un projet
        
    Returns:
        True si le projet est archivé, False sinon
    """
    # Condition 1: projet officiellement archivé
    if PROJET_ARCHIVE_STATUS in project and project[PROJET_ARCHIVE_STATUS] == 'Oui':
        return True
    
    # Condition 2: projet dans le dossier projets-archives/
    if 'nom_complet' in project and str(project['nom_complet']).startswith(PROJETS_ARCHIVES_PATH):
        return True
        
    return False


def extract_projects(gl_client: python_gitlab.Gitlab, include_archived: bool = False) -> pd.DataFrame:
    """
    Extrait les projets GitLab avec leurs informations principales
    Version simplifiée utilisant common_project_utils
    
    Args:
        gl_client: Instance du client GitLab
        include_archived: Inclure les projets archivés (défaut: False)
        
    Returns:
        DataFrame avec les informations des projets
    """
    # Utiliser la fonction commune avec ajout du champ 'archivé'
    df = extract_all_projects(gl_client, include_archived)
    
    if not df.empty:
        # Ajouter le champ 'archivé' basé sur l'état
        df[PROJET_ARCHIVE_STATUS] = df['etat'].apply(lambda x: "Oui" if x == "Archivé" else "Non")
    
    return df


def extract_active_projects(gl_client: python_gitlab.Gitlab) -> pd.DataFrame:
    """
    Extrait uniquement les projets actifs (non archivés)

    Args:
        gl_client: Client GitLab authentifié

    Returns:
        DataFrame avec les projets actifs uniquement
    """
    print("🔍 Extraction des projets actifs uniquement...")
    
    # Utiliser la fonction commune pour les projets non archivés
    df = extract_projects(gl_client, include_archived=False)
    
    if not df.empty:
        # Filtrer pour exclure les projets dans projets-archives/
        df = df[~df['nom_complet'].astype(str).str.startswith(PROJETS_ARCHIVES_PATH)]
        print(f"📦 {len(df)} projets actifs trouvés")
    
    return df


def extract_archived_projects(gl_client: python_gitlab.Gitlab) -> pd.DataFrame:
    """
    Extrait uniquement les projets archivés + projets dans projets-archives/

    Args:
        gl_client: Client GitLab authentifié

    Returns:
        DataFrame avec les projets archivés uniquement
    """
    print("🔍 Extraction des projets archivés uniquement...")
    
    # Extraire tous les projets (actifs + archivés)
    all_projects_df = extract_projects(gl_client, include_archived=True)
    
    if all_projects_df.empty:
        print("⚠️ Aucun projet trouvé")
        return pd.DataFrame()
    
    # Filtrer pour ne garder que les projets archivés OU ceux dans projets-archives/
    archived_projects = []
    
    for index, project in all_projects_df.iterrows():
        if _is_project_archived(project):
            archived_projects.append(project)
    
    archived_df = pd.DataFrame(archived_projects)
    
    if not archived_df.empty:
        print(f"📦 {len(archived_df)} projets archivés trouvés sur {len(all_projects_df)} total")
        # Compter les différents types
        official_archived = 0
        folder_archived = 0
        
        if PROJET_ARCHIVE_STATUS in archived_df.columns:
            official_archived = len(archived_df[archived_df[PROJET_ARCHIVE_STATUS] == 'Oui'])
        
        if 'nom_complet' in archived_df.columns:
            folder_archived = len(archived_df[archived_df['nom_complet'].astype(str).str.startswith(PROJETS_ARCHIVES_PATH)])
        
        print(f"  - {official_archived} projets officiellement archivés")
        print(f"  - {folder_archived} projets dans projets-archives/")
    else:
        print("⚠️ Aucun projet archivé trouvé")
    
    return archived_df


if __name__ == "__main__":
    """Extraction et export Excel des projets archivés GitLab - VERSION REFACTORISÉE"""
    import sys
    from pathlib import Path

    # Ajouter les chemins pour les imports
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    from client.gitlab_client import create_gitlab_client

    print("🧪 Extraction et export Excel des projets archivés GitLab")
    print("=" * 60)

    try:
        # Créer le client GitLab
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()

        # Extraction directe des projets archivés
        print("\n📊 Extraction des projets archivés...")
        archived_projects = extract_archived_projects(gl)

        if not archived_projects.empty:
            print(f"   ✅ {len(archived_projects)} projets archivés extraits")

        gitlab_client.disconnect()

        # Export Excel immédiat
        print("\n📁 Export Excel:")
        if not archived_projects.empty:
            try:
                # Import de l'exporteur Excel
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
                
                # Créer l'exporteur et générer le fichier Excel
                exporter = GitLabExcelExporter()
                excel_path = exporter.export_projects(archived_projects, "gitlab_archived_projects.xlsx")
                
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
            print("❌ Aucun projet archivé à exporter")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        sys.exit(1)
