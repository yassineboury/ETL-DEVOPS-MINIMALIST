"""
Processeur d'extraction GitLab + SonarQube - VERSION POWER BI
Orchestration simple sans statistiques ni complexité
Complexité cognitive visée: ≤ 10
"""
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import shutil
from datetime import datetime

from ..gitlab.client.gitlab_client import GitLabClient
from ..gitlab.extractors.gitlab_extract_users import extract_human_users
from ..gitlab.extractors.gitlab_extract_groups import extract_groups
from ..gitlab.extractors.gitlab_extract_active_projects import extract_active_projects
from ..gitlab.extractors.gitlab_extract_archived_projects import extract_archived_projects
from ..gitlab.exporters.gitlab_export_excel import GitLabExcelExporter

# Imports SonarQube
from ..sonar.client.sonar_client import SonarClient
from ..sonar.extractors.sonar_extract_metrics import extract_sonar_metrics
from ..sonar.exporters.sonar_excel_exporter import SonarExcelExporter


class ExtractionProcessor:
    """Processeur simple d'extraction GitLab + SonarQube"""

    def __init__(self):
        self.extracted_data = {}
        
    def _archive_current_exports(self, exports_dir: Path) -> bool:
        """
        Archive les exports actuels selon la structure :
        current/ → previous/ (avec suffix _prev) + archive/DDMMYYYY_HHMM/
        
        Args:
            exports_dir: Répertoire racine exports/
            
        Returns:
            True si succès, False sinon
        """
        try:
            current_dir = exports_dir / "current"
            previous_dir = exports_dir / "previous" 
            archive_dir = exports_dir / "archive"
            
            # Si pas de current/, rien à archiver
            if not current_dir.exists():
                print("📁 Aucun export current/ à archiver")
                return True
            
            # Générer timestamp français DDMMYYYY_HHMM
            timestamp = datetime.now().strftime("%d%m%Y_%H%M")
            archive_path = archive_dir / timestamp
            
            print(f"📦 Archivage des exports vers {timestamp}...")
            
            # ÉTAPE 1: Archiver current/ → archive/timestamp/
            if any(current_dir.iterdir()):
                archive_path.mkdir(parents=True, exist_ok=True)
                shutil.copytree(current_dir, archive_path, dirs_exist_ok=True)
                print(f"✅ Archive créée: {archive_path}")
            
            # ÉTAPE 2: current/ → previous/ (avec suffix _prev)
            if previous_dir.exists():
                shutil.rmtree(previous_dir)
            
            previous_dir.mkdir(parents=True, exist_ok=True)
            
            # Copier et renommer avec suffix _prev
            for platform_dir in current_dir.iterdir():
                if platform_dir.is_dir():
                    platform_name = platform_dir.name  # gitlab ou sonar
                    prev_platform_dir = previous_dir / platform_name
                    prev_platform_dir.mkdir(exist_ok=True)
                    
                    # Copier chaque fichier avec suffix _prev
                    for file_path in platform_dir.glob("*.xlsx"):
                        old_name = file_path.stem  # nom sans extension
                        new_name = f"{old_name}_prev.xlsx"
                        dest_path = prev_platform_dir / new_name
                        shutil.copy2(file_path, dest_path)
                        print(f"📋 {file_path.name} → {new_name}")
            
            print("✅ Archivage terminé - Prêt pour nouveaux exports")
            return True
            
        except Exception as e:
            print(f"❌ Erreur archivage: {e}")
            return False
    
    def _prepare_export_structure(self, exports_dir: Path) -> bool:
        """
        Prépare la structure d'export current/gitlab/ et current/sonar/
        
        Args:
            exports_dir: Répertoire racine exports/
            
        Returns:
            True si succès, False sinon
        """
        try:
            current_dir = exports_dir / "current"
            
            # Nettoyer current/ pour nouveaux exports
            if current_dir.exists():
                shutil.rmtree(current_dir)
            
            # Recréer structure current/
            (current_dir / "gitlab").mkdir(parents=True, exist_ok=True)
            (current_dir / "sonar").mkdir(parents=True, exist_ok=True)
            
            print("📁 Structure current/ préparée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur préparation structure: {e}")
            return False
        
    def process_all_data(self, exports_dir: Path, include_sonar: bool = False) -> bool:
        """
        Traite toutes les données GitLab + SonarQube optionnel
        NOUVEAU: Avec archivage automatique current/previous/archive
        
        Args:
            exports_dir: Répertoire d'export
            include_sonar: True pour inclure SonarQube, False pour GitLab seulement
            
        Returns:
            True si succès, False sinon
        """
        print("🚀 Début extraction DevSecOps complète")
        
        try:
            # PHASE 0: Archivage des exports précédents
            if not self._archive_current_exports(exports_dir):
                print("⚠️ Problème archivage - continuation sans archivage")
            
            # PHASE 1: Préparation structure current/
            if not self._prepare_export_structure(exports_dir):
                return False
            
            success = True
            
            # PHASE 2: Extraction GitLab → current/gitlab/
            current_gitlab_dir = exports_dir / "current" / "gitlab"
            success &= self._process_gitlab_data(current_gitlab_dir)
            
            # PHASE 3: Extraction SonarQube → current/sonar/ (optionnelle)
            if include_sonar and success:
                current_sonar_dir = exports_dir / "current" / "sonar"
                success &= self._process_sonar_data(current_sonar_dir)
            
            if success:
                print("🎉 Extraction complète réussie avec archivage !")
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur extraction complète: {e}")
            return False
    
    def _process_gitlab_data(self, exports_dir: Path) -> bool:
        """Traite les données GitLab"""
        print("\n📊 === EXTRACTION GITLAB ===")
        
        try:
            # Connexion GitLab
            client = GitLabClient()
            gl = client.connect()
            
            # Initialiser l'exporteur GitLab
            gitlab_exporter = GitLabExcelExporter(exports_dir)
            
            # ÉTAPE 1: Nettoyage initial de TOUS les anciens fichiers GitLab
            print("🗑️ Nettoyage des anciens exports GitLab...")
            gitlab_exporter.clean_old_exports()
            
            # ÉTAPE 2: Extractions GitLab directes
            print("📋 Extraction utilisateurs...")
            users_df = extract_human_users(gl)
            if not users_df.empty:
                gitlab_exporter.export_users(users_df, clean_first=False)
            
            print("👥 Extraction groupes...")
            groups_df = extract_groups(gl)
            if not groups_df.empty:
                gitlab_exporter.export_groups(groups_df, clean_first=False)
            
            print("📁 Extraction projets actifs...")
            active_projects_df = extract_active_projects(gl)
            if not active_projects_df.empty:
                gitlab_exporter.export_projects(active_projects_df, "active_projects", clean_first=False)
            
            print("📦 Extraction projets archivés...")  
            archived_projects_df = extract_archived_projects(gl)
            if not archived_projects_df.empty:
                gitlab_exporter.export_projects(archived_projects_df, "archived_projects", clean_first=False)
            
            print("✅ Extraction GitLab terminée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur extraction GitLab: {e}")
            return False
    
    def _process_sonar_data(self, sonar_exports_dir: Path) -> bool:
        """Traite les données SonarQube"""
        print("\n📈 === EXTRACTION SONARQUBE ===")
        
        try:
            # Connexion SonarQube
            sonar_client_wrapper = SonarClient()
            sonar_client = sonar_client_wrapper.connect()
            
            if not sonar_client:
                print("❌ Connexion SonarQube échouée")
                return False
            
            # Créer le répertoire SonarQube si nécessaire
            sonar_exports_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialiser l'exporteur SonarQube
            sonar_exporter = SonarExcelExporter(sonar_exports_dir)
            
            print("📈 Extraction métriques SonarQube (15 champs)...")
            metrics_df = extract_sonar_metrics(sonar_client)
            
            if not metrics_df.empty:
                filename = sonar_exporter.export_projects(metrics_df)
                if filename:
                    print(f"✅ Métriques SonarQube exportées: {filename}")
                    return True
                else:
                    print("❌ Échec export SonarQube")
                    return False
            else:
                print("⚠️ Aucune métrique SonarQube extraite")
                return True  # Pas d'erreur, juste pas de données
            
        except Exception as e:
            print(f"❌ Erreur extraction SonarQube: {e}")
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
            
            # Utiliser la nouvelle structure current/gitlab/
            exports_dir = Path(__file__).parent.parent.parent / "exports" / "current" / "gitlab"
            exports_dir.mkdir(parents=True, exist_ok=True)
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
