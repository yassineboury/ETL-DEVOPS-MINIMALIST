"""
Extracteur d'événements GitLab - Version optimisée
Conformité SonarCloud : Complexité cognitive < 15 par fonction

Objectif: Extraire les événements GitLab pour analyse Power BI
Colonnes: 8 champs essentiels pour le suivi d'activité
"""

import pandas as pd
from typing import Optional, List, Dict, Any
from kenobi_tools.utils.date_utils import format_date_columns
from datetime import datetime

# Constantes pour éviter les duplications
REF_HEADS_PREFIX = 'refs/heads/'


def _collect_project_events(projects: List[Any], limit: int, after_datetime: Optional[datetime] = None) -> tuple[List[Any], Dict[int, str]]:
    """
    Collecte les événements de tous les projets avec cache
    
    Args:
        projects: Liste des projets 
        limit: Limite d'événements par projet
        after_datetime: Filtre de date optionnel
        
    Returns:
        Tuple (liste événements, cache projets)
    """
    all_events = []
    projects_cache = {}
    
    for project in projects:
        project_events = _get_project_events_safe(project, limit)
        if not project_events:
            continue
            
        projects_cache[project.id] = project.name
        
        for event in project_events:
            if _should_include_event(event, after_datetime):
                all_events.append(event)
    
    return all_events, projects_cache


