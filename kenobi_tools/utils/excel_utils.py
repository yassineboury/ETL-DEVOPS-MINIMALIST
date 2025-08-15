"""
Utilitaires Excel simplifiés - VERSION REFACTORISÉE
Module centralisé pour l'export Excel avec complexité réduite
"""

import os
from datetime import datetime
from typing import Optional

import pandas as pd
from openpyxl.utils import get_column_letter

from .constants import EXPORTS_GITLAB_PATH


class ExcelExporter:
    """Exporteur Excel simplifié"""
    
    @staticmethod
    def export_dataframe_to_excel_light(
        df: pd.DataFrame,
        filename: str,
        sheet_name: str = "Data",
        enable_autofilter: bool = True,
        freeze_first_row: bool = True
    ) -> str:
        """
        Export simplifié d'un DataFrame vers Excel
        
        Args:
            df: DataFrame à exporter
            filename: Nom du fichier de sortie
            sheet_name: Nom de la feuille Excel
            enable_autofilter: Activer le filtre automatique
            freeze_first_row: Figer la première ligne
            
        Returns:
            Chemin du fichier créé ou chaîne vide en cas d'erreur
        """
        if df.empty:
            print("⚠️ DataFrame vide, pas d'export")
            return ""
        
        try:
            # Créer le répertoire de sortie
            output_path = ExcelExporter._ensure_output_directory(filename)
            
            # Export vers Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Formatage basique
                worksheet = writer.sheets[sheet_name]
                ExcelExporter._apply_basic_formatting(
                    worksheet, enable_autofilter, freeze_first_row
                )
            
            print(f"✅ Excel exporté: {os.path.basename(output_path)}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur export Excel: {e}")
            return ""
    
    @staticmethod
    def _ensure_output_directory(filename: str) -> str:
        """S'assure que le répertoire de sortie existe"""
        if os.path.isabs(filename):
            output_path = filename
        else:
            # Utiliser le répertoire d'export par défaut
            export_dir = EXPORTS_GITLAB_PATH
            os.makedirs(export_dir, exist_ok=True)
            output_path = os.path.join(export_dir, filename)
        
        # Créer le répertoire parent si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return output_path
    
    @staticmethod
    def _apply_basic_formatting(worksheet, enable_autofilter: bool, freeze_first_row: bool):
        """Applique le formatage de base à la feuille Excel"""
        if not worksheet or worksheet.max_row <= 1:
            return
        
        try:
            # Filtre automatique
            if enable_autofilter:
                max_col_letter = get_column_letter(worksheet.max_column)
                worksheet.auto_filter.ref = f"A1:{max_col_letter}{worksheet.max_row}"
            
            # Figer la première ligne
            if freeze_first_row:
                worksheet.freeze_panes = "A2"
                
        except Exception as e:
            print(f"⚠️ Erreur formatage Excel: {e}")


# Fonctions de compatibilité avec l'ancienne API
def export_dataframe_to_excel_light(
    df: pd.DataFrame,
    filename: str,
    sheet_name: str = "Data",
    enable_autofilter: bool = True,
    freeze_first_row: bool = True
) -> str:
    """Fonction de compatibilité pour l'export Excel léger"""
    return ExcelExporter.export_dataframe_to_excel_light(
        df, filename, sheet_name, enable_autofilter, freeze_first_row
    )


def generate_timestamp_filename(base_name: str, extension: str = "xlsx") -> str:
    """Génère un nom de fichier avec timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


def ensure_exports_directory() -> str:
    """S'assure que le répertoire d'exports existe"""
    os.makedirs(EXPORTS_GITLAB_PATH, exist_ok=True)
    return EXPORTS_GITLAB_PATH
