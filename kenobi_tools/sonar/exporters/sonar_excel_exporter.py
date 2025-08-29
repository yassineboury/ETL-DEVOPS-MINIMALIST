"""
Exporteur Excel SonarQube - VERSION ALIGNÉE GITLAB
Responsable de l'export des données SonarQube vers Excel format Power BI
Architecture cohérente avec les exporteurs GitLab
"""
from pathlib import Path
from typing import Optional
import pandas as pd
import glob
import os

# 🏷️ MAPPINGS COLONNES SONARQUBE POUR POWER BI
PROJECTS_COLUMN_MAPPING = {
    # Colonnes de base
    'cle_projet': 'Clé Projet',
    'nom_projet': 'Nom Projet', 
    'date_derniere_analyse': 'Date Dernière Analyse',
    'date_analyse_iso': 'Date Analyse ISO',
    'quality_gate_statut': 'Quality Gate',
    
    # Métriques de défauts
    'bugs': 'Bugs',
    'vulnerabilities': 'Vulnérabilités',
    'code_smells': 'Code Smells',
    'security_hotspots': 'Security Hotspots',
    
    # Métriques de qualité
    'coverage': 'Couverture (%)',
    'duplicated_lines_density': 'Duplication (%)',
    'ncloc': 'Lignes de Code',
    'sqale_index': 'Dette Technique (min)',
    
    # Notes (ratings)
    'reliability_rating': 'Note Fiabilité',
    'security_rating': 'Note Sécurité',
    'sqale_rating': 'Note Maintenabilité',
    'alert_status': 'Alert Status',
    
    # Tendances nouveau code
    'new_bugs': 'Nouveaux Bugs',
    'new_vulnerabilities': 'Nouvelles Vulnérabilités',
    'new_code_smells': 'Nouveaux Code Smells',
    'new_coverage': 'Nouvelle Couverture (%)'
}

# 📋 ORDRE DES COLONNES POWER BI
PROJECTS_COLUMN_ORDER = [
    'Clé Projet', 'Nom Projet', 'Date Dernière Analyse', 'Date Analyse ISO', 'Quality Gate',
    'Bugs', 'Vulnérabilités', 'Code Smells', 'Security Hotspots',
    'Couverture (%)', 'Duplication (%)', 'Lignes de Code', 'Dette Technique (min)',
    'Note Fiabilité', 'Note Sécurité', 'Note Maintenabilité', 'Alert Status',
    'Nouveaux Bugs', 'Nouvelles Vulnérabilités', 'Nouveaux Code Smells', 'Nouvelle Couverture (%)'
]


class SonarExcelExporter:
    """Exporteur Excel minimaliste pour Power BI - SonarQube"""
    
    def __init__(self, export_dir: Optional[Path] = None):
        """Initialise l'exporteur SonarQube"""
        if export_dir is None:
            current_dir = Path(__file__).parent.parent.parent.parent
            self.export_dir = current_dir / "exports" / "sonar"
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
    
    def export_projects_to_excel(self, df: pd.DataFrame, clean_first: bool = False) -> str:
        """
        Exporte les projets SonarQube vers Excel format Power BI - VERSION GITLAB
        
        Args:
            df: DataFrame avec les projets SonarQube
            clean_first: Nettoyer les anciens fichiers avant export
            
        Returns:
            str: Chemin complet du fichier Excel généré ou chaîne vide si erreur
        """
        try:
            # Nettoyer les anciens exports si demandé
            if clean_first:
                self.clean_old_exports()
            
            # Format GitLab : nom sans timestamp
            filename = self.export_dir / "sonar_projects.xlsx"
            
            if df.empty:
                print("⚠️ DataFrame vide - pas d'export projets")
                return ""
            
            print(f"📊 Export de {len(df)} projets SonarQube...")
            
            # 🏷️ APPLIQUER LE MAPPING COLONNES POWER BI (comme GitLab)
            df_export = df.rename(columns=PROJECTS_COLUMN_MAPPING)
            
            # 📋 Réorganiser selon l'ordre Power BI
            available_columns = [col for col in PROJECTS_COLUMN_ORDER if col in df_export.columns]
            df_export = df_export[available_columns]
            
            print(f"📋 Colonnes Power BI appliquées: {len(df_export.columns)}")
            
            # Export vers Excel avec convention GitLab
            df_export.to_excel(
                filename,
                sheet_name='Sonar Projects',  # Convention GitLab
                index=False,
                freeze_panes=(1, 0)  # Figer la première ligne
            )
            
            file_path = str(filename.absolute())
            print(f"✅ {len(df)} projets → {filename.name}")
            
            # Résumé de l'export
            self._print_export_summary(df)
            
            return file_path
            
        except Exception as e:
            print(f"❌ Erreur export projets vers Excel: {e}")
            return ""
    
    def _print_export_summary(self, df: pd.DataFrame):
        """Affiche un résumé de l'export des projets"""
        try:
            print(f"\n📋 RÉSUMÉ EXPORT PROJETS SONARQUBE")
            print(f"   • Total projets: {len(df)}")
            
            # Répartition par Quality Gate
            if 'Quality Gate' in df.columns:
                qg_stats = df['Quality Gate'].value_counts()
                print(f"   • Quality Gates:")
                for status, count in qg_stats.items():
                    print(f"     - {status}: {count}")
                    
            # Métriques de base
            if 'Lignes de Code' in df.columns:
                total_lines = df['Lignes de Code'].sum()
                print(f"   • Total lignes de code: {total_lines:,}")
            
            if 'Bugs' in df.columns:
                total_bugs = df['Bugs'].sum()
                print(f"   • Total bugs: {total_bugs:,}")
                    
            print("📁 Données prêtes pour Power BI")
            
        except Exception as e:
            print(f"⚠️ Erreur génération résumé: {e}")


