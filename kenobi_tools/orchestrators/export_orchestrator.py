"""
Orchestrateur d'exports - Logique métier pour les exports GitLab
Module séparé pour les opérations d'extraction et d'export
"""
import contextlib
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from tqdm import tqdm

from kenobi_tools.gitlab.client.gitlab_client import GitLabClient
from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
from kenobi_tools.gitlab.extractors.gitlab_extract_active_projects import extract_active_projects
from kenobi_tools.gitlab.extractors.gitlab_extract_archived_projects import extract_archived_projects
from kenobi_tools.gitlab.extractors.gitlab_extract_events import extract_events_by_project
from kenobi_tools.gitlab.extractors.gitlab_extract_groups import extract_groups
from kenobi_tools.gitlab.extractors.gitlab_extract_users import extract_human_users


class KenobiExportOrchestrator:
    """
    Orchestrateur d'exports GitLab
    Gère toutes les opérations d'extraction et d'export
    """
    
    def __init__(self):
        """Initialise l'orchestrateur"""
        self.gitlab_client = None
        self.gitlab_instance = None
        self.exporter = GitLabExcelExporter()
    
    def setup_gitlab_connection(self) -> bool:
        """
        Configure la connexion GitLab
        
        Returns:
            True si la connexion est réussie, False sinon
        """
        try:
            self.gitlab_client = GitLabClient()
            self.gitlab_instance = self.gitlab_client.connect()
            return self.gitlab_instance is not None
        except Exception as e:
            print(f"❌ Erreur de connexion GitLab: {e}")
            return False
    
    def close_gitlab_connection(self):
        """Ferme la connexion GitLab"""
        if self.gitlab_client:
            self.gitlab_client.disconnect()
    
    def extract_and_export_users(self) -> bool:
        """
        Extrait et exporte les utilisateurs
        
        Returns:
            True si succès, False sinon
        """
        if not self.gitlab_instance:
            return False
        
        try:
            with contextlib.redirect_stdout(sys.stdout):
                print("📥 Extraction des utilisateurs...")
                df_users = extract_human_users(self.gitlab_instance)
                
                if not df_users.empty:
                    print("📤 Export Excel des utilisateurs...")
                    self.exporter.export_users(df_users)
                    return True
                else:
                    print("⚠️ Aucun utilisateur trouvé")
                    return False
        except Exception as e:
            print(f"❌ Erreur lors de l'export des utilisateurs: {e}")
            return False
    
    def extract_and_export_groups(self) -> bool:
        """
        Extrait et exporte les groupes
        
        Returns:
            True si succès, False sinon
        """
        if not self.gitlab_instance:
            return False
        
        try:
            print("📥 Extraction des groupes...")
            df_groups = extract_groups(self.gitlab_instance)
            
            if not df_groups.empty:
                print("📤 Export Excel des groupes...")
                self.exporter.export_groups(df_groups)
                return True
            else:
                print("⚠️ Aucun groupe trouvé")
                return False
        except Exception as e:
            print(f"❌ Erreur lors de l'export des groupes: {e}")
            return False
    
    def extract_and_export_active_projects(self) -> bool:
        """
        Extrait et exporte les projets actifs
        
        Returns:
            True si succès, False sinon
        """
        if not self.gitlab_instance:
            return False
        
        try:
            print("📥 Extraction des projets actifs...")
            df_projects = extract_active_projects(self.gitlab_instance)
            
            if not df_projects.empty:
                print("📤 Export Excel des projets actifs...")
                self.exporter.export_projects(df_projects, "gitlab_active_projects.xlsx")
                return True
            else:
                print("⚠️ Aucun projet actif trouvé")
                return False
        except Exception as e:
            print(f"❌ Erreur lors de l'export des projets actifs: {e}")
            return False
    
    def extract_and_export_archived_projects(self) -> bool:
        """
        Extrait et exporte les projets archivés
        
        Returns:
            True si succès, False sinon
        """
        if not self.gitlab_instance:
            return False
        
        try:
            print("📥 Extraction des projets archivés...")
            df_projects = extract_archived_projects(self.gitlab_instance)
            
            if not df_projects.empty:
                print("📤 Export Excel des projets archivés...")
                self.exporter.export_projects(df_projects, "gitlab_archived_projects.xlsx")
                return True
            else:
                print("⚠️ Aucun projet archivé trouvé")
                return False
        except Exception as e:
            print(f"❌ Erreur lors de l'export des projets archivés: {e}")
            return False
    
    def extract_and_export_events(self, days: Optional[int], period_label: str) -> bool:
        """
        Extrait et exporte les événements
        
        Args:
            days: Nombre de jours à extraire (None pour tous)
            period_label: Label de la période sélectionnée
            
        Returns:
            True si succès, False sinon
        """
        if not self.gitlab_instance:
            return False
        
        try:
            print(f"📥 Extraction des événements ({period_label})...")
            
            # Calculer la date de début si nécessaire
            after_date = None
            if days is not None:
                after_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            df_events = extract_events_by_project(
                self.gitlab_instance, 
                after_date=after_date
            )
            
            if not df_events.empty:
                print("📤 Export Excel des événements...")
                filename = f"gitlab_events_{period_label.replace(' ', '_').lower()}.xlsx"
                self.exporter.export_events(df_events, filename)
                return True
            else:
                print(f"⚠️ Aucun événement trouvé pour {period_label}")
                return False
        except Exception as e:
            print(f"❌ Erreur lors de l'export des événements: {e}")
            return False
    
    def perform_complete_export(self) -> bool:
        """
        Effectue un export complet de toutes les données
        
        Returns:
            True si succès, False sinon
        """
        if not self.gitlab_instance:
            return False
        
        print("🚀 Début de l'export complet GitLab...")
        success_count = 0
        total_operations = 5
        
        # Progress bar pour l'export complet
        with tqdm(total=total_operations, desc="Export complet", unit="module") as pbar:
            # 1. Utilisateurs
            pbar.set_description("Export utilisateurs")
            if self.extract_and_export_users():
                success_count += 1
            pbar.update(1)
            
            # 2. Groupes
            pbar.set_description("Export groupes")
            if self.extract_and_export_groups():
                success_count += 1
            pbar.update(1)
            
            # 3. Projets actifs
            pbar.set_description("Export projets actifs")
            if self.extract_and_export_active_projects():
                success_count += 1
            pbar.update(1)
            
            # 4. Projets archivés
            pbar.set_description("Export projets archivés")
            if self.extract_and_export_archived_projects():
                success_count += 1
            pbar.update(1)
            
            # 5. Événements (30 derniers jours)
            pbar.set_description("Export événements")
            if self.extract_and_export_events(30, "30_derniers_jours"):
                success_count += 1
            pbar.update(1)
        
        print(f"📊 Export complet terminé: {success_count}/{total_operations} modules exportés avec succès")
        return success_count > 0
