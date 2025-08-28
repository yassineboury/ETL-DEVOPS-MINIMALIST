"""
📊 Exporteur Excel SonarQube COMPLET
Export de TOUTES les métriques SonarQube vers Excel format Power BI
Version unifiée pour analyse complète de la qualité de code
"""

from pathlib import Path
import pandas as pd


def export_complete_to_excel(df: pd.DataFrame) -> str:
    """
    Exporte les projets SonarQube COMPLETS vers Excel format Power BI
    
    Args:
        df: DataFrame avec tous les projets + toutes métriques
        
    Returns:
        str: Chemin complet du fichier Excel généré ou chaîne vide si erreur
    """
    try:
        if df.empty:
            print("⚠️ DataFrame vide - pas d'export complet")
            return ""
            
        print(f"📊 Préparation export COMPLET de {len(df)} projets...")
        print(f"📈 {len(df.columns)} métriques par projet")
        
        # Créer le répertoire d'export
        exports_dir = Path("exports/sonar")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Nom de fichier unifié
        filename = exports_dir / "sonar_projects.xlsx"
        
        # Réorganiser les colonnes (colonnes principales en premier)
        priority_columns = [
            'cle_projet', 'nom_projet', 'date_derniere_analyse', 'Quality Gate',
            'Lignes Code', 'Bugs', 'Vulnérabilités', 'Code Smells',
            'Couverture Tests %', 'Densité Duplication %', 
            'Rating Fiabilité', 'Rating Sécurité', 'Rating Maintenabilité'
        ]
        
        # Colonnes disponibles dans l'ordre de priorité
        ordered_columns = []
        for col in priority_columns:
            if col in df.columns:
                ordered_columns.append(col)
        
        # Ajouter les autres colonnes restantes
        remaining_columns = [col for col in df.columns if col not in ordered_columns]
        final_columns = ordered_columns + sorted(remaining_columns)
        
        # Réorganiser le DataFrame
        df_export = df[final_columns]
        
        # Export vers Excel avec formatage Power BI
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_export.to_excel(
                writer, 
                sheet_name='Sonar Projects Complete', 
                index=False,
                freeze_panes=(1, 0)  # Figer la première ligne
            )
            
            # Récupération de la feuille pour ajustements
            worksheet = writer.sheets['Sonar Projects Complete']
            
            # Auto-ajustement des largeurs (limité pour éviter des colonnes trop larges)
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value or '')) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 30)
        
        file_path = str(filename.absolute())
        print(f"✅ Export complet: {file_path}")
        
        # Résumé de l'export
        _print_complete_export_summary(df_export)
        
        return file_path
        
    except Exception as e:
        print(f"❌ Erreur export complet vers Excel: {e}")
        return ""


def _print_complete_export_summary(df: pd.DataFrame):
    """
    Affiche un résumé détaillé de l'export complet
    
    Args:
        df: DataFrame exporté
    """
    try:
        print(f"\n📋 RÉSUMÉ EXPORT SONARQUBE COMPLET")
        print(f"   • Total projets: {len(df)}")
        print(f"   • Total métriques: {len(df.columns)}")
        
        # Quality Gates
        if 'Quality Gate' in df.columns:
            qg_stats = df['Quality Gate'].value_counts()
            print(f"   • Quality Gates:")
            for status, count in qg_stats.items():
                print(f"     - {status}: {count}")
        
        # Projets avec bugs
        if 'Bugs' in df.columns:
            bugs_stats = df['Bugs'].describe()
            print(f"   • Bugs (stats):")
            print(f"     - Moyenne: {bugs_stats['mean']:.1f}")
            print(f"     - Maximum: {bugs_stats['max']:.0f}")
            
        # Couverture de tests
        if 'Couverture Tests %' in df.columns:
            coverage_stats = df['Couverture Tests %'].describe()
            print(f"   • Couverture Tests (stats):")
            print(f"     - Moyenne: {coverage_stats['mean']:.1f}%")
            print(f"     - Minimum: {coverage_stats['min']:.1f}%")
            
        # Projets par taille (lignes de code)
        if 'Lignes Code' in df.columns:
            ncloc_stats = df['Lignes Code'].describe()
            print(f"   • Lignes de Code (stats):")
            print(f"     - Total: {df['Lignes Code'].sum():.0f}")
            print(f"     - Moyenne/projet: {ncloc_stats['mean']:.0f}")
            print(f"     - Plus gros projet: {ncloc_stats['max']:.0f}")
        
        # Top 5 des projets les plus critiques (le plus de bugs + vulnérabilités)
        if 'Bugs' in df.columns and 'Vulnérabilités' in df.columns:
            df_issues = df.copy()
            df_issues['Total Issues'] = (df_issues['Bugs'].fillna(0) + 
                                       df_issues['Vulnérabilités'].fillna(0))
            top_issues = df_issues.nlargest(5, 'Total Issues')[['nom_projet', 'Total Issues']]
            
            print(f"   • Top 5 projets critiques:")
            for _, row in top_issues.iterrows():
                print(f"     - {row['nom_projet']}: {row['Total Issues']:.0f} issues")
        
        print("📁 Toutes les métriques SonarQube prêtes pour Power BI")
        
    except Exception as e:
        print(f"⚠️ Erreur génération résumé complet: {e}")
