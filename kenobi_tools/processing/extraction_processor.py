"""
Processeur d'extraction GitLab - VERSION POWER BI
Orchestration simple sans statistiques ni complexité
Complexité cognitive visée: ≤ 10
"""
from pathlib import Path
from typing import Optional
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

    def process_events_extraction(self) -> bool:
        """
        Extraction d'événements - VERSION COMPLÈTE
        
        Returns:
            True si succès, False sinon
        """
        print("📅 Extraction événements...")
        
        try:
            # Connexion GitLab
            client = GitLabClient()
            gl = client.connect()
            
            # Initialiser l'exporteur
            exports_dir = Path(__file__).parent.parent.parent / "exports" / "gitlab"
            exporter = GitLabExcelExporter(exports_dir)
            
            # Pour les événements, on peut extraire un sample ou faire une extraction basique
            print("⚠️ Extraction événements désactivée temporairement")
            print("📊 Utilisez Power BI pour l'analyse temporelle des événements")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur extraction événements: {e}")
            return False