# Fonction de compatibilité (legacy)
def export_projects_to_excel(df: pd.DataFrame) -> str:
    """Fonction legacy - utilise la classe SonarExcelExporter avec mapping complet"""
    exporter = SonarExcelExporter()
    return exporter.export_projects_to_excel(df, clean_first=True)
    try:
        if df.empty:
            print("⚠️ DataFrame vide - pas d'export projets")
            return ""
            
        print(f"📊 Préparation export de {len(df)} projets...")
        
        # Créer le répertoire d'export s'il n'existe pas
        exports_dir = Path("exports/sonar")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Renommer les colonnes pour Power BI
        df_export = df.rename(columns=PROJECTS_COLUMN_MAPPING)
        
        # Réorganiser les colonnes dans l'ordre Power BI
        available_columns = [col for col in PROJECTS_COLUMN_ORDER if col in df_export.columns]
        df_export = df_export[available_columns]
        
        # Génération du nom de fichier (format cohérent avec GitLab)
        filename = exports_dir / "sonar_projects.xlsx"
        
        # Export vers Excel avec formatage Power BI
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_export.to_excel(
                writer, 
                sheet_name='Sonar Projects', 
                index=False,
                freeze_panes=(1, 0)  # Figer la première ligne (en-têtes)
            )
            
            # Récupération de la feuille pour ajustements
            worksheet = writer.sheets['Sonar Projects']
            
            # Auto-ajustement des largeurs de colonnes
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value or '')) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 50)
        
        file_path = str(filename.absolute())
        print(f"✅ Projets exportés: {file_path}")
        
        # Résumé de l'export
        _print_export_summary(df_export)
        
        return file_path
        
    except Exception as e:
        print(f"❌ Erreur export projets vers Excel: {e}")
        return ""


def _print_export_summary(df: pd.DataFrame):
    """
    Affiche un résumé de l'export des projets
    
    Args:
        df: DataFrame exporté
    """
    try:
        print(f"\n📋 RÉSUMÉ EXPORT PROJETS SONARQUBE")
        print(f"   • Total projets: {len(df)}")
        
        # Répartition par Quality Gate
        if 'Quality Gate' in df.columns:
            qg_stats = df['Quality Gate'].value_counts()
            print(f"   • Quality Gates:")
            for status, count in qg_stats.items():
                print(f"     - {status}: {count}")
                
        # Projets avec/sans analyse récente
        if 'Dernière Analyse' in df.columns:
            analyzed_count = df['Dernière Analyse'].notna().sum()
            not_analyzed_count = len(df) - analyzed_count
            print(f"   • Analyses:")
            print(f"     - Projets analysés: {analyzed_count}")
            print(f"     - Sans analyse récente: {not_analyzed_count}")
                
        print("📁 Données prêtes pour Power BI")
        
    except Exception as e:
        print(f"⚠️ Erreur génération résumé: {e}")
