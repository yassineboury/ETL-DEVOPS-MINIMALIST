"""
Extracteur de projets archivés GitLab - VERSION ULTRA-SIMPLIFIÉE POWER BI
Extraction pure sans statistiques - Power BI s'en charge !
Complexité cognitive visée: ≤ 8
"""
import pandas as pd
import gitlab as python_gitlab
from .common_project_utils import extract_all_projects


def extract_archived_projects(gl_client: python_gitlab.Gitlab) -> pd.DataFrame:
    """
    Extrait uniquement les projets archivés - VERSION SIMPLIFIÉE
    
    Args:
        gl_client: Client GitLab authentifié
        
    Returns:
        DataFrame avec les projets archivés uniquement
    """
    print("📦 Extraction des projets archivés...")
    
    # Extraire tous les projets archivés
    all_projects_df = extract_all_projects(gl_client, include_archived=True)
    
    if all_projects_df.empty:
        print("⚠️ Aucun projet trouvé")
        return pd.DataFrame()
    
    # Filtrer uniquement les archivés (noms techniques uniformisés)
    archive_condition = all_projects_df['archive'] == 'Oui' if 'archive' in all_projects_df.columns else pd.Series([False] * len(all_projects_df))
    path_condition = all_projects_df['nom_complet'].str.startswith('projets-archives/') if 'nom_complet' in all_projects_df.columns else pd.Series([False] * len(all_projects_df))
    
    archived_df = all_projects_df[archive_condition | path_condition].copy()
    
    # Assurer que c'est un DataFrame
    if not isinstance(archived_df, pd.DataFrame):
        archived_df = pd.DataFrame(archived_df)
    
    print(f"✅ {len(archived_df)} projets archivés extraits")
    print("📋 Données prêtes pour Power BI")
    
    return archived_df


if __name__ == "__main__":
    """Test simple du module"""
    import sys
    from pathlib import Path
    
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))
    
    from ..client.gitlab_client import GitLabClient
    
    print("🧪 Test extraction projets archivés - VERSION SIMPLIFIÉE")
    
    try:
        client = GitLabClient()
        gl = client.connect()
        
        df = extract_archived_projects(gl)
        print(f"📊 Résultat: {len(df)} projets archivés")
        
        client.disconnect()
        print("✅ Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
