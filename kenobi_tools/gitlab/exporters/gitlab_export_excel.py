"""
Exporteur Excel pour GitLab - VERSION REFACTORISÉE
Module principal pour exporter les données GitLab vers Excel avec formatage professionnel
Complexité cognitive réduite via séparation des responsabilités
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from .excel_formatters import ExcelStyleFormatter, ExcelColumnAdjuster
from .excel_statistics import ExcelStatsGenerator


class GitLabExcelExporter:
    """
    Exporteur Excel GitLab refactorisé pour réduire la complexité cognitive
    Utilise des classes spécialisées pour le formatage et les statistiques
    """
    
    # Constantes pour les colonnes répétées
    DATE_CREATION_HEADER = 'Date Creation'
    ID_PROJET_HEADER = 'id Projet'
    
    def __init__(self, export_dir: Optional[Path] = None):
        """
        Initialise l'exporteur avec les composants spécialisés
        
        Args:
            export_dir: Répertoire d'export (défaut: exports/gitlab/)
        """
        self.export_dir = self._setup_export_directory(export_dir)
        
        # Composants spécialisés pour réduire la complexité
        self.style_formatter = ExcelStyleFormatter()
        self.column_adjuster = ExcelColumnAdjuster()
        self.stats_generator = ExcelStatsGenerator()
    
    def _setup_export_directory(self, export_dir: Optional[Path]) -> Path:
        """Configure le répertoire d'export"""
        if export_dir is None:
            current_dir = Path(__file__).parent.parent.parent.parent
            export_path = current_dir / "exports" / "gitlab"
        else:
            export_path = Path(export_dir)
        
        export_path.mkdir(parents=True, exist_ok=True)
        return export_path
    
    def _generate_timestamp_filename(self, base_name: str) -> str:
        """Génère un nom de fichier avec timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"gitlab_{base_name}_{timestamp}.xlsx"
    
    def _apply_standard_formatting(self, worksheet, df_renamed: pd.DataFrame):
        """Applique le formatage standard à une feuille Excel"""
        if worksheet is not None:
            self.style_formatter.apply_header_style(worksheet, len(df_renamed.columns))
            self.column_adjuster.auto_adjust_columns(worksheet)
            self.style_formatter.apply_content_alignment(worksheet)
            self.style_formatter.setup_auto_filter_and_freeze(worksheet)
    
    def export_users(self, df_users: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Exporte les utilisateurs GitLab vers Excel
        
        Args:
            df_users: DataFrame des utilisateurs
            filename: Nom du fichier (optionnel)
            
        Returns:
            Chemin du fichier créé
        """
        if df_users.empty:
            print("⚠️ Aucun utilisateur à exporter")
            return ""
        
        filename = filename or self._generate_timestamp_filename("users")
        file_path = self.export_dir / filename
        
        # Mapping des colonnes pour Power BI
        columns_mapping = {
            'id': 'id Utilisateur',
            'username': 'Nom Utilisateur',
            'name': 'Nom Complet',
            'email': 'Email',
            'state': 'État',
            'created_at': self.DATE_CREATION_HEADER,
            'is_admin': 'Administrateur',
            'external': 'Externe',
            'two_factor_enabled': '2FA Activé',
            'last_sign_in_at': 'Dernière Connexion',
            'confirmed_at': 'Confirmé le',
            'last_activity_on': 'Dernière Activité',
            'web_url': 'URL Profil'
        }
        
        df_renamed = df_users.rename(columns=columns_mapping)
        
        with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
            df_renamed.to_excel(writer, sheet_name='Gitlab Users', index=False)
            worksheet = writer.sheets.get('Gitlab Users')
            self._apply_standard_formatting(worksheet, df_renamed)
        
        print(f"✅ Fichier utilisateurs Excel créé: {file_path}")
        print(f"👥 {len(df_renamed)} utilisateurs exportés")
        return str(file_path)
    
    def export_projects(self, df_projects: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Exporte les projets GitLab vers Excel
        
        Args:
            df_projects: DataFrame des projets
            filename: Nom du fichier (optionnel)
            
        Returns:
            Chemin du fichier créé
        """
        if df_projects.empty:
            print("⚠️ Aucun projet à exporter")
            return ""
        
        filename = filename or self._generate_timestamp_filename("projects")
        file_path = self.export_dir / filename
        
        # Mapping des colonnes pour Power BI
        columns_mapping = {
            'id': self.ID_PROJET_HEADER,
            'name': 'Nom Projet',
            'path': 'Chemin Projet',
            'description': 'Description',
            'web_url': 'URL Projet',
            'created_at': self.DATE_CREATION_HEADER,
            'last_activity_at': 'Dernière Activité',
            'namespace_name': 'Namespace',
            'namespace_kind': 'Type Namespace',
            'default_branch': 'Branche Défaut',
            'visibility': 'Visibilité',
            'archived': 'Archivé',
            'star_count': 'Étoiles',
            'forks_count': 'Forks'
        }
        
        df_renamed = df_projects.rename(columns=columns_mapping)
        
        with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
            df_renamed.to_excel(writer, sheet_name='Gitlab Projects', index=False)
            worksheet = writer.sheets.get('Gitlab Projects')
            self._apply_standard_formatting(worksheet, df_renamed)
        
        print(f"✅ Fichier projets Excel créé: {file_path}")
        print(f"📦 {len(df_renamed)} projets exportés")
        return str(file_path)
    
    def export_groups(self, df_groups: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Exporte les groupes GitLab vers Excel
        
        Args:
            df_groups: DataFrame des groupes
            filename: Nom du fichier (optionnel)
            
        Returns:
            Chemin du fichier créé
        """
        if df_groups.empty:
            print("⚠️ Aucun groupe à exporter")
            return ""
        
        filename = filename or self._generate_timestamp_filename("groups")
        file_path = self.export_dir / filename
        
        # Mapping des colonnes pour Power BI
        columns_mapping = {
            'id': 'id Groupe',
            'name': 'Nom Groupe',
            'path': 'Chemin Groupe',
            'description': 'Description',
            'web_url': 'URL Groupe',
            'created_at': self.DATE_CREATION_HEADER,
            'visibility': 'Visibilité',
            'full_name': 'Nom Complet',
            'full_path': 'Chemin Complet'
        }
        
        df_renamed = df_groups.rename(columns=columns_mapping)
        
        with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
            df_renamed.to_excel(writer, sheet_name='Gitlab Groups', index=False)
            worksheet = writer.sheets.get('Gitlab Groups')
            self._apply_standard_formatting(worksheet, df_renamed)
        
        print(f"✅ Fichier groupes Excel créé: {file_path}")
        print(f"👥 {len(df_renamed)} groupes exportés")
        return str(file_path)
    
    def export_events(self, df_events: pd.DataFrame, filename: Optional[str] = None, 
                     original_count: Optional[int] = None) -> str:
        """
        Exporte les événements GitLab vers Excel avec statistiques
        
        Args:
            df_events: DataFrame des événements
            filename: Nom du fichier (optionnel)
            original_count: Nombre d'événements avant filtrage
            
        Returns:
            Chemin du fichier créé
        """
        if df_events.empty:
            print("⚠️ Aucun événement à exporter")
            return ""
        
        filename = filename or self._generate_timestamp_filename("events")
        file_path = self.export_dir / filename
        
        # Mapping des colonnes pour Power BI
        columns_mapping = {
            'id': 'id Evenement',
            'title': 'Titre',
            'action_name': 'Action',
            'target_type': 'Type Cible',
            'target_title': 'Titre Cible',
            'created_at': self.DATE_CREATION_HEADER,
            'author_name': 'Nom Auteur',
            'author_username': 'Username Auteur',
            'project_id': self.ID_PROJET_HEADER,
            'project_name': 'Nom Projet'
        }
        
        df_renamed = df_events.rename(columns=columns_mapping)
        
        with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
            # Feuille principale des événements
            df_renamed.to_excel(writer, sheet_name='Gitlab Events', index=False)
            worksheet = writer.sheets.get('Gitlab Events')
            self._apply_standard_formatting(worksheet, df_renamed)
            
            # Feuille des statistiques
            stats_data = self.stats_generator.generate_events_statistics(df_events, original_count)
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Statistiques', index=False, header=False)
            
            stats_worksheet = writer.sheets.get('Statistiques')
            if stats_worksheet:
                self.style_formatter.apply_header_style(stats_worksheet, 2)
                self.column_adjuster.auto_adjust_columns(stats_worksheet)
        
        print(f"✅ Fichier événements Excel créé: {file_path}")
        print(f"📊 {len(df_renamed)} événements exportés")
        return str(file_path)
