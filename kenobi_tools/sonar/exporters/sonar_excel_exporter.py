"""
📊 Exporteur Excel SonarQube - Projets
Responsable de l'export des données SonarQube vers Excel format Power BI
Architecture cohérente avec les exporteurs GitLab
"""

from pathlib import Path
import pandas as pd


# Mapping colonnes techniques → Power BI pour les projets SonarQube
PROJECTS_COLUMN_MAPPING = {
    'cle_projet': 'Clé Projet',
    'nom_projet': 'Nom Projet', 
    'date_derniere_analyse': 'Dernière Analyse',
    'quality_gate_statut': 'Quality Gate'
}

# Ordre des colonnes dans Excel (Power BI ready)
PROJECTS_COLUMN_ORDER = [
    'Clé Projet',
    'Nom Projet',
    'Quality Gate',
    'Dernière Analyse'
]


def export_projects_to_excel(df: pd.DataFrame) -> str:
    """
    Exporte les projets SonarQube vers Excel format Power BI
    
    Args:
        df: DataFrame avec les projets SonarQube
        
    Returns:
        str: Chemin complet du fichier Excel généré ou chaîne vide si erreur
    """
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
