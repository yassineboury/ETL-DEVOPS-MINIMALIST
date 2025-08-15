"""
Fonctions communes pour l'extraction des projets GitLab
Module partagé pour éviter la duplication de code entre extracteurs
"""
from datetime import datetime
from typing import Any, Dict, Optional

import gitlab as python_gitlab
import pandas as pd


def format_date(date_string: Optional[str]) -> str:
    """
    Formate une date ISO vers le format DD/MM/YYYY HH:MM:SS

    Args:
        date_string: Date au format ISO

    Returns:
        Date formatée ou "N/A" si None
    """
    if not date_string:
        return "N/A"

    try:
        # Parser la date ISO (gérer différents formats)
        if 'T' in date_string:
            # Format ISO complet
            date_part = date_string.split('T')[0]
            time_part = date_string.split('T')[1].split('.')[0].split('+')[0].split('Z')[0]
        else:
            # Format date simple
            date_part = date_string.split(' ')[0] if ' ' in date_string else date_string
            time_part = date_string.split(' ')[1] if ' ' in date_string else "00:00:00"

        # Parser la date
        dt = datetime.strptime(f"{date_part} {time_part[:8]}", "%Y-%m-%d %H:%M:%S")

        # Formater vers DD/MM/YYYY HH:MM:SS
        return dt.strftime("%d/%m/%Y %H:%M:%S")

    except Exception:
        # En cas d'erreur, retourner la chaîne originale ou N/A
        return date_string if date_string else "N/A"


def translate_namespace_kind(kind: str) -> str:
    """
    Traduit le type de namespace en français

    Args:
        kind: Type de namespace ('user', 'group', etc.)

    Returns:
        Traduction française
    """
    translations = {
        'user': 'Utilisateur',
        'group': 'Groupe',
        'project': 'Projet'
    }
    return translations.get(kind, kind.capitalize())


def determine_project_state(project) -> str:
    """
    Détermine l'état d'un projet GitLab

    Args:
        project: Objet projet GitLab

    Returns:
        État du projet: "Actif", "Archivé", "Supprimé"
    """
    if getattr(project, 'archived', False):
        return "Archivé"
    elif getattr(project, 'marked_for_deletion_at', None):
        return "Supprimé"
    else:
        return "Actif"


def get_last_commit_date(project) -> str:
    """
    Récupère la date du dernier commit d'un projet

    Args:
        project: Objet projet GitLab

    Returns:
        Date formatée du dernier commit ou "N/A"
    """
    try:
        commits = project.commits.list(per_page=1, page=1)
        if commits:
            return format_date(commits[0].committed_date)
    except Exception:
        pass
    return "N/A"


def get_dominant_language(project) -> str:
    """
    Détermine le langage de programmation dominant d'un projet

    Args:
        project: Objet projet GitLab

    Returns:
        Nom du langage dominant ou "N/A"
    """
    try:
        languages = project.languages()
        
        if languages:
            # Trouver le langage avec le plus haut pourcentage
            dominant_language = max(languages.items(), key=lambda x: x[1])
            return dominant_language[0]
            
    except Exception:
        # En cas d'erreur d'API ou d'accès, ignorer silencieusement
        pass
        
    return "N/A"


def is_empty_project(project) -> str:
    """
    Détermine si un projet est vide (pas de commits)

    Args:
        project: Objet projet GitLab

    Returns:
        "Oui" si vide, "Non" sinon
    """
    try:
        # Vérifier s'il y a des commits
        commits = project.commits.list(per_page=1, page=1)
        return "Non" if commits else "Oui"
    except Exception:
        # En cas d'erreur, considérer comme non vide par prudence
        return "Non"


def create_project_data_dict(project) -> Dict[str, Any]:
    """
    Crée un dictionnaire avec toutes les données d'un projet
    
    Args:
        project: Objet projet GitLab
        
    Returns:
        Dictionnaire avec les données du projet formatées
    """
    # Récupération des données de base
    namespace = getattr(project, 'namespace', {})
    namespace_name = namespace.get('name', 'N/A') if isinstance(namespace, dict) else str(namespace)
    namespace_kind = namespace.get('kind', 'N/A') if isinstance(namespace, dict) else 'N/A'
    
    # Déterminer l'activité récente
    last_activity = getattr(project, 'last_activity_at', None)
    last_commit_date = get_last_commit_date(project)
    
    return {
        'id': project.id,
        'nom': project.name,
        'nom_complet': getattr(project, 'path_with_namespace', 'N/A'),
        'description': getattr(project, 'description', '') or '',
        'visibilite': getattr(project, 'visibility', 'N/A'),
        'namespace': namespace_name,
        'type_namespace': translate_namespace_kind(namespace_kind),
        'url': getattr(project, 'web_url', 'N/A'),
        'ssh_url': getattr(project, 'ssh_url_to_repo', 'N/A'),
        'http_url': getattr(project, 'http_url_to_repo', 'N/A'),
        'etoiles': getattr(project, 'star_count', 0),
        'forks': getattr(project, 'forks_count', 0),
        'issues_ouvertes': getattr(project, 'open_issues_count', 0),
        'date_creation': format_date(getattr(project, 'created_at', None)),
        'derniere_activite': format_date(last_activity),
        'dernier_commit': last_commit_date,
        'langage_principal': get_dominant_language(project),
        'etat': determine_project_state(project),
        'vide': is_empty_project(project),
    }


def extract_all_projects(gl_client: python_gitlab.Gitlab, include_archived: bool = False) -> pd.DataFrame:
    """
    Fonction de base pour extraire tous les projets GitLab
    
    Args:
        gl_client: Instance du client GitLab
        include_archived: Inclure les projets archivés
        
    Returns:
        DataFrame avec les informations des projets
    """
    try:
        print(f"🔍 Extraction des projets GitLab (archivés: {'Oui' if include_archived else 'Non'})...")
        
        # Récupérer tous les projets avec la configuration appropriée
        projects = gl_client.projects.list(
            all=True,
            archived=include_archived,
            simple=False,
            statistics=True,
            with_custom_attributes=True
        )
        
        projects_data = []
        
        for project in projects:
            try:
                project_data = create_project_data_dict(project)
                projects_data.append(project_data)
                
            except Exception as e:
                print(f"⚠️ Erreur lors du traitement du projet {getattr(project, 'name', 'unknown')}: {e}")
                continue
        
        df = pd.DataFrame(projects_data)
        print(f"✅ {len(df)} projets extraits")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des projets : {e}")
        return pd.DataFrame()
