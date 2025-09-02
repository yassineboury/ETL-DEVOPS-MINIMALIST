"""
Exporteur Excel pour GitLab - VERSION ULTRA-SIMPLIFIÉE POWER BI
Export brut sans formatage - Power BI s'occupe de tout !
Complexité cognitive visée: ≤ 8
"""
from pathlib import Path
from typing import Optional
import pandas as pd
import glob
import os

from ...utils.column_mappings import (
    get_users_mapping, get_users_column_order,
    get_groups_mapping, get_groups_column_order, 
    get_projects_mapping, get_projects_column_order
)

# Import de la référence officielle des colonnes
from ...utils.column_mappings import (
    USERS_COLUMN_MAPPING, 
    USERS_COLUMN_ORDER,
    get_users_mapping,
    get_users_column_order
)


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
    
    def clean_old_exports(self):
        """Supprime tous les anciens fichiers Excel pour avoir toujours la dernière version"""
        xlsx_files = glob.glob(str(self.export_dir / "*.xlsx"))
        for file in xlsx_files:
            try:
                os.remove(file)
                print(f"🗑️ Ancien fichier supprimé: {Path(file).name}")
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {Path(file).name}: {e}")
    
    def export_users(self, df_users: pd.DataFrame, clean_first: bool = False) -> str:
        """Exporte les utilisateurs - VERSION SIMPLE (SANS TIMESTAMP)"""
        # Nettoyer les anciens exports seulement si demandé
        if clean_first:
            self.clean_old_exports()
        
        # NOM FIXE sans timestamp pour structure current/previous/archive
        filename = self.export_dir / "gitlab_users.xlsx"
        
        if df_users.empty:
            # Créer un fichier vide avec en-têtes pour Power BI (RÉFÉRENCE OFFICIELLE)
            empty_df = pd.DataFrame(columns=get_users_column_order())
            empty_df.to_excel(filename, sheet_name="Gitlab Users", index=False)
            print(f"⚠️ Aucun utilisateur trouvé - fichier vide créé → {filename.name}")
            return str(filename)
        
        # Mapping des colonnes selon la RÉFÉRENCE OFFICIELLE
        column_mapping = get_users_mapping()
        
        # Renommer les colonnes pour Power BI
        df_export = df_users.rename(columns=column_mapping)
        
        # Réordonner les colonnes selon la spécification OFFICIELLE
        column_order = get_users_column_order()
        df_export = df_export[column_order]
        
        # Export basique - Power BI fait le reste
        df_export.to_excel(filename, sheet_name="Gitlab Users", index=False)
        
        print(f"✅ {len(df_users)} utilisateurs → {filename.name}")
        return str(filename)
    
    def export_groups(self, df_groups: pd.DataFrame, clean_first: bool = False) -> str:
        """Exporte les groupes - VERSION SIMPLE (SANS TIMESTAMP)"""
        # Nettoyer les anciens exports seulement si demandé
        if clean_first:
            self.clean_old_exports()
        
        # NOM FIXE sans timestamp pour structure current/previous/archive
        filename = self.export_dir / "gitlab_groups.xlsx"
        
        if df_groups.empty:
            # Créer un fichier vide avec en-têtes Power BI (RÉFÉRENCE CENTRALISÉE)
            empty_df = pd.DataFrame(columns=get_groups_column_order())
            empty_df.to_excel(filename, sheet_name="Gitlab Groups", index=False)
            print(f"⚠️ Aucun groupe trouvé - fichier vide créé → {filename.name}")
            return str(filename)
        
        # Mapper les colonnes selon la RÉFÉRENCE OFFICIELLE
        column_mapping = get_groups_mapping()
        df_export = df_groups.rename(columns=column_mapping)
        df_export = df_export[get_groups_column_order()]
        
        # Export Power BI
        df_export.to_excel(filename, sheet_name="Gitlab Groups", index=False)
        
        print(f"✅ {len(df_groups)} groupes → {filename.name}")
        return str(filename)
    
    def export_projects(self, df_projects: pd.DataFrame, project_type: str = "projects", clean_first: bool = False) -> str:
        """Exporte les projets - VERSION SIMPLE (SANS TIMESTAMP)"""
        # Nettoyer les anciens exports seulement si demandé
        if clean_first:
            self.clean_old_exports()
        
        # NOM FIXE sans timestamp pour structure current/previous/archive
        filename = self.export_dir / f"gitlab_{project_type}.xlsx"
        
        # Noms de feuilles fixes selon la spécification
        if "active" in project_type.lower():
            sheet_name = "Gitlab Active Projects"
        elif "archived" in project_type.lower():
            sheet_name = "Gitlab Archived Projects"
        else:
            sheet_name = "Gitlab Projects"
        
        if df_projects.empty:
            # Créer un fichier vide avec en-têtes Power BI (RÉFÉRENCE CENTRALISÉE)
            empty_df = pd.DataFrame(columns=get_projects_column_order())
            empty_df.to_excel(filename, sheet_name=sheet_name, index=False)
            print(f"⚠️ Aucun projet {project_type} trouvé - fichier vide créé → {filename.name}")
            return str(filename)
        
        # Mapper les colonnes selon la RÉFÉRENCE OFFICIELLE
        column_mapping = get_projects_mapping()
        df_export = df_projects.rename(columns=column_mapping)
        df_export = df_export[get_projects_column_order()]
        
        # Export Power BI
        df_export.to_excel(filename, sheet_name=sheet_name, index=False)
        
        print(f"✅ {len(df_projects)} projets {project_type} → {filename.name}")
        return str(filename)
    
    def export_events(self, df_events: pd.DataFrame, clean_first: bool = False) -> str:
        """Exporte les événements avec mapping Power BI (SANS TIMESTAMP)"""
        if df_events.empty:
            print("⚠️ Aucun événement à exporter")
            return ""
        
        # Nettoyer les anciens exports seulement si demandé
        if clean_first:
            self.clean_old_exports()
        
        # NOM FIXE sans timestamp pour structure current/previous/archive
        filename = self.export_dir / "gitlab_events.xlsx"
        
        # Appliquer le mapping Power BI
        from kenobi_tools.utils.column_mappings import get_events_mapping, get_events_column_order
        mapping = get_events_mapping()
        df_export = df_events.rename(columns=mapping)
        
        # Réorganiser les colonnes dans l'ordre validé
        column_order = get_events_column_order()
        df_export = df_export.reindex(columns=column_order)
        
        # Export avec nom d'onglet Power BI
        df_export.to_excel(filename, sheet_name="Gitlab Events", index=False)
        
        print(f"✅ {len(df_events)} événements → {filename.name}")
        return str(filename)


# Version encore plus simple pour usage direct
def quick_export_to_excel(df: pd.DataFrame, filename: str) -> str:
    """Export ultra-rapide pour Power BI"""
    if df.empty:
        return ""
    
    df.to_excel(filename, index=False)
    return filename
