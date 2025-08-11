"""
Extracteur d'événements GitLab
Module pour extraire les événements GitLab selon les spécifications
"""
from datetime import datetime
from typing import Any, Dict, Optional

import gitlab as python_gitlab
import pandas as pd


def _format_date(date_string: Optional[str]) -> str:
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


def _translate_action_name(action: str) -> str:
    """
    Traduit les noms d'action GitLab en français

    Args:
        action: Nom d'action GitLab

    Returns:
        Action traduite en français
    """
    if not action:
        return "N/A"

    translations = {
        'opened': 'ouvert',
        'closed': 'fermé',
        'reopened': 'rouvert',
        'pushed': 'poussé',
        'commented on': 'commenté',
        'merged': 'fusionné',
        'created': 'créé',
        'updated': 'mis à jour',
        'deleted': 'supprimé',
        'joined': 'rejoint',
        'left': 'quitté'
    }
    return translations.get(action, action)


def _translate_target_type(target_type: Optional[str]) -> str:
    """
    Traduit les types de cible GitLab en français

    Args:
        target_type: Type de cible GitLab

    Returns:
        Type traduit en français
    """
    if not target_type:
        return 'N/A'

    translations = {
        'Issue': 'Ticket',
        'MergeRequest': 'Demande de fusion',
        'Note': 'Commentaire',
        'Project': 'Projet',
        'Milestone': 'Jalon',
        'Epic': 'Épique',
        'Snippet': 'Extrait de code',
        'User': 'Utilisateur'
    }
    return translations.get(target_type, target_type)


def _should_skip_project(project, include_archived: bool, gl_client) -> bool:
    """
    Détermine si un projet doit être ignoré

    Args:
        project: Projet GitLab
        include_archived: Inclure les projets archivés
        gl_client: Client GitLab

    Returns:
        True si le projet doit être ignoré
    """
    if include_archived:
        return False

    try:
        full_project = gl_client.projects.get(project.id)
        return getattr(full_project, 'archived', False)
    except Exception:
        return True


def _get_project_events(project):
    """
    Récupère les événements d'un projet

    Args:
        project: Projet GitLab

    Returns:
        Liste des événements ou None en cas d'erreur
    """
    try:
        events = project.events.list(all=True, per_page=100)
        return events if events else None
    except Exception:
        return None


def _build_event_info(event) -> Dict[str, Any]:
    """
    Construit les informations d'un événement

    Args:
        event: Événement GitLab

    Returns:
        Dictionnaire avec les informations de l'événement
    """
    push_data = getattr(event, 'push_data', {}) or {}

    return {
        'id_evenement': getattr(event, 'id', 0),
        'nom_action': _translate_action_name(getattr(event, 'action_name', 'N/A')),
        'type_cible': _translate_target_type(getattr(event, 'target_type', None)),
        'date_creation': _format_date(getattr(event, 'created_at', None)),
        'id_projet': getattr(event, 'project_id', 0),
        'id_auteur': getattr(event, 'author_id', 0),
        'id_cible': getattr(event, 'target_id', None),
        'iid_cible': getattr(event, 'target_iid', None),
        'titre_cible': getattr(event, 'target_title', 'N/A'),
        'nb_commits': push_data.get('commit_count', None),
        'branche_ref': push_data.get('ref', 'N/A'),
        'type_ref': push_data.get('ref_type', 'N/A')
    }


def _process_project_events(project, include_archived: bool, gl_client) -> tuple[list, int]:
    """
    Traite les événements d'un projet

    Args:
        project: Projet GitLab
        include_archived: Inclure les projets archivés
        gl_client: Client GitLab

    Returns:
        Tuple (liste des événements, nombre d'événements traités)
    """
    # Filtrer les projets archivés si nécessaire
    if _should_skip_project(project, include_archived, gl_client):
        return [], 0

    # Récupérer les événements du projet
    events = _get_project_events(project)
    if not events:
        return [], 0

    events_data = []
    project_name = getattr(project, 'name', 'N/A')
    print(f"📊 Projet '{project_name}': {len(events)} événements")

    for event in events:
        try:
            event_info = _build_event_info(event)
            events_data.append(event_info)
        except Exception as event_error:
            print(f"⚠️ Erreur événement ID {getattr(event, 'id', 'N/A')}: {event_error}")
            continue

    return events_data, len(events_data)


def extract_events(gl_client: python_gitlab.Gitlab, include_archived: bool = False) -> pd.DataFrame:
    """
    Extrait tous les événements GitLab accessibles

    Args:
        gl_client: Client GitLab connecté
        include_archived: Inclure les projets archivés

    Returns:
        DataFrame avec les événements GitLab
    """
    try:
        print("📊 === EXTRACTION DES ÉVÉNEMENTS GITLAB ===")
        print("📋 Récupération de la liste des projets...")

        # Récupérer tous les projets
        all_projects = gl_client.projects.list(all=True, simple=True)
        total_projects = len(all_projects)

        print(f"📋 {total_projects} projets trouvés")

        events_data = []
        processed_projects = 0
        filtered_events = 0

        for project in all_projects:
            try:
                project_events, event_count = _process_project_events(project, include_archived, gl_client)
                events_data.extend(project_events)
                filtered_events += event_count

                processed_projects += 1

                if processed_projects % 10 == 0:
                    print(f"📈 Progression: {processed_projects}/{total_projects} projets traités")

                # Limiter à 50 projets pour éviter les timeouts
                if processed_projects >= 50:
                    print("⚠️ Limitation à 50 projets appliquée")
                    break

            except Exception as project_error:
                print(f"⚠️ Erreur projet ID {getattr(project, 'id', 'N/A')}: {project_error}")
                continue

        print(f"✅ {filtered_events} événements extraits sur {processed_projects} projets")

        # Créer le DataFrame
        if events_data:
            df = pd.DataFrame(events_data)

            # Trier par date de création (plus récents en premier)
            df = df.sort_values('date_creation', ascending=False)
            df = df.reset_index(drop=True)

            return df
        else:
            return pd.DataFrame()

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des événements: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    """Test de l'extracteur d'événements"""
    print("🧪 Test de l'extracteur d'événements GitLab")
    print("=" * 50)

    # Cette partie serait utilisée pour des tests
    # avec un vrai client GitLab
