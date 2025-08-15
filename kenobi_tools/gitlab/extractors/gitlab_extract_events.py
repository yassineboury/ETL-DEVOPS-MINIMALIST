"""
Extracteur d'événements GitLab - VERSION ULTRA-SIMPLIFIÉE POWER BI
Extraction pure sans complexité - Power BI s'en charge !
Complexité cognitive visée: ≤ 8
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from ...utils.date_utils import DateFormatter


def extract_events_by_project(
    gl_client,
    project_ids: list,
    days_back: int = 30
) -> pd.DataFrame:
    """
    Extrait les événements GitLab - VERSION ULTRA-SIMPLE
    
    Args:
        gl_client: Client GitLab authentifié
        project_ids: Liste des IDs de projets
        days_back: Nombre de jours en arrière
        
    Returns:
        DataFrame avec les événements pour Power BI
    """
    print(f"📊 Extraction événements ({days_back} derniers jours)...")
    
    try:
        after_date = datetime.now() - timedelta(days=days_back)
        all_events = _extract_events_from_projects(gl_client, project_ids[:10], after_date)
        
        df = pd.DataFrame(all_events)
        
        if not df.empty:
            df = DateFormatter.format_date_columns(df)
            print(f"✅ {len(df)} événements extraits")
        else:
            print("⚠️ Aucun événement trouvé")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction événements: {e}")
        return pd.DataFrame()


def _extract_events_from_projects(gl_client, project_ids: list, after_date: datetime) -> list:
    """Extrait les événements de plusieurs projets"""
    all_events = []
    
    for project_id in project_ids:
        events = _extract_events_from_single_project(gl_client, project_id, after_date)
        all_events.extend(events)
    
    return all_events


def _extract_events_from_single_project(gl_client, project_id: int, after_date: datetime) -> list:
    """Extrait les événements d'un seul projet"""
    try:
        project = gl_client.projects.get(project_id)
        events = project.events.list(all=True, after=after_date.isoformat())
        
        return [_format_event_data(event, project) for event in events]
        
    except Exception as e:
        print(f"⚠️ Erreur projet {project_id}: {e}")
        return []


def _format_event_data(event, project) -> dict:
    """Formate les données d'un événement"""
    author_name = ''
    author_email = ''
    
    if hasattr(event, 'author') and event.author:
        author_name = event.author.get('name', '')
        author_email = event.author.get('email', '')
    
    return {
        'id Événement': event.id,
        'Type Action': event.action_name,
        'Type Cible': getattr(event, 'target_type', ''),
        'Titre Cible': getattr(event, 'target_title', ''),
        'Auteur': author_name,
        'Email Auteur': author_email,
        'Nom Projet': project.name,
        'ID Projet': project.id,
        'Date Création': event.created_at
    }


# Fonction de compatibilité pour l'ancien code
def extract_events_for_projects(gl_client, projects_list):
    """Fonction de compatibilité - redirige vers la version simple"""
    project_ids = [p['id'] if isinstance(p, dict) else p.id for p in projects_list]
    return extract_events_by_project(gl_client, project_ids)
