"""
Extraction des projets GitLab
"""
import gitlab
import pandas as pd
from typing import List, Dict, Any


def extract_projects(gl_client: gitlab.Gitlab) -> pd.DataFrame:
    """
    Extrait la liste des projets GitLab
    
    Args:
        gl_client: Client GitLab authentifié
        
    Returns:
        DataFrame avec les informations des projets
    """
    print("🔍 Extraction des projets GitLab...")
    
    projects_data = []
    
    try:
        # Récupérer tous les projets (avec pagination automatique)
        projects = gl_client.projects.list(all=True, simple=True)
        
        for project in projects:
            project_info = {
                'id': project.id,
                'name': project.name,
                'path': project.path,
                'path_with_namespace': project.path_with_namespace,
                'description': getattr(project, 'description', ''),
                'visibility': project.visibility,
                'created_at': project.created_at,
                'last_activity_at': project.last_activity_at,
                'web_url': project.web_url,
                'default_branch': getattr(project, 'default_branch', 'main'),
                'archived': getattr(project, 'archived', False),
                'issues_enabled': getattr(project, 'issues_enabled', False),
                'merge_requests_enabled': getattr(project, 'merge_requests_enabled', False),
                'star_count': getattr(project, 'star_count', 0),
                'forks_count': getattr(project, 'forks_count', 0),
            }
            projects_data.append(project_info)
            
        print(f"✅ {len(projects_data)} projets extraits")
        return pd.DataFrame(projects_data)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des projets: {e}")
        return pd.DataFrame()


def extract_projects_by_ids(gl_client: gitlab.Gitlab, project_ids: List[int]) -> pd.DataFrame:
    """
    Extrait des projets spécifiques par leurs IDs
    
    Args:
        gl_client: Client GitLab authentifié
        project_ids: Liste des IDs des projets
        
    Returns:
        DataFrame avec les informations des projets
    """
    print(f"🔍 Extraction de {len(project_ids)} projets spécifiques...")
    
    projects_data = []
    
    for project_id in project_ids:
        try:
            project = gl_client.projects.get(project_id)
            
            project_info = {
                'id': project.id,
                'name': project.name,
                'path': project.path,
                'path_with_namespace': project.path_with_namespace,
                'description': getattr(project, 'description', ''),
                'visibility': project.visibility,
                'created_at': project.created_at,
                'last_activity_at': project.last_activity_at,
                'web_url': project.web_url,
                'default_branch': getattr(project, 'default_branch', 'main'),
                'archived': getattr(project, 'archived', False),
                'issues_enabled': getattr(project, 'issues_enabled', False),
                'merge_requests_enabled': getattr(project, 'merge_requests_enabled', False),
                'star_count': getattr(project, 'star_count', 0),
                'forks_count': getattr(project, 'forks_count', 0),
            }
            projects_data.append(project_info)
            
        except Exception as e:
            print(f"⚠️ Erreur projet ID {project_id}: {e}")
            
    print(f"✅ {len(projects_data)} projets extraits")
    return pd.DataFrame(projects_data)
