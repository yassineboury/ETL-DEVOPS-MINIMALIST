"""
Processeur d'extraction GitLab - VERSION POWER BI
Orchestration simple sans statistiques ni complexité
Complexité cognitive visée: ≤ 10
"""
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

from ..gitlab.client.gitlab_client import GitLabClient
from ..gitlab.extractors.gitlab_extract_users import extract_human_users
from ..gitlab.extractors.gitlab_extract_groups import extract_groups
from ..gitlab.extractors.gitlab_extract_active_projects import extract_active_projects
from ..gitlab.extractors.gitlab_extract_archived_projects import extract_archived_projects
from ..gitlab.exporters.gitlab_export_excel import GitLabExcelExporter


class ExtractionProcessor:
    """Processeur simple d'extraction GitLab"""

    def __init__(self):
        self.extracted_data = {}
        
    def process_all_data(self, exports_dir: Path) -> bool:
        """
        Traite toutes les données GitLab - VERSION CORRIGÉE
        
        Args:
            exports_dir: Répertoire d'export
            
        Returns:
            True si succès, False sinon
        """
        print("🚀 Début extraction GitLab complète")
        
        try:
            # Connexion GitLab
            client = GitLabClient()
            gl = client.connect()
            
            # Initialiser l'exporteur
            exporter = GitLabExcelExporter(exports_dir)
            
            # ÉTAPE 1: Nettoyage initial de TOUS les anciens fichiers
            print("🗑️ Nettoyage des anciens exports...")
            exporter.clean_old_exports()
            
            # ÉTAPE 2: Extractions directes (sans nettoyage supplémentaire)
            print("📋 Extraction utilisateurs...")
            users_df = extract_human_users(gl)
            if not users_df.empty:
                exporter.export_users(users_df, clean_first=False)
            
            print("👥 Extraction groupes...")
            groups_df = extract_groups(gl)
            if not groups_df.empty:
                exporter.export_groups(groups_df, clean_first=False)
            
            print("📁 Extraction projets actifs...")
            active_projects_df = extract_active_projects(gl)
            if not active_projects_df.empty:
                exporter.export_projects(active_projects_df, "active_projects", clean_first=False)
            
            print("📦 Extraction projets archivés...")  
            archived_projects_df = extract_archived_projects(gl)
            if not archived_projects_df.empty:
                exporter.export_projects(archived_projects_df, "archived_projects", clean_first=False)
            
            print("✅ Extraction complète terminée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur extraction: {e}")
            return False

    def process_events_extraction(self, events_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Extraction d'événements GitLab avec période configurable
        
        Args:
            events_config: Configuration de période depuis le menu
        
        Returns:
            True si succès, False sinon
        """
        print("📅 Extraction événements GitLab...")
        
        try:
            # Connexion GitLab
            client = GitLabClient()
            gl = client.connect()
            
            # Importation de l'extracteur d'événements
            from kenobi_tools.gitlab.extractors.gitlab_extract_events import extract_gitlab_events_with_period
            
            # Paramètres de période
            after_date = None
            period_name = "Tous"
            
            if events_config:
                after_date = events_config.get("after_date")
                period_name = events_config.get("name", "Période personnalisée")
                print(f"🗓️ Période sélectionnée: {period_name}")
            
            # Extraction avec période
            df_events = extract_gitlab_events_with_period(gl, limit=500, after_date=after_date)
            
            if df_events.empty:
                print("⚠️ Aucun événement extrait pour cette période")
                return True  # Pas d'erreur, juste pas de données
            
            # Initialiser l'exporteur
            exports_dir = Path(__file__).parent.parent.parent / "exports" / "gitlab"
            exporter = GitLabExcelExporter(exports_dir)
            
            # Export Excel avec mapping Power BI
            filename = exporter.export_events(df_events)
            
            if filename:
                print(f"✅ Événements exportés: {filename}")
                print(f"📊 Période: {period_name}")
                return True
            else:
                print("❌ Échec de l'export des événements")
                return False
            
        except Exception as e:
            print(f"❌ Erreur extraction événements: {e}")
            return False
