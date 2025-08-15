"""
Processeur d'extraction GitLab - VERSION ULTRA-SIMPLIFIÉE POWER BI
Orchestration simple sans statistiques ni complexité
Complexité cognitive visée: ≤ 10
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
import pandas as pd

from ..gitlab.client.gitlab_client import GitLabClient
from ..gitlab.extractors.gitlab_extract_users import extract_human_users
from ..gitlab.extractors.gitlab_extract_groups import extract_groups
from ..gitlab.extractors.gitlab_extract_active_projects import extract_active_projects
from ..gitlab.extractors.gitlab_extract_archived_projects import extract_archived_projects
from ..gitlab.extractors.gitlab_extract_events import extract_events_by_project
from ..gitlab.exporters.gitlab_export_excel import GitLabExcelExporter


class ExtractionProcessor:
    """Processeur simple d'extraction GitLab"""

    def __init__(self):
        self.extracted_data = {}
        
    def process_all_data(self, exports_dir: Path) -> bool:
        """
        Traite toutes les données GitLab - VERSION SIMPLIFIÉE
        
        Args:
            exports_dir: Répertoire d'export
            
        Returns:
            True si succès, False sinon
        """
        print("🚀 Début extraction GitLab simplifiée")
        
        try:
            # Connexion GitLab
            client = GitLabClient()
            gl = client.connect()
            
            # Extractions directes
            print("👥 Extraction utilisateurs...")
            self.extracted_data['users'] = extract_human_users(gl)
            
            print("👥 Extraction groupes...")
            self.extracted_data['groups'] = extract_groups(gl)
            
            print("📁 Extraction projets actifs...")
            self.extracted_data['active_projects'] = extract_active_projects(gl)
            
            print("📦 Extraction projets archivés...")  
            self.extracted_data['archived_projects'] = extract_archived_projects(gl)
            
            # Export Excel direct - utilisation des méthodes existantes
            print("📊 Export Excel...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export utilisateurs
            if not self.extracted_data.get('users', pd.DataFrame()).empty:
                users_file = exports_dir / f"gitlab_users_{timestamp}.xlsx"
                self.extracted_data['users'].to_excel(users_file, index=False)
                print(f"✅ Utilisateurs exportés: {users_file}")
            
            # Export groupes  
            if not self.extracted_data.get('groups', pd.DataFrame()).empty:
                groups_file = exports_dir / f"gitlab_groups_{timestamp}.xlsx"
                self.extracted_data['groups'].to_excel(groups_file, index=False)
                print(f"✅ Groupes exportés: {groups_file}")
            
            # Export projets actifs
            if not self.extracted_data.get('active_projects', pd.DataFrame()).empty:
                active_file = exports_dir / f"gitlab_active_projects_{timestamp}.xlsx"
                self.extracted_data['active_projects'].to_excel(active_file, index=False)
                print(f"✅ Projets actifs exportés: {active_file}")
                
            # Export projets archivés
            if not self.extracted_data.get('archived_projects', pd.DataFrame()).empty:
                archived_file = exports_dir / f"gitlab_archived_projects_{timestamp}.xlsx"
                self.extracted_data['archived_projects'].to_excel(archived_file, index=False)
                print(f"✅ Projets archivés exportés: {archived_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur extraction: {e}")
            return False

    def process_events_extraction(self) -> bool:
        """
        Extraction d'événements désactivée - Power BI s'en charge
        
        Returns:
            True (fonction simplifiée)
        """
        print("📅 Extraction événements...")
        print("⚠️ Extraction événements désactivée - utilisez Power BI pour l'analyse temporelle")
        return True
