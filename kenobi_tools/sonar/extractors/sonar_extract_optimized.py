"""
📊 Extracteur SonarQube OPTIMISÉ - Version corrigée avec structure validée
Extraction complète des projets avec toutes les métriques validées + champs dates
Architecture simplifiée et debuggée pour récupération réelle des métriques
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

# Ajouter le projet au path pour les imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from kenobi_tools.sonar.client.sonar_client import SonarClient


# 🎯 MÉTRIQUES SONARQUBE OPTIMISÉES (structure validée)
SONAR_METRICS_OPTIMIZED = {
    # 📏 TAILLE & STRUCTURE (7 métriques)
    'ncloc': 'Lignes Code',
    'lines': 'Lignes Totales',
    'files': 'Fichiers',
    'directories': 'Répertoires', 
    'classes': 'Classes',
    'functions': 'Fonctions',
    'statements': 'Instructions',
    
    # 🧠 COMPLEXITÉ (5 métriques)
    'complexity': 'Complexité Total',
    'cognitive_complexity': 'Complexité Cognitive',
    'complexity_in_classes': 'Complexité Classes',
    'complexity_in_functions': 'Complexité Fonctions',
    'comment_lines_density': 'Densité Commentaires %',
    
    # 🔄 DUPLICATION (4 métriques)
    'duplicated_lines': 'Lignes Dupliquées',
    'duplicated_blocks': 'Blocs Dupliqués', 
    'duplicated_files': 'Fichiers Dupliqués',
    'duplicated_lines_density': 'Densité Duplication %',
    
    # 🧪 COUVERTURE TESTS (7 métriques)
    'coverage': 'Couverture %',
    'line_coverage': 'Couverture Lignes %',
    'branch_coverage': 'Couverture Branches %',
    'lines_to_cover': 'Lignes à Couvrir',
    'uncovered_lines': 'Lignes Non Couvertes',
    'conditions_to_cover': 'Conditions à Couvrir', 
    'uncovered_conditions': 'Conditions Non Couvertes',
    
    # 🎯 EXÉCUTION TESTS (5 métriques)
    'tests': 'Nombre Tests',
    'test_success_density': 'Succès Tests %',
    'test_failures': 'Échecs Tests',
    'test_errors': 'Erreurs Tests',
    'skipped_tests': 'Tests Ignorés',
    
    # 🐛 FIABILITÉ (3 métriques)
    'bugs': 'Bugs',
    'reliability_rating': 'Rating Fiabilité',
    'reliability_remediation_effort': 'Effort Bugs (min)',
    
    # 🔒 SÉCURITÉ (6 métriques)
    'vulnerabilities': 'Vulnérabilités',
    'security_rating': 'Rating Sécurité', 
    'security_remediation_effort': 'Effort Sécurité (min)',
    'security_hotspots': 'Points Chauds',
    'security_hotspots_reviewed': 'Points Chauds Revus',
    'security_review_rating': 'Rating Revue Sécurité',
    
    # 🧹 MAINTENABILITÉ (5 métriques)
    'code_smells': 'Code Smells',
    'maintainability_rating': 'Rating Maintenabilité',
    'technical_debt': 'Dette Technique (min)',
    'sqale_debt_ratio': 'Ratio Dette %',
    'development_cost': 'Coût Développement (min)',
    
    # 📊 ÉVOLUTION (4 métriques nouvelles)
    'new_lines': 'Nouvelles Lignes',
    'new_coverage': 'Nouvelle Couverture %',
    'new_bugs': 'Nouveaux Bugs',
    'new_code_smells': 'Nouveaux Code Smells'
}

# 📅 CHAMPS DATES
SONAR_DATE_FIELDS = {
    'export_date': 'Date Export',
    'createdAt': 'Date Création Projet',
    'lastAnalysisDate': 'Dernière Analyse',
    'analysedAt': 'Date Quality Gate'
}


def extract_sonar_projects_optimized(client_session) -> pd.DataFrame:
    """
    Extrait TOUS les projets SonarQube avec métriques optimisées + dates
    Version corrigée avec debug et gestion d'erreurs améliorée
    
    Args:
        client_session: Session requests authentifiée SonarQube
        
    Returns:
        pd.DataFrame: DataFrame optimisé avec projets + métriques + dates
    """
    try:
        print("📊 EXTRACTION SONARQUBE OPTIMISÉE")
        print("=" * 50)
        
        # Initialiser le client
        temp_client = SonarClient()
        temp_client.session = client_session
        temp_client.url = client_session.headers.get('base_url', 'https://sonar.oncf.net')
        
        print(f"🔗 URL SonarQube: {temp_client.url}")
        
        # 1️⃣ RÉCUPÉRATION DE TOUS LES PROJETS
        all_projects = _get_all_projects(client_session, temp_client.url)
        
        if not all_projects:
            print("❌ Aucun projet trouvé")
            return pd.DataFrame()
            
        print(f"📁 {len(all_projects)} projets trouvés")
        
        # 2️⃣ ENRICHISSEMENT AVEC MÉTRIQUES ET DATES
        print("\n📈 Enrichissement avec métriques et dates...")
        enriched_projects = []
        
        for i, project in enumerate(all_projects, 1):
            project_key = project.get('key', '')
            project_name = project.get('name', '')
            
            print(f"🔍 {i:3}/{len(all_projects)} | {project_name[:50]}")
            
            # Structure de base avec dates
            project_data = _build_base_project_data(project)
            
            # Enrichissement avec métriques
            metrics_data = _get_project_metrics_optimized(client_session, temp_client.url, project_key)
            project_data.update(metrics_data)
            
            # Quality Gate séparé
            qg_data = _get_project_quality_gate(client_session, temp_client.url, project_key)
            project_data.update(qg_data)
            
            enriched_projects.append(project_data)
            
        # 3️⃣ CONVERSION EN DATAFRAME
        df = pd.DataFrame(enriched_projects)
        
        print(f"\n✅ EXTRACTION TERMINÉE")
        print(f"   📊 {len(df)} projets extraits")
        print(f"   📈 {len(df.columns)} colonnes de données")
        print(f"   🎯 {len(SONAR_METRICS_OPTIMIZED)} métriques configurées")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction optimisée: {e}")
        import traceback
        print(f"📍 Stack trace: {traceback.format_exc()}")
        return pd.DataFrame()


def _get_all_projects(session, base_url: str) -> List[Dict[str, Any]]:
    """
    Récupère tous les projets SonarQube avec pagination
    
    Args:
        session: Session requests authentifiée
        base_url: URL de base SonarQube
        
    Returns:
        List[Dict]: Liste complète des projets
    """
    try:
        all_projects = []
        page = 1
        page_size = 100
        
        while True:
            print(f"📄 Page {page}...")
            
            response = session.get(
                f"{base_url}/api/projects/search",
                params={
                    'ps': page_size,
                    'p': page,
                    'qualifiers': 'TRK'
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur API projets page {page}: {response.status_code}")
                print(f"   Réponse: {response.text[:200]}")
                break
                
            data = response.json()
            projects = data.get('components', [])
            
            if not projects:
                break
                
            print(f"   ✅ {len(projects)} projets récupérés")
            all_projects.extend(projects)
            
            # Vérifier si on a tout récupéré
            paging = data.get('paging', {})
            total = paging.get('total', 0)
            if len(all_projects) >= total:
                print(f"   📊 Total final: {len(all_projects)}/{total} projets")
                break
                
            page += 1
            
        return all_projects
        
    except Exception as e:
        print(f"❌ Erreur récupération projets: {e}")
        return []


def _build_base_project_data(project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construit les données de base du projet avec dates formatées
    
    Args:
        project: Données brutes du projet SonarQube
        
    Returns:
        dict: Données de base avec dates
    """
    try:
        # Date d'export (maintenant)
        export_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Date de création projet
        created_at = project.get('createdAt')
        creation_date = _format_sonar_date(created_at) if created_at else None
        
        # Date de dernière analyse
        last_analysis = project.get('lastAnalysisDate')
        analysis_date = _format_sonar_date(last_analysis) if last_analysis else None
        
        return {
            # Identification
            'Clé Projet': project.get('key', ''),
            'Nom Projet': project.get('name', ''),
            
            # Dates (4 champs)
            'Date Export': export_date,
            'Date Création Projet': creation_date,
            'Dernière Analyse': analysis_date,
            'Date Quality Gate': None,  # Sera rempli par _get_project_quality_gate
            
            # Quality Gate (sera rempli séparément)
            'Quality Gate Status': 'UNKNOWN'
        }
        
    except Exception as e:
        print(f"⚠️ Erreur construction données base: {e}")
        return {
            'Clé Projet': project.get('key', ''),
            'Nom Projet': project.get('name', ''),
            'Date Export': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'Date Création Projet': None,
            'Dernière Analyse': None,
            'Date Quality Gate': None,
            'Quality Gate Status': 'ERROR'
        }


