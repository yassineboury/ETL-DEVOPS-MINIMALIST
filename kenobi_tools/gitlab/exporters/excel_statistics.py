"""
Statistiques Excel - Générateur de statistiques pour les exports Excel
Module séparé pour les calculs statistiques et métriques
"""
from typing import List, Optional

import pandas as pd


class ExcelStatsGenerator:
    """Classe responsable de la génération des statistiques Excel"""
    
    METRIC_COLUMN_NAME = 'Métrique'
    
    def generate_events_statistics(self, df_events: pd.DataFrame, original_count: Optional[int] = None) -> List[List]:
        """
        Génère toutes les statistiques pour les événements
        
        Args:
            df_events: DataFrame des événements
            original_count: Nombre d'événements avant filtrage
            
        Returns:
            Liste des données statistiques
        """
        stats_data = []
        
        self._add_general_statistics(stats_data, df_events, original_count)
        self._add_action_statistics(stats_data, df_events)
        self._add_target_statistics(stats_data, df_events)
        self._add_project_statistics(stats_data, df_events)
        self._add_author_statistics(stats_data, df_events)
        
        return stats_data

    def generate_mr_statistics(self, df_mrs: pd.DataFrame) -> List[List]:
        """
        Génère toutes les statistiques pour les merge requests
        
        Args:
            df_mrs: DataFrame des merge requests
            
        Returns:
            Liste des données statistiques
        """
        stats_data = []
        
        self._add_general_mr_stats(stats_data, df_mrs)
        self._add_state_stats(stats_data, df_mrs)
        self._add_merge_status_stats(stats_data, df_mrs)
        self._add_conflict_stats(stats_data, df_mrs)
        self._add_project_stats(stats_data, df_mrs)
        self._add_author_stats(stats_data, df_mrs)
        
        return stats_data

    def _add_general_statistics(self, stats_data: List, df_events: pd.DataFrame, original_count: Optional[int]):
        """Ajoute les statistiques générales des événements"""
        stats_data.extend([
            [self.METRIC_COLUMN_NAME, 'Valeur'],
            ['Total événements', len(df_events)],
        ])
        
        if original_count:
            stats_data.append(['Total événements (avant filtrage)', original_count])

    def _add_action_statistics(self, stats_data: List, df_events: pd.DataFrame):
        """Ajoute les statistiques par action"""
        if 'action' in df_events.columns:
            action_counts = df_events['action'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Actions les plus fréquentes:', '']
            ])
            for action, count in action_counts.head(10).items():
                stats_data.append([f"  {action}", count])

    def _add_target_statistics(self, stats_data: List, df_events: pd.DataFrame):
        """Ajoute les statistiques par type de cible"""
        if 'target_type' in df_events.columns:
            target_counts = df_events['target_type'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Types de cibles:', '']
            ])
            for target, count in target_counts.items():
                stats_data.append([f"  {target}", count])

    def _add_project_statistics(self, stats_data: List, df_events: pd.DataFrame):
        """Ajoute les statistiques par projet"""
        if 'nom_projet' in df_events.columns:
            project_counts = df_events['nom_projet'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Projets les plus actifs:', '']
            ])
            for project, count in project_counts.head(10).items():
                stats_data.append([f"  {project}", count])

    def _add_author_statistics(self, stats_data: List, df_events: pd.DataFrame):
        """Ajoute les statistiques par auteur"""
        if 'nom_auteur' in df_events.columns:
            author_counts = df_events['nom_auteur'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Auteurs les plus actifs:', '']
            ])
            for author, count in author_counts.head(10).items():
                stats_data.append([f"  {author}", count])

    def _add_general_mr_stats(self, stats_data: List, df_mrs: pd.DataFrame):
        """Ajoute les statistiques générales des MR"""
        stats_data.extend([
            [self.METRIC_COLUMN_NAME, 'Valeur'],
            ['Total Merge Requests', len(df_mrs)],
        ])

    def _add_state_stats(self, stats_data: List, df_mrs: pd.DataFrame):
        """Ajoute les statistiques par état des MR"""
        if 'etat' in df_mrs.columns:
            state_counts = df_mrs['etat'].value_counts()
            stats_data.extend([
                ['', ''],
                ['États des MR:', '']
            ])
            for state, count in state_counts.items():
                stats_data.append([f"  {state}", count])

    def _add_merge_status_stats(self, stats_data: List, df_mrs: pd.DataFrame):
        """Ajoute les statistiques de statut de merge"""
        if 'merge_status' in df_mrs.columns:
            merge_counts = df_mrs['merge_status'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Statuts de merge:', '']
            ])
            for status, count in merge_counts.items():
                stats_data.append([f"  {status}", count])

    def _add_conflict_stats(self, stats_data: List, df_mrs: pd.DataFrame):
        """Ajoute les statistiques de conflits"""
        if 'has_conflicts' in df_mrs.columns:
            conflict_counts = df_mrs['has_conflicts'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Conflits:', '']
            ])
            for conflict, count in conflict_counts.items():
                stats_data.append([f"  {'Avec conflits' if conflict else 'Sans conflits'}", count])

    def _add_project_stats(self, stats_data: List, df_mrs: pd.DataFrame):
        """Ajoute les statistiques par projet pour les MR"""
        if 'nom_projet' in df_mrs.columns:
            project_counts = df_mrs['nom_projet'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Projets avec le plus de MR:', '']
            ])
            for project, count in project_counts.head(10).items():
                stats_data.append([f"  {project}", count])

    def _add_author_stats(self, stats_data: List, df_mrs: pd.DataFrame):
        """Ajoute les statistiques par auteur pour les MR"""
        if 'nom_auteur' in df_mrs.columns:
            author_counts = df_mrs['nom_auteur'].value_counts()
            stats_data.extend([
                ['', ''],
                ['Auteurs avec le plus de MR:', '']
            ])
            for author, count in author_counts.head(10).items():
                stats_data.append([f"  {author}", count])
