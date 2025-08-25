"""
Extracteur d'événements GitLab - Version optimisée
Conformité SonarCloud : Complexité cognitive < 15 par fonction

Objectif: Extraire les événements GitLab pour analyse Power BI
Colonnes: 8 champs essentiels pour le suivi d'activité
"""

import pandas as pd
from typing import Optional
from kenobi_tools.utils.date_utils import format_date_columns


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
        
        # Récupérer tous les projets accessibles
        projects = gl.projects.list(all=True)
        print(f"🔍 Analyse de {len(projects)} projets...")
        
        all_events = []
        projects_cache = {}  # Cache pour éviter les appels API répétés
        
        # Extraire événements projet par projet
        for project in projects:
            try:
                # Récupérer événements du projet (limite raisonnable par projet)
                project_events = project.events.list(per_page=min(limit//10, 20), get_all=False)
                
                if project_events:
                    # Cache du nom de projet
                    projects_cache[project.id] = project.name
                    
                    for event in project_events:
                        all_events.append(event)
                        
            except Exception as e:
                # Ignorer les erreurs de projets individuels (permissions, etc.)
                continue
        
        print(f"🔄 Traitement de {len(all_events)} événements collectés...")
        
        if not all_events:
            print("⚠️ Aucun événement trouvé")
            return pd.DataFrame()
        
        # Limiter le nombre total d'événements si nécessaire
        if len(all_events) > limit:
            # Trier par date (plus récents d'abord) et limiter
            all_events.sort(key=lambda x: getattr(x, 'created_at', ''), reverse=True)
            all_events = all_events[:limit]
            print(f"📊 Limité aux {limit} événements les plus récents")
        
        data = []
        
        for event in all_events:
            # Récupérer le nom du projet avec cache
            project_name = _get_project_name_cached(
                gl, event.project_id, projects_cache
            )
            
            # Extraire informations de branche depuis push_data
            branche = _extract_branch_info(event)
            
            # Extraire les données de l'événement
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
        
        # Créer DataFrame
        df = pd.DataFrame(data)
        
        # Formater les dates en français
        df = format_date_columns(df)
        
        # Statistiques des auteurs
        authors = df['utilisateur'].unique()
        print(f"✅ {len(df)} événements extraits de {len(authors)} utilisateurs différents")
        print(f"👥 Auteurs: {list(authors)[:10]}{'...' if len(authors) > 10 else ''}")
        
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
    except Exception:
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
        
    except Exception:
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
        # Vérifier si l'événement a des données de push
        if hasattr(event, 'push_data') and event.push_data:
            push_data = event.push_data
            
            # Extraire le nom de la branche depuis le ref
            if hasattr(push_data, 'ref') and push_data.ref:
                ref = push_data.ref
                # Le ref est généralement au format 'refs/heads/branch-name'
                if ref.startswith('refs/heads/'):
                    return ref.replace('refs/heads/', '')
                # Parfois c'est juste le nom de la branche
                return ref
        
        # Pour les autres types d'événements, essayer de récupérer depuis target
        if hasattr(event, 'target_type') and event.target_type == 'MergeRequest':
            # Pour les MR, on pourrait extraire plus d'infos, mais c'est complexe
            return None
        
        return None
        
    except Exception:
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
            # url_cible = _build_target_url(gl.url, project_id, event)
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
            print(f"\n📊 Aperçu des données extraites:")
            print(f"   Colonnes: {list(df_events.columns)}")
            print(f"   Types d'actions: {df_events['type_action'].unique()}")
            print(f"   Nombre d'événements: {len(df_events)}")
            
            # Afficher les premières lignes
            print(f"\n📋 Premiers événements:")
            for idx, row in df_events.head(3).iterrows():
                print(f"   {row['utilisateur']} - {row['type_action']} - {row['nom_projet']}")
        else:
            print("❌ Aucune donnée extraite")
            
    except Exception as e:
        print(f"❌ Test échoué: {e}")
