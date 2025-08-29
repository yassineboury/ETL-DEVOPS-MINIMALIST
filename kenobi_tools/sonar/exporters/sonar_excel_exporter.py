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

from kenobi_tools.sonar.extractors.sonar_extract_projects import (
    SONAR_PROJECTS_COLUMN_MAPPING,
    SONAR_PROJECTS_COLUMN_ORDER
)


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
    
    def export_projects(self, df_projects: pd.DataFrame, clean_first: bool = False) -> str:
        """Exporte les projets SonarQube - VERSION SIMPLE"""
        # Nettoyer les anciens exports seulement si demandé
        if clean_first:
            self.clean_old_exports()
        
        filename = self.export_dir / "sonar_projects.xlsx"
        
        if df_projects.empty:
            # Créer un fichier vide avec en-têtes pour Power BI
            empty_df = pd.DataFrame(columns=SONAR_PROJECTS_COLUMN_ORDER)
            empty_df.to_excel(filename, sheet_name="Sonar Projects", index=False)
            print(f"⚠️ Aucun projet trouvé - fichier vide créé → {filename}")
            return str(filename)
        
        # Mapping des colonnes pour Power BI
        df_export = df_projects.rename(columns=SONAR_PROJECTS_COLUMN_MAPPING)
        
        # Réordonner les colonnes selon la spécification
        df_export = df_export[SONAR_PROJECTS_COLUMN_ORDER]
        
        # Export basique - Power BI fait le reste
        df_export.to_excel(filename, sheet_name="Sonar Projects", index=False)
        
        print(f"✅ {len(df_projects)} projets → {filename}")
        return str(filename)