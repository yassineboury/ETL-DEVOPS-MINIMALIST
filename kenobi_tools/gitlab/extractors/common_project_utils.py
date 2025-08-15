"""
Utilitaires communs pour l'extraction des projets GitLab - VERSION ULTRA-SIMPLIFIÉE
Une seule fonction simple pour Power BI
Complexité cognitive visée: ≤ 8
"""
import pandas as pd
import gitlab as python_gitlab
from ...utils.date_utils import DateFormatter


def extract_all_projects(gl_client: python_gitlab.Gitlab, include_archived: bool = False) -> pd.DataFrame:
    """
    Extrait tous les projets GitLab - VERSION ULTRA-SIMPLE
    
    Args:
        gl_client: Client GitLab authentifié
        include_archived: Inclure les projets archivés
        
    Returns:
        DataFrame avec les données brutes pour Power BI
    """
    try:
        print(f"🔍 Extraction projets (archivés: {'Oui' if include_archived else 'Non'})...")
        
        # Récupération des projets
        projects = gl_client.projects.list(all=True, archived=include_archived)
        
        if not projects:
            print("⚠️ Aucun projet trouvé")
            return pd.DataFrame()
        
        # Construction des données brutes pour Power BI
        data = []
        for project in projects:
            data.append({
                'id Projet': project.id,
                'Nom': project.name,
                'Nom Complet': project.path_with_namespace,
                'Description': getattr(project, 'description', '') or '',
                'Visibilité': project.visibility,
                'Archivé': 'Oui' if getattr(project, 'archived', False) else 'Non',
                'Date Création': project.created_at,
                'Date Dernière Activité': project.last_activity_at,
                'URL Web': project.web_url,
                'Langage Principal': getattr(project, 'default_branch', ''),
                'Étoiles': getattr(project, 'star_count', 0),
                'Forks': getattr(project, 'forks_count', 0)
            })
        
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Format dates pour Power BI
            df = DateFormatter.format_date_columns(df)
            print(f"✅ {len(df)} projets extraits")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction projets: {e}")
        return pd.DataFrame()
