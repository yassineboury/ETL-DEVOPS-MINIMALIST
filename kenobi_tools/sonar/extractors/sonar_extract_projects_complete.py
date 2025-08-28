"""
📊 Extracteur SonarQube COMPLET - Projets + TOUTES les Métriques
Récupère tous les projets avec l'ensemble complet des métriques SonarQube
Version unifiée pour avoir une vue complète de la qualité de code
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

# Ajouter le projet au path pour les imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from kenobi_tools.sonar.client.sonar_client import SonarClient


# 🎯 MÉTRIQUES SONARQUBE COMPLÈTES
SONAR_METRICS_COMPLETE = {
    # 📏 TAILLE ET COMPLEXITÉ
    'ncloc': 'Lignes Code',
    'lines': 'Lignes Totales', 
    'statements': 'Instructions',
    'functions': 'Fonctions',
    'classes': 'Classes',
    'files': 'Fichiers',
    'directories': 'Répertoires',
    'complexity': 'Complexité Cyclomatique',
    'cognitive_complexity': 'Complexité Cognitive',
    
    # 🐛 FIABILITÉ
    'bugs': 'Bugs',
    'reliability_rating': 'Rating Fiabilité',
    'reliability_remediation_effort': 'Effort Correction Fiabilité',
    
    # 🔒 SÉCURITÉ
    'vulnerabilities': 'Vulnérabilités',
    'security_rating': 'Rating Sécurité',
    'security_remediation_effort': 'Effort Correction Sécurité',
    'security_hotspots': 'Points Chauds Sécurité',
    'security_hotspots_reviewed': 'Points Chauds Revus',
    'security_review_rating': 'Rating Revue Sécurité',
    
    # 🧹 MAINTENABILITÉ
    'code_smells': 'Code Smells',
    'maintainability_rating': 'Rating Maintenabilité',
    'technical_debt': 'Dette Technique (min)',
    'sqale_debt_ratio': 'Ratio Dette Technique',
    
    # 🧪 COUVERTURE DE TESTS
    'coverage': 'Couverture Tests %',
    'line_coverage': 'Couverture Lignes %',
    'branch_coverage': 'Couverture Branches %',
    'uncovered_lines': 'Lignes Non Couvertes',
    'uncovered_conditions': 'Conditions Non Couvertes',
    
    # 📋 TESTS
    'tests': 'Nombre Tests',
    'test_success_density': 'Densité Succès Tests %',
    'test_failures': 'Échecs Tests',
    'test_errors': 'Erreurs Tests',
    'skipped_tests': 'Tests Ignorés',
    'test_execution_time': 'Temps Exécution Tests',
    
    # 🔄 DUPLICATION
    'duplicated_lines_density': 'Densité Duplication %',
    'duplicated_lines': 'Lignes Dupliquées',
    'duplicated_blocks': 'Blocs Dupliqués',
    'duplicated_files': 'Fichiers Dupliqués',
    
    # 📊 AUTRES MÉTRIQUES QUALITÉ
    'alert_status': 'Statut Quality Gate',
    'quality_gate_details': 'Détails Quality Gate',
    'sqale_index': 'Index SQALE',
    'development_cost': 'Coût Développement',
    'ncloc_language_distribution': 'Distribution Langages',
    'new_lines': 'Nouvelles Lignes',
    'new_coverage': 'Nouvelle Couverture %',
    'new_duplicated_lines_density': 'Nouvelle Duplication %',
    'new_maintainability_rating': 'Nouveau Rating Maintenabilité',
    'new_reliability_rating': 'Nouveau Rating Fiabilité', 
    'new_security_rating': 'Nouveau Rating Sécurité',
}


def extract_sonar_projects_complete(client_session) -> pd.DataFrame:
    """
    Extrait TOUS les projets SonarQube avec TOUTES les métriques disponibles
    
    Args:
        client_session: Session requests authentifiée SonarQube
        
    Returns:
        pd.DataFrame: DataFrame complet avec projets + toutes métriques
    """
    try:
        print("📊 Extraction COMPLÈTE projets SonarQube + toutes métriques...")
        
        # Initialiser le client temporairement
        temp_client = SonarClient()
        temp_client.session = client_session
        temp_client.url = client_session.headers.get('base_url', 'https://sonar.oncf.net')
        
        # Récupération de tous les projets
        all_projects = []
        page = 1
        page_size = 100
        
        while True:
            print(f"📄 Récupération projets page {page}...")
            
            response = client_session.get(
                f"{temp_client.url}/api/projects/search",
                params={
                    'ps': page_size,
                    'p': page,
                    'qualifiers': 'TRK'
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur API projets: {response.status_code}")
                break
                
            data = response.json()
            projects = data.get('components', [])
            
            if not projects:
                break
                
            print(f"📊 {len(projects)} projet(s) récupéré(s)")
            all_projects.extend(projects)
            
            # Vérifier si on a tout récupéré
            total_projects = data.get('paging', {}).get('total', 0)
            if len(all_projects) >= total_projects:
                break
                
            page += 1
            
        if not all_projects:
            print("⚠️ Aucun projet trouvé")
            return pd.DataFrame()
            
        print(f"📁 {len(all_projects)} projet(s) au total trouvés")
        
        # Récupération des métriques pour tous les projets
        print("📈 Récupération de TOUTES les métriques...")
        all_metrics_keys = ','.join(SONAR_METRICS_COMPLETE.keys())
        
        enriched_projects = []
        for i, project in enumerate(all_projects, 1):
            project_key = project.get('key', '')
            project_name = project.get('name', '')
            
            print(f"🔍 {i}/{len(all_projects)}: {project_name} ({project_key})")
            
            # Données de base du projet
            project_data = {
                'cle_projet': project_key,
                'nom_projet': project_name,
                'date_derniere_analyse': None
            }
            
            # Date de dernière analyse
            analysis_date = project.get('lastAnalysisDate')
            if analysis_date:
                try:
                    dt = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                    project_data['date_derniere_analyse'] = dt.strftime('%d/%m/%Y %H:%M:%S')
                except Exception:
                    project_data['date_derniere_analyse'] = analysis_date
            
            # Récupération de TOUTES les métriques
            metrics_data = _get_all_project_metrics(client_session, temp_client.url, project_key)
            
            # Fusion des données projet + métriques
            project_data.update(metrics_data)
            enriched_projects.append(project_data)
            
        # Conversion en DataFrame
        df = pd.DataFrame(enriched_projects)
        
        print(f"✅ {len(df)} projets avec métriques complètes extraits")
        print(f"📊 {len(df.columns)} colonnes de données au total")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction projets complets: {e}")
        return pd.DataFrame()


def _get_all_project_metrics(session, base_url: str, project_key: str) -> Dict[str, Any]:
    """
    Récupère TOUTES les métriques d'un projet SonarQube
    
    Args:
        session: Session requests authentifiée
        base_url: URL de base SonarQube
        project_key: Clé du projet
        
    Returns:
        dict: Toutes les métriques du projet
    """
    try:
        # Initialiser toutes les métriques à None
        metrics_values = {}
        for metric_key in SONAR_METRICS_COMPLETE.keys():
            column_name = SONAR_METRICS_COMPLETE[metric_key]
            metrics_values[column_name] = None
        
        # Récupération des métriques par batch (l'API a des limites)
        all_metrics_keys = list(SONAR_METRICS_COMPLETE.keys())
        batch_size = 20  # SonarQube limite le nombre de métriques par requête
        
        for i in range(0, len(all_metrics_keys), batch_size):
            batch_keys = all_metrics_keys[i:i + batch_size]
            metrics_param = ','.join(batch_keys)
            
            response = session.get(
                f"{base_url}/api/measures/component",
                params={
                    'component': project_key,
                    'metricKeys': metrics_param
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                component = data.get('component', {})
                measures = component.get('measures', [])
                
                # Traitement des mesures récupérées
                for measure in measures:
                    metric_key = measure.get('metric', '')
                    if metric_key in SONAR_METRICS_COMPLETE:
                        column_name = SONAR_METRICS_COMPLETE[metric_key]
                        value = measure.get('value', '')
                        
                        # Conversion des valeurs selon le type
                        processed_value = _process_metric_value(metric_key, value)
                        metrics_values[column_name] = processed_value
        
        # Quality Gate spécial (API séparée)
        try:
            qg_response = session.get(
                f"{base_url}/api/qualitygates/project_status",
                params={'projectKey': project_key}
            )
            
            if qg_response.status_code == 200:
                qg_data = qg_response.json()
                project_status = qg_data.get('projectStatus', {})
                metrics_values['Quality Gate'] = project_status.get('status', 'UNKNOWN')
        except Exception:
            metrics_values['Quality Gate'] = 'UNKNOWN'
        
        return metrics_values
        
    except Exception as e:
        print(f"⚠️ Erreur métriques projet {project_key}: {e}")
        # Retourner un dict avec toutes les métriques à None
        return {SONAR_METRICS_COMPLETE[key]: None for key in SONAR_METRICS_COMPLETE.keys()}


def _process_metric_value(metric_key: str, value: str) -> Any:
    """
    Traite et convertit une valeur de métrique selon son type
    
    Args:
        metric_key: Clé de la métrique
        value: Valeur brute de la métrique
        
    Returns:
        Any: Valeur traitée (float, int, str)
    """
    try:
        if not value or value == '':
            return None
            
        # Métriques numériques entières
        integer_metrics = [
            'ncloc', 'lines', 'statements', 'functions', 'classes', 'files',
            'directories', 'complexity', 'cognitive_complexity', 'bugs',
            'vulnerabilities', 'code_smells', 'uncovered_lines',
            'uncovered_conditions', 'tests', 'test_failures', 'test_errors',
            'skipped_tests', 'duplicated_lines', 'duplicated_blocks',
            'duplicated_files', 'security_hotspots', 'new_lines'
        ]
        
        # Métriques pourcentages (float)
        percentage_metrics = [
            'coverage', 'line_coverage', 'branch_coverage',
            'test_success_density', 'duplicated_lines_density',
            'sqale_debt_ratio', 'new_coverage', 'new_duplicated_lines_density'
        ]
        
        # Métriques ratings (A, B, C, D, E → 1, 2, 3, 4, 5)
        rating_metrics = [
            'reliability_rating', 'security_rating', 'maintainability_rating',
            'security_review_rating', 'new_maintainability_rating',
            'new_reliability_rating', 'new_security_rating'
        ]
        
        if metric_key in integer_metrics:
            return int(float(value))
        elif metric_key in percentage_metrics:
            return round(float(value), 2)
        elif metric_key in rating_metrics:
            # Convertir A,B,C,D,E en 1,2,3,4,5
            if value in ['A', '1', '1.0']:
                return 'A (1)'
            elif value in ['B', '2', '2.0']:
                return 'B (2)'
            elif value in ['C', '3', '3.0']:
                return 'C (3)'
            elif value in ['D', '4', '4.0']:
                return 'D (4)'
            elif value in ['E', '5', '5.0']:
                return 'E (5)'
            else:
                return f"Rating {value}"
        else:
            # Garder comme string pour les autres
            return str(value)
            
    except Exception:
        return value  # Retourner la valeur brute si traitement échoue


def extract_and_export_sonar_complete() -> str:
    """
    Point d'entrée pour l'extraction complète SonarQube
    
    Returns:
        str: Chemin du fichier Excel généré ou chaîne vide si erreur
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Connexion SonarQube
        client = SonarClient()
        session = client.connect()
        
        if not session:
            print("❌ Impossible de se connecter à SonarQube")
            return ""
            
        # Enrichir la session avec l'URL
        if client.url:
            session.headers['base_url'] = client.url
        
        # Extraction complète
        df = extract_sonar_projects_complete(session)
        
        if df.empty:
            print("⚠️ Aucun projet à exporter")
            return ""
            
        # Export vers Excel complet
        from kenobi_tools.sonar.exporters.sonar_complete_exporter import export_complete_to_excel
        return export_complete_to_excel(df)
        
    except Exception as e:
        print(f"❌ Erreur extraction/export complet: {e}")
        return ""


if __name__ == "__main__":
    """Test direct de l'extracteur complet"""
    result = extract_and_export_sonar_complete()
    if result:
        print(f"✅ Export complet terminé: {result}")
    else:
        print("❌ Export complet échoué")