def _get_project_metrics_optimized(session, base_url: str, project_key: str) -> Dict[str, Any]:
    """
    Récupère TOUTES les métriques optimisées pour un projet
    Version corrigée avec gestion d'erreurs et batching
    
    Args:
        session: Session requests authentifiée
        base_url: URL de base SonarQube
        project_key: Clé du projet
        
    Returns:
        dict: Métriques du projet avec noms Excel
    """
    try:
        # Initialiser toutes les métriques à None
        metrics_values = {}
        for metric_key, excel_name in SONAR_METRICS_OPTIMIZED.items():
            metrics_values[excel_name] = None
        
        # Récupération par batch (API SonarQube limite à ~50 métriques/requête)
        all_metric_keys = list(SONAR_METRICS_OPTIMIZED.keys())
        batch_size = 25  # Taille conservative
        
        print(f"      📊 Récupération {len(all_metric_keys)} métriques par batch de {batch_size}")
        
        for i in range(0, len(all_metric_keys), batch_size):
            batch_keys = all_metric_keys[i:i + batch_size]
            batch_param = ','.join(batch_keys)
            
            print(f"         Batch {i//batch_size + 1}: {len(batch_keys)} métriques")
            
            try:
                response = session.get(
                    f"{base_url}/api/measures/component",
                    params={
                        'component': project_key,
                        'metricKeys': batch_param
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    component = data.get('component', {})
                    measures = component.get('measures', [])
                    
                    print(f"         ✅ {len(measures)} métriques récupérées")
                    
                    # Traitement des mesures
                    for measure in measures:
                        metric_key = measure.get('metric', '')
                        if metric_key in SONAR_METRICS_OPTIMIZED:
                            excel_name = SONAR_METRICS_OPTIMIZED[metric_key]
                            raw_value = measure.get('value', '')
                            processed_value = _process_metric_value_optimized(metric_key, raw_value)
                            metrics_values[excel_name] = processed_value
                            
                elif response.status_code == 404:
                    print(f"         ⚠️ Métriques non disponibles pour batch {i//batch_size + 1}")
                    continue  # Continuer avec le batch suivant
                else:
                    print(f"         ⚠️ Erreur batch {i//batch_size + 1}: {response.status_code}")
                    
            except Exception as e:
                print(f"         ❌ Exception batch {i//batch_size + 1}: {e}")
                continue
        
        return metrics_values
        
    except Exception as e:
        print(f"      ❌ Erreur métriques {project_key}: {e}")
        # Retourner dict avec toutes les métriques à None
        return {excel_name: None for excel_name in SONAR_METRICS_OPTIMIZED.values()}


def _get_project_quality_gate(session, base_url: str, project_key: str) -> Dict[str, Any]:
    """
    Récupère le Quality Gate d'un projet avec sa date
    
    Args:
        session: Session requests authentifiée
        base_url: URL de base SonarQube
        project_key: Clé du projet
        
    Returns:
        dict: Quality Gate status et date
    """
    try:
        response = session.get(
            f"{base_url}/api/qualitygates/project_status",
            params={'projectKey': project_key},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            project_status = data.get('projectStatus', {})
            
            status = project_status.get('status', 'UNKNOWN')
            analysed_at = project_status.get('analysedAt')
            qg_date = _format_sonar_date(analysed_at) if analysed_at else None
            
            return {
                'Quality Gate Status': status,
                'Date Quality Gate': qg_date
            }
        else:
            print(f"      ⚠️ Quality Gate non accessible: {response.status_code}")
            
    except Exception as e:
        print(f"      ⚠️ Erreur Quality Gate: {e}")
        
    return {
        'Quality Gate Status': 'UNKNOWN',
        'Date Quality Gate': None
    }


def _process_metric_value_optimized(metric_key: str, value: str) -> Any:
    """
    Traite et convertit une valeur de métrique selon son type (version optimisée)
    
    Args:
        metric_key: Clé de la métrique SonarQube
        value: Valeur brute de l'API
        
    Returns:
        Any: Valeur convertie (int, float, str) ou None
    """
    try:
        if not value or value == '':
            return None
            
        # Métriques entières
        integer_metrics = {
            'ncloc', 'lines', 'files', 'directories', 'classes', 'functions', 'statements',
            'complexity', 'cognitive_complexity', 'complexity_in_classes', 'complexity_in_functions',
            'duplicated_lines', 'duplicated_blocks', 'duplicated_files',
            'lines_to_cover', 'uncovered_lines', 'conditions_to_cover', 'uncovered_conditions',
            'tests', 'test_failures', 'test_errors', 'skipped_tests',
            'bugs', 'reliability_remediation_effort',
            'vulnerabilities', 'security_remediation_effort', 'security_hotspots', 'security_hotspots_reviewed',
            'code_smells', 'technical_debt', 'development_cost',
            'new_lines', 'new_bugs', 'new_code_smells'
        }
        
        # Métriques pourcentages
        percentage_metrics = {
            'comment_lines_density', 'duplicated_lines_density',
            'coverage', 'line_coverage', 'branch_coverage', 'test_success_density',
            'sqale_debt_ratio', 'new_coverage'
        }
        
        # Métriques ratings (A-E)
        rating_metrics = {
            'reliability_rating', 'security_rating', 'maintainability_rating', 'security_review_rating'
        }
        
        if metric_key in integer_metrics:
            return int(float(value))
        elif metric_key in percentage_metrics:
            return round(float(value), 2)
        elif metric_key in rating_metrics:
            # Formater les ratings de façon lisible
            rating_map = {'1': 'A (1)', '2': 'B (2)', '3': 'C (3)', '4': 'D (4)', '5': 'E (5)'}
            return rating_map.get(str(value), f"Rating {value}")
        else:
            return str(value)
            
    except Exception:
        return value  # Retourner la valeur brute si conversion échoue


def _format_sonar_date(iso_date: str) -> Optional[str]:
    """
    Convertit une date ISO SonarQube en format français
    
    Args:
        iso_date: Date au format ISO (ex: 2025-08-29T14:30:25+0200)
        
    Returns:
        str: Date au format français ou None
    """
    try:
        if iso_date:
            # Gérer les différents formats de date SonarQube
            clean_date = iso_date.replace('Z', '+00:00')
            dt = datetime.fromisoformat(clean_date)
            return dt.strftime('%d/%m/%Y %H:%M:%S')
    except Exception:
        pass
    return None


def extract_and_export_sonar_optimized() -> str:
    """
    Point d'entrée principal pour l'extraction optimisée
    
    Returns:
        str: Chemin du fichier Excel généré ou chaîne vide si erreur
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        print("🎯 LANCEMENT EXTRACTION SONARQUBE OPTIMISÉE")
        
        # Connexion SonarQube
        client = SonarClient()
        session = client.connect()
        
        if not session:
            print("❌ Impossible de se connecter à SonarQube")
            return ""
            
        # Enrichir la session avec l'URL
        if client.url:
            session.headers['base_url'] = client.url
        
        # Extraction optimisée
        df = extract_sonar_projects_optimized(session)
        
        if df.empty:
            print("⚠️ Aucun projet à exporter")
            return ""
            
        # Export vers Excel optimisé
        return _export_to_excel_optimized(df)
        
    except Exception as e:
        print(f"❌ Erreur extraction/export optimisé: {e}")
        return ""


def _export_to_excel_optimized(df: pd.DataFrame) -> str:
    """
    Export Excel optimisé avec structure organisée
    
    Args:
        df: DataFrame avec projets et métriques
        
    Returns:
        str: Chemin du fichier Excel
    """
    try:
        from pathlib import Path
        
        # Créer le répertoire d'export
        exports_dir = Path("exports/sonar")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = exports_dir / f"sonar_projects_optimized_{timestamp}.xlsx"
        
        print(f"📁 Export vers: {filename}")
        
        # Réorganiser les colonnes dans l'ordre logique
        column_order = _get_optimized_column_order(df.columns)
        df_export = df.reindex(columns=column_order)
        
        # Export avec formatage
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_export.to_excel(
                writer, 
                sheet_name='Sonar Projects Optimized', 
                index=False,
                freeze_panes=(1, 0)
            )
            
            # Ajustement des colonnes
            worksheet = writer.sheets['Sonar Projects Optimized']
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value or '')) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 40)
        
        file_path = str(filename.absolute())
        
        # Résumé
        _print_optimized_summary(df_export)
        
        print(f"✅ Export optimisé terminé: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"❌ Erreur export optimisé: {e}")
        return ""


def _get_optimized_column_order(available_columns) -> List[str]:
    """
    Retourne l'ordre optimisé des colonnes pour Excel
    
    Args:
        available_columns: Colonnes disponibles dans le DataFrame
        
    Returns:
        List[str]: Ordre des colonnes optimisé
    """
    # Ordre logique souhaité
    preferred_order = [
        # Identification et dates
        'Clé Projet', 'Nom Projet', 'Date Export', 'Date Création Projet', 
        'Dernière Analyse', 'Date Quality Gate', 'Quality Gate Status',
        
        # Structure et taille
        'Lignes Code', 'Lignes Totales', 'Fichiers', 'Répertoires', 
        'Classes', 'Fonctions', 'Instructions',
        
        # Complexité
        'Complexité Total', 'Complexité Cognitive', 'Complexité Classes', 
        'Complexité Fonctions', 'Densité Commentaires %',
        
        # Duplication
        'Lignes Dupliquées', 'Blocs Dupliqués', 'Fichiers Dupliqués', 'Densité Duplication %',
        
        # Couverture
        'Couverture %', 'Couverture Lignes %', 'Couverture Branches %',
        'Lignes à Couvrir', 'Lignes Non Couvertes', 'Conditions à Couvrir', 'Conditions Non Couvertes',
        
        # Tests
        'Nombre Tests', 'Succès Tests %', 'Échecs Tests', 'Erreurs Tests', 'Tests Ignorés',
        
        # Issues
        'Bugs', 'Rating Fiabilité', 'Effort Bugs (min)',
        'Vulnérabilités', 'Rating Sécurité', 'Effort Sécurité (min)',
        'Points Chauds', 'Points Chauds Revus', 'Rating Revue Sécurité',
        'Code Smells', 'Rating Maintenabilité', 'Dette Technique (min)', 
        'Ratio Dette %', 'Coût Développement (min)',
        
        # Évolution
        'Nouvelles Lignes', 'Nouvelle Couverture %', 'Nouveaux Bugs', 'Nouveaux Code Smells'
    ]
    
    # Filtrer pour ne garder que les colonnes disponibles
    ordered_columns = [col for col in preferred_order if col in available_columns]
    
    # Ajouter les colonnes restantes à la fin
    remaining_columns = [col for col in available_columns if col not in ordered_columns]
    
    return ordered_columns + sorted(remaining_columns)


def _print_optimized_summary(df: pd.DataFrame):
    """
    Affiche un résumé détaillé de l'export optimisé
    """
    try:
        print(f"\n📋 RÉSUMÉ EXPORT SONARQUBE OPTIMISÉ")
        print(f"   📊 Total projets: {len(df)}")
        print(f"   📈 Total colonnes: {len(df.columns)}")
        
        # Quality Gates
        if 'Quality Gate Status' in df.columns:
            qg_stats = df['Quality Gate Status'].value_counts()
            print(f"   🎯 Quality Gates:")
            for status, count in qg_stats.items():
                print(f"     - {status}: {count}")
        
        # Projets avec/sans analyse
        if 'Dernière Analyse' in df.columns:
            analyzed = df['Dernière Analyse'].notna().sum()
            print(f"   📅 Analyses:")
            print(f"     - Projets analysés: {analyzed}")
            print(f"     - Sans analyse: {len(df) - analyzed}")
            
        # Métriques de qualité moyennes
        quality_metrics = ['Bugs', 'Vulnérabilités', 'Code Smells', 'Couverture %']
        for metric in quality_metrics:
            if metric in df.columns:
                values = pd.to_numeric(df[metric], errors='coerce')
                if not values.isna().all():
                    mean_val = values.mean()
                    print(f"   📊 {metric} (moyenne): {mean_val:.1f}")
        
        print("📁 Données optimisées prêtes pour Power BI")
        
    except Exception as e:
        print(f"⚠️ Erreur génération résumé: {e}")


if __name__ == "__main__":
    """Test direct de l'extracteur optimisé"""
    result = extract_and_export_sonar_optimized()
    if result:
        print(f"🎯 Export optimisé réussi: {result}")
    else:
        print("❌ Export optimisé échoué")
