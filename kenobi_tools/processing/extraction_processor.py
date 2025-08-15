"""
Logique de traitement des extractions GitLab
Sépare la logique métier de l'orchestration et de l'interface
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from tqdm import tqdm

from ..gitlab.client.gitlab_client import GitLabClient
from ..gitlab.extractors.gitlab_extract_users import extract_human_users
from ..gitlab.extractors.gitlab_extract_groups import extract_groups
from ..gitlab.extractors.gitlab_extract_active_projects import extract_active_projects
from ..gitlab.extractors.gitlab_extract_archived_projects import extract_archived_projects
from ..gitlab.extractors.gitlab_extract_events import extract_events_by_project
from ..gitlab.exporters.gitlab_export_excel import GitLabExcelExporter


class ExtractionProcessor:
    """Gestionnaire de la logique d'extraction et traitement des données"""

    def __init__(self):
        self.extracted_data = {}
        self.created_files = []
        self.total_steps = 4  # Utilisateurs, Groupes, Projets, Événements
        self.current_step = 0
        self.main_progress = None

    def _get_timestamp(self) -> str:
        """Génère un timestamp pour les noms de fichiers"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def process_base_data(self, gl_client, exports_dir: Path) -> bool:
        """
        Traite les données de base (utilisateurs, groupes, projets)
        
        Args:
            gl_client: Client GitLab
            gl: Instance gitlab
            exports_dir: Répertoire d'export
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Initialiser la barre de progression principale
            self.main_progress = tqdm(
                total=self.total_steps,
                desc="🎭 Maestro Kenobi",
                colour="cyan",
                leave=True,
                position=0
            )

            # Étape 1: Extraction utilisateurs
            self._update_progress("👥 Utilisateurs")
            users_df = self._extract_users(gl_client.client)
            if not users_df.empty:
                self.extracted_data["users"] = users_df

            # Étape 2: Extraction groupes
            self._update_progress("🏢 Groupes")
            groups_df = self._extract_groups(gl_client.client)
            if not groups_df.empty:
                self.extracted_data["groups"] = groups_df

            # Étape 3: Extraction projets
            self._update_progress("📁 Projets")
            projects_success = self._extract_projects(gl_client.client, exports_dir)
            
            return projects_success

        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des données de base: {e}")
            return False
        finally:
            if self.main_progress:
                self.main_progress.close()

    def process_events_data(self, gl, exports_dir: Path, events_config: Dict[str, Any]) -> bool:
        """
        Traite les données d'événements
        
        Args:
            gl_client: Client GitLab
            gl: Instance gitlab
            exports_dir: Répertoire d'export
            events_config: Configuration des événements
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Étape 4: Extraction événements
            self._update_progress("📊 Événements")
            events_success = self._extract_events(gl, events_config, exports_dir)
            return events_success

        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des événements: {e}")
            return False

    def _extract_users(self, gl_client) -> pd.DataFrame:
        """Extrait les utilisateurs"""
        try:
            return extract_human_users(gl_client, include_blocked=True)
        except Exception as e:
            print(f"❌ Erreur extraction utilisateurs: {e}")
            return pd.DataFrame()

    def _extract_groups(self, gl_client) -> pd.DataFrame:
        """Extrait les groupes"""
        try:
            return extract_groups(gl_client)
        except Exception as e:
            print(f"❌ Erreur extraction groupes: {e}")
            return pd.DataFrame()

    def _extract_projects(self, gl_client, exports_dir: Path) -> bool:
        """Extrait les projets actifs et archivés"""
        try:
            # Projets actifs
            active_projects_df = extract_active_projects(gl_client)
            if not active_projects_df.empty:
                self.extracted_data["active_projects"] = active_projects_df
                
                # Export des projets actifs
                excel_exporter = GitLabExcelExporter(exports_dir)
                filename = excel_exporter.export_projects(
                    active_projects_df,
                    filename=f"gitlab_projets_actifs_{self._get_timestamp()}.xlsx"
                )
                if filename:
                    self.created_files.append(filename)

            # Projets archivés
            archived_projects_df = extract_archived_projects(gl_client)
            if not archived_projects_df.empty:
                self.extracted_data["archived_projects"] = archived_projects_df
                
                # Export des projets archivés
                excel_exporter = GitLabExcelExporter(exports_dir)
                filename = excel_exporter.export_projects(
                    archived_projects_df,
                    filename=f"gitlab_projets_archives_{self._get_timestamp()}.xlsx"
                )
                if filename:
                    self.created_files.append(filename)

            return True

        except Exception as e:
            print(f"❌ Erreur extraction projets: {e}")
            return False

    def _extract_events(self, gl, events_config: Dict[str, Any], exports_dir: Path) -> bool:
        """Extrait les événements selon la configuration"""
        try:
            if not events_config:
                return True

            # Récupérer les projets pour l'extraction d'événements
            projects_to_process = []
            
            # Utiliser les projets actifs extraits
            if "active_projects" in self.extracted_data:
                projects_df = self.extracted_data["active_projects"]
                projects_to_process.extend(projects_df.to_dict('records'))

            if not projects_to_process:
                print("⚠️ Aucun projet trouvé pour l'extraction d'événements")
                return True

            # Extraire les événements
            events_df = extract_events_by_project(
                gl,
                projects_to_process,
                after_date=events_config.get("after_date"),
                before_date=events_config.get("before_date")
            )

            if not events_df.empty:
                self.extracted_data["events"] = events_df
                
                # Export des événements
                excel_exporter = GitLabExcelExporter(exports_dir)
                filename = excel_exporter.export_events(
                    events_df,
                    filename=f"gitlab_evenements_{self._get_timestamp()}.xlsx"
                )
                if filename:
                    self.created_files.append(filename)

            return True

        except Exception as e:
            print(f"❌ Erreur extraction événements: {e}")
            return False

    def export_base_data(self, exports_dir: Path) -> bool:
        """Exporte les données de base (utilisateurs et groupes)"""
        try:
            # Export des utilisateurs
            if "users" in self.extracted_data:
                excel_exporter = GitLabExcelExporter(exports_dir)
                filename = excel_exporter.export_users(
                    self.extracted_data["users"],
                    filename=f"gitlab_utilisateurs_{self._get_timestamp()}.xlsx"
                )
                if filename:
                    self.created_files.append(filename)

            # Export des groupes
            if "groups" in self.extracted_data:
                excel_exporter = GitLabExcelExporter(exports_dir)
                filename = excel_exporter.export_groups(
                    self.extracted_data["groups"],
                    filename=f"gitlab_groupes_{self._get_timestamp()}.xlsx"
                )
                if filename:
                    self.created_files.append(filename)

            return True

        except Exception as e:
            print(f"❌ Erreur export données de base: {e}")
            return False

    def _update_progress(self, task_name: str):
        """Met à jour la progression"""
        self.current_step += 1
        if self.main_progress:
            self.main_progress.set_description(f"🎭 {task_name}")
            self.main_progress.update(1)

    def get_extraction_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'extraction"""
        return {
            "extracted_data_keys": list(self.extracted_data.keys()),
            "created_files": self.created_files,
            "total_files": len(self.created_files)
        }
