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
            project_data = _extract_single_project_data(project)
            data.append(project_data)
        
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Format dates pour Power BI
            df = DateFormatter.format_date_columns(df)
            print(f"✅ {len(df)} projets extraits")
        
        return df
        
    except python_gitlab.GitlabError as e:
        print(f"❌ Erreur GitLab: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Erreur extraction projets: {e}")
        return pd.DataFrame()


def _extract_single_project_data(project) -> dict:
    """Extrait les données d'un projet unique"""
    branches_count = _get_branches_count(project)
    namespace_type = _get_namespace_type(project)
    
    return {
        'id_projet': project.id,
        'nom': project.name,
        'nom_complet': project.path_with_namespace,
        'archive': 'Oui' if getattr(project, 'archived', False) else 'Non',
        'date_creation': project.created_at,
        'date_derniere_activite': project.last_activity_at,
        'total_branches': branches_count,
        'type_namespace': namespace_type
    }


def _get_branches_count(project) -> int:
    """Récupère le nombre de branches"""
    try:
        return len(project.branches.list(get_all=False))  # Limite à 20 pour performance
    except python_gitlab.GitlabError:
        return 0


def _get_namespace_type(project) -> str:
    """Récupère le type de namespace"""
    try:
        if hasattr(project, 'namespace') and project.namespace:
            # Le namespace est un dictionnaire, pas un objet
            kind = project.namespace.get('kind', 'user')
            return 'Groupe' if kind == 'group' else 'Utilisateur'
    except (AttributeError, TypeError):
        pass
    return 'Utilisateur'
