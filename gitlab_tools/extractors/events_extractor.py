"""
Extracteur d'événements GitLab
Module pour extraire les événements GitLab selon les spécifications
"""
from datetime import datetime, timedelta
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


def _build_event_info(event, project_name: str = "N/A") -> Dict[str, Any]:
    """
    Construit les informations d'un événement

    Args:
        event: Événement GitLab
        project_name: Nom du projet

    Returns:
        Dictionnaire avec les informations de l'événement
    """
    try:
        push_data = getattr(event, 'push_data', {}) or {}
        
        # Debug: afficher le type et les attributs de l'événement
        # print(f"🐛 Event type: {type(event)}, id: {getattr(event, 'id', 'NONE')}")

        return {
            'id_evenement': getattr(event, 'id', 0),
            'id_projet': getattr(event, 'project_id', 0),
            'nom_action': getattr(event, 'action_name', 'N/A'),
            'type_cible': getattr(event, 'target_type', 'N/A'),
            'id_auteur': getattr(event, 'author_id', 0),
            'date_creation': _format_date(getattr(event, 'created_at', 'N/A')),
            'action_push': push_data.get('action', 'N/A'),
            'nom_branche': push_data.get('ref', 'N/A')
        }
    except Exception as e:
        print(f"⚠️ Erreur dans _build_event_info: {e}")
        return {
            'id_event': 0,
            'project_id': 0,
            'action_name': 'ERROR',
            'target_type': 'ERROR',
            'author_id': 0,
            'created_at': 'ERROR',
            'push_action': 'ERROR',
            'branch_name': 'ERROR'
        }


def _process_project_events(project, include_archived: bool, gl_client, cutoff_date=None) -> tuple[list, int]:
    """
    Traite les événements d'un projet avec filtrage par date

    Args:
        project: Projet GitLab
        include_archived: Inclure les projets archivés
        gl_client: Client GitLab
        cutoff_date: Date limite pour filtrer les événements

    Returns:
        Tuple (liste des événements convertis, nombre d'événements traités)
    """
    # Filtrer les projets archivés si nécessaire
    if _should_skip_project(project, include_archived, gl_client):
        return [], 0

    # Récupérer les événements du projet
    events = _get_project_events(project)
    if not events:
        return [], 0

    project_name = getattr(project, 'name', 'N/A')
    
    # Filtrer par date AVANT la conversion
    filtered_events = []
    for event in events:
        try:
            if cutoff_date is None:
                # Pas de filtrage de date
                filtered_events.append(event)
            else:
                # Filtrer par date de création
                event_created_at = getattr(event, 'created_at', None)
                if event_created_at:
                    # Convertir la date ISO de GitLab au format datetime
                    event_date = datetime.fromisoformat(event_created_at.replace('Z', '+00:00')).replace(tzinfo=None)
                    if event_date >= cutoff_date:
                        filtered_events.append(event)
        except Exception as e:
            # En cas d'erreur de parsing de date, garder l'événement si pas de filtrage
            if cutoff_date is None:
                filtered_events.append(event)
    
    print(f"📊 Projet '{project_name}': {len(events)} événements ({len(filtered_events)} après filtrage)")
    
    # Convertir les événements filtrés en dictionnaires
    events_data = []
    for event in filtered_events:
        try:
            event_info = _build_event_info(event, project_name)
            events_data.append(event_info)
        except Exception as event_error:
            print(f"⚠️ Erreur événement ID {getattr(event, 'id', 'N/A')}: {event_error}")
            continue

    return events_data, len(events_data)


def extract_events(
    gl_client: python_gitlab.Gitlab, 
    include_archived: bool = False,
    days_back: int | None = 30
) -> pd.DataFrame:
    """
    Extrait tous les événements GitLab accessibles

    Args:
        gl_client: Client GitLab connecté
        include_archived: Inclure les projets archivés
        days_back: Nombre de jours en arrière pour filtrer les événements (défaut: 30, None = toutes les dates)

    Returns:
        DataFrame avec les événements GitLab
    """
    try:
        print("📊 === EXTRACTION DES ÉVÉNEMENTS GITLAB ===")
        print(f"� Extraction des événements des {days_back} derniers jours")
        print("�📋 Récupération de la liste des projets...")

        # Calculer la date de début (X jours en arrière ou toutes les dates)
        if days_back is not None:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            print(f"📅 Date limite: {cutoff_date.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            cutoff_date = None
            print("📅 Extraction de toutes les dates")

        # Récupérer tous les projets actifs seulement
        all_projects = gl_client.projects.list(all=True, simple=True, archived=include_archived)
        total_projects = len(all_projects)

        print(f"📋 {total_projects} projets {'actifs' if not include_archived else 'actifs + archivés'} trouvés")

        events_data = []
        processed_projects = 0
        filtered_events = 0

        for project in all_projects:
            try:
                # Traitement du projet avec filtrage intégré
                project_events, event_count = _process_project_events(project, include_archived, gl_client, cutoff_date)
                
                # Ajouter directement les événements convertis
                events_data.extend(project_events)
                filtered_events += event_count

                processed_projects += 1

                if processed_projects % 10 == 0:
                    print(f"📈 Progression: {processed_projects}/{total_projects} projets traités")

            except Exception as project_error:
                print(f"⚠️ Erreur projet ID {getattr(project, 'id', 'N/A')}: {project_error}")
                continue

        print(f"✅ {filtered_events} événements extraits sur {processed_projects} projets")

        # Créer le DataFrame
        if events_data:
            df = pd.DataFrame(events_data)

            # Trier par date de création (plus récents en premier)
            if 'date_creation' in df.columns:
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