def _get_project_events_safe(project, limit: int) -> List[Any]:
    """Récupère les événements d'un projet avec gestion d'erreur"""
    try:
        return project.events.list(per_page=min(limit//10, 20), get_all=False)
    except (AttributeError, ValueError):
        return []


def _should_include_event(event, after_datetime: Optional[datetime]) -> bool:
    """Détermine si un événement doit être inclus selon le filtre de date"""
    if not after_datetime:
        return True
        
    try:
        event_date = datetime.fromisoformat(event.created_at.replace('Z', '+00:00'))
        return event_date >= after_datetime
    except (ValueError, AttributeError):
        return True  # Inclure en cas d'erreur de parsing


def _process_events_to_dataframe(all_events: List[Any], projects_cache: Dict[int, str], gl, limit: int) -> pd.DataFrame:
    """
    Transforme les événements en DataFrame avec formatage
    
    Args:
        all_events: Liste des événements
        projects_cache: Cache des noms de projets
        gl: Client GitLab
        limit: Limite totale d'événements
        
    Returns:
        DataFrame formaté
    """
    if not all_events:
        return pd.DataFrame()
    
    # Limiter et trier si nécessaire
    if len(all_events) > limit:
        all_events.sort(key=lambda x: getattr(x, 'created_at', ''), reverse=True)
        all_events = all_events[:limit]
        print(f"📊 Limité aux {limit} événements les plus récents")
    
    data = []
    for event in all_events:
        project_name = _get_project_name_cached(gl, event.project_id, projects_cache)
        branche = _extract_branch_info(event)
        
        event_data = {
            'id_evenement': event.id,
            'type_action': event.action_name,
            'id_projet': event.project_id,
            'nom_projet': project_name,
            'id_utilisateur': event.author_id,
            'utilisateur': event.author_username,
            'date_evenement': event.created_at,
            'branche': branche
        }
        data.append(event_data)
    
    df = pd.DataFrame(data)
    return format_date_columns(df)


def _print_extraction_stats(df: pd.DataFrame, after_date: Optional[str] = None) -> None:
    """Affiche les statistiques d'extraction"""
    authors = df['utilisateur'].unique()
    print(f"✅ {len(df)} événements extraits de {len(authors)} utilisateurs différents")
    
    if after_date and not df.empty:
        min_date = df['date_evenement'].min()
        max_date = df['date_evenement'].max()
        print(f"📅 Période effective: {min_date} → {max_date}")
    
    print(f"👥 Auteurs: {list(authors)[:10]}{'...' if len(authors) > 10 else ''}")


def extract_gitlab_events_with_period(gl, limit: int = 100, after_date: Optional[str] = None) -> pd.DataFrame:
    """
    Extrait les événements GitLab avec filtrage par période
    
    Args:
        gl: Client GitLab connecté
        limit: Nombre maximum d'événements par projet
        after_date: Date limite (format ISO), None pour tous
        
    Returns:
        DataFrame avec colonnes techniques (format underscore)
    """
    try:
        print("📥 Extraction des événements GitLab via projets...")
        
        after_datetime = None
        if after_date:
            after_datetime = datetime.fromisoformat(after_date.replace('Z', '+00:00'))
            print(f"🗓️ Événements après le: {after_datetime.strftime('%d/%m/%Y')}")
        
        # Récupérer tous les projets
        projects = gl.projects.list(all=True)
        print(f"🔍 Analyse de {len(projects)} projets...")
        
        # Collecter les événements
        all_events, projects_cache = _collect_project_events(projects, limit, after_datetime)
        print(f"🔄 Traitement de {len(all_events)} événements collectés...")
        
        if not all_events:
            print("⚠️ Aucun événement trouvé pour cette période")
            return pd.DataFrame()
        
        # Traiter en DataFrame
        df = _process_events_to_dataframe(all_events, projects_cache, gl, limit)
        
        # Afficher statistiques
        _print_extraction_stats(df, after_date)
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des événements: {e}")
        return pd.DataFrame()


def extract_gitlab_events(gl, limit: int = 100) -> pd.DataFrame:
    """
    Extrait les événements GitLab via les projets (plus d'événements d'autres users)
    
    Args:
        gl: Client GitLab connecté
        limit: Nombre maximum d'événements par projet
        
    Returns:
        DataFrame avec colonnes techniques (format underscore)
    """
    try:
        print("📥 Extraction des événements GitLab via projets...")
        
        # Récupérer tous les projets
        projects = gl.projects.list(all=True)
        print(f"🔍 Analyse de {len(projects)} projets...")
        
        # Collecter les événements (sans filtre de date)
        all_events, projects_cache = _collect_project_events(projects, limit)
        print(f"🔄 Traitement de {len(all_events)} événements collectés...")
        
        if not all_events:
            print("⚠️ Aucun événement trouvé")
            return pd.DataFrame()
        
        # Traiter en DataFrame
        df = _process_events_to_dataframe(all_events, projects_cache, gl, limit)
        
        # Afficher statistiques
        _print_extraction_stats(df)
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des événements: {e}")
        return pd.DataFrame()


def _get_project_name_cached(gl, project_id: int, cache: dict) -> str:
    """
    Récupère le nom d'un projet avec mise en cache
    
    Args:
        gl: Client GitLab
        project_id: ID du projet
        cache: Dictionnaire de cache
        
    Returns:
        Nom du projet ou "Projet Inconnu"
    """
    if project_id in cache:
        return cache[project_id]
    
    try:
        project = gl.projects.get(project_id)
        project_name = project.name
        cache[project_id] = project_name
        return project_name
    except (AttributeError, ValueError):
        cache[project_id] = f"Projet {project_id}"
        return cache[project_id]


def _build_target_url(gitlab_url: str, project_id: int, event) -> Optional[str]:
    """
    Construit l'URL cible de l'événement
    
    Args:
        gitlab_url: URL de base GitLab
        project_id: ID du projet
        event: Objet événement
        
    Returns:
        URL cible ou None
    """
    try:
        base_url = f"{gitlab_url.rstrip('/')}/{project_id}"
        
        # URL selon le type d'action
        if hasattr(event, 'target_type') and event.target_type:
            target_type = event.target_type
            target_id = getattr(event, 'target_id', None)
            
            if target_type == 'Issue' and target_id:
                return f"{base_url}/-/issues/{target_id}"
            elif target_type == 'MergeRequest' and target_id:
                return f"{base_url}/-/merge_requests/{target_id}"
            elif target_type == 'Milestone' and target_id:
                return f"{base_url}/-/milestones/{target_id}"
        
        # URL par défaut vers le projet
        return base_url
        
    except (AttributeError, ValueError):
        return None


def _extract_branch_info(event) -> Optional[str]:
    """
    Extrait l'information de branche d'un événement GitLab
    
    Args:
        event: Objet événement GitLab
        
    Returns:
        Nom de la branche ou None
    """
    try:
        # Méthode 1: Vérifier dans attributes.push_data (structure réelle GitLab)
        ref = _get_ref_from_attributes(event)
        if ref:
            return _clean_ref_name(ref)
        
        # Méthode 2: Vérifier si l'événement a un attribut push_data direct
        ref = _get_ref_from_push_data(event)
        if ref:
            return _clean_ref_name(ref)
        
        # Méthode 3: Chercher dans target_title pour les merge requests
        branch_name = _extract_branch_from_merge_request(event)
        if branch_name:
            return branch_name
        
        return None
        
    except (AttributeError, ValueError):
        return None


def _get_ref_from_attributes(event) -> Optional[str]:
    """Extrait ref depuis event.attributes.push_data"""
    if hasattr(event, 'attributes') and isinstance(event.attributes, dict):
        push_data = event.attributes.get('push_data')
        if push_data and isinstance(push_data, dict):
            return push_data.get('ref')
    return None


def _get_ref_from_push_data(event) -> Optional[str]:
    """Extrait ref depuis event.push_data"""
    if hasattr(event, 'push_data') and event.push_data:
        push_data = event.push_data
        
        # Si c'est un dict
        if isinstance(push_data, dict):
            return push_data.get('ref')
        
        # Si c'est un objet avec attributs
        elif hasattr(push_data, 'ref') and push_data.ref:
            return push_data.ref
    return None


def _clean_ref_name(ref: str) -> str:
    """Nettoie le nom de référence en supprimant le préfixe refs/heads/"""
    if ref.startswith(REF_HEADS_PREFIX):
        return ref.replace(REF_HEADS_PREFIX, '')
    return ref


def _extract_branch_from_merge_request(event) -> Optional[str]:
    """Extrait le nom de branche depuis le titre d'une merge request"""
    if hasattr(event, 'target_type') and event.target_type == 'MergeRequest':
        if hasattr(event, 'target_title') and event.target_title:
            # Les MR ont souvent le format "Merge branch 'feature' into 'main'"
            title = event.target_title
            if 'branch' in title.lower():
                # Extraire le nom de branche si possible
                import re
                match = re.search(r"'([^']+)'", title)
                if match:
                    return match.group(1)
    return None


def extract_project_events(gl, project_id: int, limit: int = 50) -> pd.DataFrame:
    """
    Extrait les événements d'un projet spécifique
    
    Args:
        gl: Client GitLab connecté
        project_id: ID du projet
        limit: Nombre maximum d'événements
        
    Returns:
        DataFrame avec événements du projet
    """
    try:
        print(f"📥 Extraction des événements du projet {project_id}...")
        
        project = gl.projects.get(project_id)
        events = project.events.list(per_page=limit, get_all=False)
        
        if not events:
            print("⚠️ Aucun événement trouvé pour ce projet")
            return pd.DataFrame()
        
        data = []
        
        for event in events:
            branche = _extract_branch_info(event)
            
            event_data = {
                'id_evenement': event.id,
                'type_action': event.action_name,
                'id_projet': project_id,
                'nom_projet': project.name,
                'id_utilisateur': event.author_id,
                'utilisateur': event.author_username,
                'date_evenement': event.created_at,
                'branche': branche
            }
            
            data.append(event_data)
        
        df = pd.DataFrame(data)
        df = format_date_columns(df)
        
        print(f"✅ {len(df)} événements extraits pour le projet")
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des événements du projet: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    # Test de l'extracteur
    from kenobi_tools.gitlab.client.gitlab_client import GitLabClient
    
    print("🧪 Test de l'extracteur d'événements")
    
    try:
        client = GitLabClient()
        gl = client.connect()
        
        # Test extraction événements système
        df_events = extract_gitlab_events(gl, limit=10)
        
        if not df_events.empty:
            print("\n📊 Aperçu des données extraites:")
            print(f"   Colonnes: {list(df_events.columns)}")
            print(f"   Types d'actions: {df_events['type_action'].unique()}")
            print(f"   Nombre d'événements: {len(df_events)}")
            
            # Afficher les premières lignes
            print("\n📋 Premiers événements:")
            for idx, row in df_events.head(3).iterrows():
                print(f"   {row['utilisateur']} - {row['type_action']} - {row['nom_projet']}")
        else:
            print("❌ Aucune donnée extraite")
            
    except Exception as e:
        print(f"❌ Test échoué: {e}")
