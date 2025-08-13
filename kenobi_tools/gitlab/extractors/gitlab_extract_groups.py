"""
Extracteur de groupes GitLab - Kenobi Tools
Module pour extraire les informations des groupes GitLab selon les spécifications DevSecOps
Optimisé pour export Excel avec métriques de gouvernance et sécurité
"""
from datetime import datetime
from typing import Optional
import pandas as pd
import gitlab as python_gitlab


def extract_groups(gl_client: python_gitlab.Gitlab, include_statistics: bool = True) -> pd.DataFrame:
    """
    Extrait les groupes GitLab avec leurs informations principales
    
    Args:
        gl_client: Instance du client GitLab
        include_statistics: Inclure les statistiques des groupes
        
    Returns:
        DataFrame avec les informations des groupes
    """
    try:
        print("🔍 Extraction des groupes GitLab...")
        
        # Récupération de tous les groupes accessibles
        groups = gl_client.groups.list(all=True, statistics=include_statistics)
        groups_data = []
        
        for group in groups:
            group_info = {
                'id': group.id,
                'name': group.name,
                'path': group.path,
                'full_name': getattr(group, 'full_name', ''),
                'full_path': getattr(group, 'full_path', ''),
                'description': getattr(group, 'description', ''),
                'visibility': getattr(group, 'visibility', ''),
                'created_at': _format_date(getattr(group, 'created_at', None)),
                'web_url': getattr(group, 'web_url', ''),
                'parent_id': getattr(group, 'parent_id', None),
            }
            
            if include_statistics and hasattr(group, 'statistics'):
                stats = group.statistics
                group_info.update({
                    'projects_count': stats.get('projects_count', 0),
                    'members_count': stats.get('members_count', 0),
                    'subgroups_count': stats.get('subgroups_count', 0),
                })
            
            groups_data.append(group_info)
        
        df = pd.DataFrame(groups_data)
        print(f"✅ {len(df)} groupes extraits")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des groupes : {e}")
        raise


def _format_date(date_string: Optional[str]) -> str:
    """Formate une date ISO vers le format DD/MM/YYYY HH:MM:SS"""
    if not date_string:
        return "N/A"
    
    try:
        # Parse ISO format
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, AttributeError):
        return date_string or "N/A"
