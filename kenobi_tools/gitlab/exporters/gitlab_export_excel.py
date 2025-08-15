"""
Exporteur Excel pour GitLab - VERSION ULTRA-SIMPLIFIÉE POWER BI
Export brut sans formatage - Power BI s'occupe de tout !
Complexité cognitive visée: ≤ 8
"""
from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd


class GitLabExcelExporter:
    """Exporteur Excel minimaliste pour Power BI"""
    
    def __init__(self, export_dir: Optional[Path] = None):
        """Initialise l'exporteur simple"""
        if export_dir is None:
            current_dir = Path(__file__).parent.parent.parent.parent
            self.export_dir = current_dir / "exports" / "gitlab"
        else:
            self.export_dir = Path(export_dir)
        
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_users(self, df_users: pd.DataFrame) -> str:
        """Exporte les utilisateurs - VERSION SIMPLE"""
        if df_users.empty:
            print("⚠️ Aucun utilisateur à exporter")
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.export_dir / f"gitlab_users_{timestamp}.xlsx"
        
        # Export basique - Power BI fait le reste
        df_users.to_excel(filename, sheet_name="Gitlab Users", index=False)
        
        print(f"✅ {len(df_users)} utilisateurs → {filename}")
        return str(filename)
    
    def export_groups(self, df_groups: pd.DataFrame) -> str:
        """Exporte les groupes - VERSION SIMPLE"""
        if df_groups.empty:
            print("⚠️ Aucun groupe à exporter")
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.export_dir / f"gitlab_groups_{timestamp}.xlsx"
        
        df_groups.to_excel(filename, sheet_name="Gitlab Groups", index=False)
        
        print(f"✅ {len(df_groups)} groupes → {filename}")
        return str(filename)
    
    def export_projects(self, df_projects: pd.DataFrame, project_type: str = "projects") -> str:
        """Exporte les projets - VERSION SIMPLE"""
        if df_projects.empty:
            print(f"⚠️ Aucun projet {project_type} à exporter")
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.export_dir / f"gitlab_{project_type}_{timestamp}.xlsx"
        sheet_name = f"Gitlab {project_type.title()}"
        
        df_projects.to_excel(filename, sheet_name=sheet_name, index=False)
        
        print(f"✅ {len(df_projects)} projets {project_type} → {filename}")
        return str(filename)
    
    def export_events(self, df_events: pd.DataFrame) -> str:
        """Exporte les événements - VERSION SIMPLE"""
        if df_events.empty:
            print("⚠️ Aucun événement à exporter")
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.export_dir / f"gitlab_events_{timestamp}.xlsx"
        
        df_events.to_excel(filename, sheet_name="Gitlab Events", index=False)
        
        print(f"✅ {len(df_events)} événements → {filename}")
        return str(filename)


# Version encore plus simple pour usage direct
def quick_export_to_excel(df: pd.DataFrame, filename: str) -> str:
    """Export ultra-rapide pour Power BI"""
    if df.empty:
        return ""
    
    df.to_excel(filename, index=False)
    return filename
