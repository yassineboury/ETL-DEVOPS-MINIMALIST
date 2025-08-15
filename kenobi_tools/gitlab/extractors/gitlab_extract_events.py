"""
Extracteur d'événements GitLab - VERSION REFACTORISÉE
Module pour extraire les événements GitLab avec complexité cognitive réduite
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from kenobi_tools.utils.date_utils import format_gitlab_date


class EventExtractor:
    """Extracteur d'événements GitLab simplifié"""
    
    @staticmethod
    def extract_events_by_project(
        gl_client,
        projects: List[Dict[str, Any]],
        after_date: Optional[str] = None,
        before_date: Optional[str] = None,
        max_projects: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Extrait les événements pour une liste de projets
        
        Args:
            gl_client: Client GitLab authentifié
            projects: Liste des projets à traiter
            after_date: Date de début (ISO format)
            before_date: Date de fin (ISO format)
            max_projects: Limite du nombre de projets à traiter
            
        Returns:
            DataFrame avec tous les événements
        """
        print("🔍 Extraction des événements GitLab...")
        
        if not projects:
            print("⚠️ Aucun projet fourni pour l'extraction d'événements")
            return pd.DataFrame()
        
        # Limiter le nombre de projets si spécifié
        projects_to_process = projects[:max_projects] if max_projects else projects
        print(f"📊 Traitement de {len(projects_to_process)} projet(s)")
        
        all_events = []
        
        for i, project in enumerate(projects_to_process, 1):
            project_id = project.get('id')
            if not project_id:
                continue
                
            project_name = project.get('name', 'N/A')
            
            print(f"  📂 [{i}/{len(projects_to_process)}] {project_name}")
            
            try:
                project_events = EventExtractor._extract_project_events(
                    gl_client, int(project_id), project_name, after_date, before_date
                )
                all_events.extend(project_events)
                
            except Exception as e:
                print(f"    ❌ Erreur projet {project_name}: {e}")
                continue
        
        if not all_events:
            print("⚠️ Aucun événement trouvé")
            return pd.DataFrame()
        
        # Créer le DataFrame final
        df = pd.DataFrame(all_events)
        df = EventExtractor._process_dataframe(df)
        
        print(f"✅ {len(df)} événements extraits au total")
        return df
    
    @staticmethod
    def _extract_project_events(
        gl_client, 
        project_id: int, 
        project_name: str,
        after_date: Optional[str],
        before_date: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extrait les événements d'un projet spécifique"""
        try:
            project = gl_client.projects.get(project_id, lazy=True)
            
            # Paramètres de requête
            params = {'all': True, 'sort': 'desc'}
            if after_date:
                params['after'] = after_date
            if before_date:
                params['before'] = before_date
            
            # Récupérer les événements
            events = project.events.list(**params)
            
            if not events:
                return []
            
            # Convertir en dictionnaires
            project_events = []
            for event in events:
                event_data = EventExtractor._process_single_event(event, project_name)
                if event_data:
                    project_events.append(event_data)
            
            return project_events
            
        except Exception as e:
            print(f"    ⚠️ Erreur extraction projet {project_id}: {e}")
            return []
    
    @staticmethod
    def _process_single_event(event, project_name: str) -> Optional[Dict[str, Any]]:
        """Traite un événement individuel"""
        try:
            return {
                'project_id': getattr(event, 'project_id', 0),
                'project_name': project_name,
                'event_id': getattr(event, 'id', 0),
                'author_name': getattr(event, 'author_name', 'N/A'),
                'author_username': getattr(event, 'author_username', 'N/A'),
                'created_at': format_gitlab_date(getattr(event, 'created_at', None)),
                'action_name': getattr(event, 'action_name', 'N/A'),
                'target_type': getattr(event, 'target_type', 'N/A'),
                'target_title': getattr(event, 'target_title', 'N/A'),
                'push_data_commit_count': getattr(event, 'push_data', {}).get('commit_count', 0) if hasattr(event, 'push_data') and event.push_data else 0,
                'note': getattr(event, 'note', {}).get('body', '')[:100] if hasattr(event, 'note') and event.note else ''
            }
        except Exception as e:
            print(f"    ⚠️ Erreur traitement événement: {e}")
            return None
    
    @staticmethod
    def _process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Traitement final du DataFrame"""
        if df.empty:
            return df
        
        # Trier par ID décroissant (plus récents en premier)
        if 'event_id' in df.columns:
            df = df.sort_values('event_id', ascending=False).reset_index(drop=True)
        
        return df


# Fonction de compatibilité avec l'ancienne API
def extract_events_by_project(
    gl_client,
    projects: List[Dict[str, Any]],
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    max_projects: Optional[int] = None
) -> pd.DataFrame:
    """
    Fonction de compatibilité pour l'extraction d'événements
    """
    return EventExtractor.extract_events_by_project(
        gl_client, projects, after_date, before_date, max_projects
    )


def main():
    """Fonction principale - DÉSACTIVÉE TEMPORAIREMENT"""
    print("⚠️ Cette fonction de test est désactivée après refactorisation")
    print("💡 Utilisez maestro_kenobi.py pour les extractions")


if __name__ == "__main__":
    main()
