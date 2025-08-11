"""
Extraction des utilisateurs GitLab
"""
import gitlab
import pandas as pd
from typing import List, Dict, Any


def extract_users(gl_client) -> pd.DataFrame:
    """
    Extrait la liste des utilisateurs GitLab
    
    Args:
        gl_client: Client GitLab authentifié
        
    Returns:
        DataFrame avec les informations des utilisateurs
    """
    print("🔍 Extraction des utilisateurs GitLab...")
    
    users_data = []
    
    try:
        # Récupérer tous les utilisateurs actifs
        users = gl_client.users.list(all=True, active=True)
        
        for user in users:
            user_info = {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': getattr(user, 'email', ''),
                'state': user.state,
                'created_at': user.created_at,
                'last_activity_on': getattr(user, 'last_activity_on', ''),
                'web_url': user.web_url,
                'is_admin': getattr(user, 'is_admin', False),
                'can_create_group': getattr(user, 'can_create_group', False),
                'can_create_project': getattr(user, 'can_create_project', False),
                'projects_limit': getattr(user, 'projects_limit', 0),
            }
            users_data.append(user_info)
            
        print(f"✅ {len(users_data)} utilisateurs extraits")
        return pd.DataFrame(users_data)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des utilisateurs: {e}")
        return pd.DataFrame()


def extract_project_members(gl_client, project_id: int) -> pd.DataFrame:
    """
    Extrait les membres d'un projet spécifique
    
    Args:
        gl_client: Client GitLab authentifié
        project_id: ID du projet
        
    Returns:
        DataFrame avec les membres du projet
    """
    print(f"🔍 Extraction des membres du projet {project_id}...")
    
    members_data = []
    
    try:
        project = gl_client.projects.get(project_id)
        members = project.members.list(all=True)
        
        for member in members:
            member_info = {
                'project_id': project_id,
                'user_id': member.id,
                'username': member.username,
                'name': member.name,
                'email': getattr(member, 'email', ''),
                'access_level': member.access_level,
                'access_level_name': member.get_access_level_string(),
                'created_at': getattr(member, 'created_at', ''),
                'expires_at': getattr(member, 'expires_at', ''),
            }
            members_data.append(member_info)
            
        print(f"✅ {len(members_data)} membres extraits")
        return pd.DataFrame(members_data)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des membres du projet {project_id}: {e}")
        return pd.DataFrame()
