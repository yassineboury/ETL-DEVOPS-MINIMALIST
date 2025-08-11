"""
Extraction des métriques de couverture SonarQube
"""
import requests
import pandas as pd
from typing import Dict, List, Optional


def extract_coverage(sonar_url: str, sonar_token: str, project_keys: List[str]) -> pd.DataFrame:
    """
    Extrait les métriques de couverture de code des projets SonarQube
    
    Args:
        sonar_url: URL de l'instance SonarQube
        sonar_token: Token d'authentification SonarQube
        project_keys: Liste des clés de projets SonarQube
        
    Returns:
        DataFrame avec les métriques de couverture
    """
    print("🔍 Extraction de la couverture de code SonarQube...")
    
    coverage_data = []
    
    # Métriques de couverture à récupérer
    metrics = [
        'coverage',                    # Couverture globale
        'line_coverage',              # Couverture de lignes
        'branch_coverage',            # Couverture de branches
        'new_coverage',               # Couverture nouveau code
        'new_line_coverage',          # Couverture lignes nouveau code
        'new_branch_coverage',        # Couverture branches nouveau code
        'uncovered_lines',            # Lignes non couvertes
        'uncovered_conditions',       # Conditions non couvertes
    ]
    
    for project_key in project_keys:
        try:
            # API SonarQube pour récupérer les métriques
            url = f"{sonar_url}/api/measures/component"
            params = {
                'component': project_key,
                'metricKeys': ','.join(metrics)
            }
            
            response = requests.get(
                url, 
                params=params,
                auth=(sonar_token, ''),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                component = data.get('component', {})
                measures = component.get('measures', [])
                
                # Construire le dictionnaire des métriques
                project_metrics = {
                    'project_key': project_key,
                    'project_name': component.get('name', project_key),
                    'last_analysis': component.get('analysisDate', ''),
                }
                
                # Ajouter chaque métrique
                for measure in measures:
                    metric_key = measure.get('metric')
                    metric_value = measure.get('value', '0')
                    
                    # Convertir en float si possible
                    try:
                        metric_value = float(metric_value)
                    except (ValueError, TypeError):
                        metric_value = 0.0
                        
                    project_metrics[metric_key] = metric_value
                
                # Ajouter des métriques calculées
                project_metrics['coverage_status'] = _get_coverage_status(
                    project_metrics.get('coverage', 0)
                )
                
                coverage_data.append(project_metrics)
                
            else:
                print(f"⚠️ Erreur API pour le projet {project_key}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction de la couverture pour {project_key}: {e}")
    
    print(f"✅ Couverture extraite pour {len(coverage_data)} projets")
    return pd.DataFrame(coverage_data)


def _get_coverage_status(coverage: float) -> str:
    """
    Determine le statut de la couverture selon des seuils
    """
    if coverage >= 80:
        return 'Excellente'
    elif coverage >= 60:
        return 'Bonne'
    elif coverage >= 40:
        return 'Moyenne'
    else:
        return 'Insuffisante'


def extract_coverage_history(sonar_url: str, sonar_token: str, project_key: str, 
                           from_date: str = None, to_date: str = None) -> pd.DataFrame:
    """
    Extrait l'historique de couverture d'un projet
    
    Args:
        sonar_url: URL de l'instance SonarQube
        sonar_token: Token d'authentification
        project_key: Clé du projet SonarQube
        from_date: Date de début (format YYYY-MM-DD)
        to_date: Date de fin (format YYYY-MM-DD)
        
    Returns:
        DataFrame avec l'historique de couverture
    """
    print(f"🔍 Extraction de l'historique de couverture pour {project_key}...")
    
    try:
        url = f"{sonar_url}/api/measures/search_history"
        params = {
            'component': project_key,
            'metrics': 'coverage,line_coverage,branch_coverage',
        }
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        response = requests.get(
            url,
            params=params, 
            auth=(sonar_token, ''),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            measures = data.get('measures', [])
            
            history_data = []
            for measure in measures:
                metric_key = measure.get('metric')
                history = measure.get('history', [])
                
                for point in history:
                    history_data.append({
                        'project_key': project_key,
                        'metric': metric_key,
                        'date': point.get('date'),
                        'value': float(point.get('value', 0))
                    })
            
            return pd.DataFrame(history_data)
            
        else:
            print(f"⚠️ Erreur API historique pour {project_key}: {response.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction de l'historique pour {project_key}: {e}")
        return pd.DataFrame()
