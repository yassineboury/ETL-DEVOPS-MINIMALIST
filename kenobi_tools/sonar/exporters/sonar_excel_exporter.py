"""
Exporteur Excel pour SonarQube - VERSION SIMPLIFIÉE POWER BI
Export brut sans formatage - Power BI s'occupe de tout !
Pattern identique à GitLab
"""
from pathlib import Path
from typing import Optional
import pandas as pd
import glob
import os

from kenobi_tools.sonar.extractors.sonar_extract_metrics import (
    SONAR_METRICS_COLUMN_MAPPING,
    SONAR_METRICS_COLUMN_ORDER
)

# Constantes
SONAR_SHEET_NAME = "Sonar Metrics"
DATE_DERNIERE_ANALYSE_COLUMN = "Date Dernière Analyse"


class SonarExcelExporter:
    """Exporteur Excel minimaliste pour SonarQube - Power BI ready"""
    
    def __init__(self, export_dir: Optional[Path] = None):
        """Initialise l'exporteur simple"""
        if export_dir is None:
            current_dir = Path(__file__).parent.parent.parent.parent
            self.export_dir = current_dir / "exports" / "sonar"
        else:
            self.export_dir = Path(export_dir)
        
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_old_exports(self):
        """Supprime tous les anciens fichiers Excel"""
        xlsx_files = glob.glob(str(self.export_dir / "*.xlsx"))
        for file in xlsx_files:
            try:
                os.remove(file)
                print(f"🗑️ Ancien fichier supprimé: {Path(file).name}")
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {Path(file).name}: {e}")
    
    def export_projects(self, df_metrics: pd.DataFrame, clean_first: bool = False) -> str:
        """Exporte les métriques SonarQube complètes - VERSION SIMPLE"""
        # Nettoyer les anciens exports seulement si demandé
        if clean_first:
            self.clean_old_exports()
        
        # Nom fixe comme GitLab (sans timestamp)
        filename = self.export_dir / "sonar_metrics.xlsx"
        
        if df_metrics.empty:
            # Créer un fichier vide avec en-têtes pour Power BI
            empty_df = pd.DataFrame(columns=SONAR_METRICS_COLUMN_ORDER)
            empty_df.to_excel(filename, sheet_name=SONAR_SHEET_NAME, index=False)
            print(f"⚠️ Aucune métrique trouvée - fichier vide créé → {filename}")
            return str(filename)
        
        # Mapping des colonnes pour Power BI
        df_export = df_metrics.rename(columns=SONAR_METRICS_COLUMN_MAPPING)
        
        # Réordonner les colonnes selon la spécification
        df_export = df_export[SONAR_METRICS_COLUMN_ORDER]
        
        # TRI PAR DATE : Plus récente → Plus ancienne
        if DATE_DERNIERE_ANALYSE_COLUMN in df_export.columns:
            # Convertir les dates pour le tri (gérer les valeurs vides)
            df_export['_date_sort'] = pd.to_datetime(df_export[DATE_DERNIERE_ANALYSE_COLUMN], 
                                                    format='%d/%m/%Y %H:%M:%S', errors='coerce')
            # Trier par date décroissante (NaT en fin)
            df_export = df_export.sort_values('_date_sort', ascending=False, na_position='last')
            # Supprimer la colonne temporaire
            df_export = df_export.drop('_date_sort', axis=1)
        
        # Export basique - Power BI fait le reste
        df_export.to_excel(filename, sheet_name=SONAR_SHEET_NAME, index=False)
        
        print(f"✅ {len(df_metrics)} métriques SonarQube → {filename}")
        return str(filename)


def export_sonar_metrics_to_excel(df_metrics: pd.DataFrame, filename: Optional[str] = None) -> str:
    """Export fonction utilitaire - comme dans GitLab"""
    if filename:
        # Pour tests uniquement - utiliser le répertoire sonar standard
        current_dir = Path(__file__).parent.parent.parent.parent
        export_dir = current_dir / "exports" / "sonar"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Nom fixe personnalisé (pour tests)
        custom_path = export_dir / filename
        
        # Mapping Power BI
        df_export = df_metrics.rename(columns=SONAR_METRICS_COLUMN_MAPPING)
        df_export = df_export[SONAR_METRICS_COLUMN_ORDER]
        
        # TRI PAR DATE : Plus récente → Plus ancienne (même logique que export_projects)
        if DATE_DERNIERE_ANALYSE_COLUMN in df_export.columns:
            # Convertir les dates pour le tri (gérer les valeurs vides)
            df_export['_date_sort'] = pd.to_datetime(df_export[DATE_DERNIERE_ANALYSE_COLUMN], 
                                                    format='%d/%m/%Y %H:%M:%S', errors='coerce')
            # Trier par date décroissante (NaT en fin)
            df_export = df_export.sort_values('_date_sort', ascending=False, na_position='last')
            # Supprimer la colonne temporaire
            df_export = df_export.drop('_date_sort', axis=1)
        
        df_export.to_excel(custom_path, sheet_name=SONAR_SHEET_NAME, index=False)
        print(f"✅ Export SonarQube test: {custom_path}")
        return str(custom_path)
    else:
        # Export standard
        exporter = SonarExcelExporter()
        return exporter.export_projects(df_metrics)