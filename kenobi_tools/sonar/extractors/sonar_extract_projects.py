"""
Extracteur de projets SonarQube
Extrait les données de base des projets avec architecture modulaire par sections
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from sonarqube import SonarQubeClient


def extract_projects(sonar_client: SonarQubeClient) -> pd.DataFrame:
    """
    Extrait la liste des projets SonarQube avec données de base
    
    Args:
        sonar_client: Client SonarQube authentifié
    
    Returns:
        DataFrame avec les projets ou DataFrame vide si erreur
    """
    try:
        print("📥 Extraction des projets SonarQube...")
        
        # ═══════════════════════════════════════════════════════════
        # 📊 SECTION : DONNÉES PROJETS
        # ═══════════════════════════════════════════════════════════
        projects_data = _extract_basic_project_data(sonar_client)
        
        if not projects_data:
            print("⚠️ Aucun projet trouvé")
            return pd.DataFrame()
        
        # ═══════════════════════════════════════════════════════════
        # 🔄 CONVERSION DATAFRAME
        # ═══════════════════════════════════════════════════════════
        df = pd.DataFrame(projects_data)
        
        # Format dates françaises
        if not df.empty and 'date_derniere_analyse' in df.columns:
            df = _format_date_columns(df)
        
        print(f"✅ {len(df)} projets extraits")
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction projets: {e}")
        return pd.DataFrame()


def _extract_basic_project_data(sonar_client: SonarQubeClient) -> List[Dict[str, Any]]:
    """
    SECTION DONNÉES PROJETS : Extrait les informations de base des projets
    
    Champs extraits:
    - Clé Projet
    - Nom Projet  
    - Date Dernière Analyse
    - Qualité Gate
    """
    projects_data = []
    
    try:
        # Récupération liste des projets
        projects = sonar_client.projects.search_projects()
        
        if not projects or 'components' not in projects:
            return []
        
        components = projects.get('components', [])
        if not components:
            return []
        
        for project in components:
            project_key = project.get('key', '')
            
            # Données de base du projet
            project_info = {
                'cle_projet': project_key,
                'nom_projet': project.get('name', ''),
                'date_derniere_analyse': _get_last_analysis_date(sonar_client, project_key),
                'qualite_gate': _get_quality_gate_status(sonar_client, project_key)
            }
            
            projects_data.append(project_info)
            
    except Exception as e:
        print(f"⚠️ Erreur extraction données projets: {e}")
    
    return projects_data


def _get_last_analysis_date(sonar_client: SonarQubeClient, project_key: str) -> str:
    """Récupère la date de dernière analyse"""
    try:
        # API correcte : search_project_analyses_and_events
        analyses = sonar_client.project_analyses.search_project_analyses_and_events(
            project=project_key
        )
        
        if analyses and 'analyses' in analyses and analyses['analyses']:
            # Récupérer la première analyse (plus récente)
            last_analysis = analyses['analyses'][0]
            analysis_date = last_analysis.get('date', '')
            if analysis_date:
                # Formatter la date au format français
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                    return dt.strftime('%d/%m/%Y %H:%M:%S')
                except:
                    return analysis_date
        
        return ''
        
    except Exception as e:
        print(f"⚠️ Erreur date analyse {project_key}: {e}")
        return ''


def _get_quality_gate_status(sonar_client: SonarQubeClient, project_key: str) -> str:
    """Récupère le statut du Quality Gate via les métriques"""
    try:
        # Utiliser les métriques pour récupérer le statut Quality Gate
        measures = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="alert_status"
        )
        
        if measures and measures.get('component', {}).get('measures'):
            component_measures = measures['component'].get('measures', [])
            for measure in component_measures:
                if measure.get('metric') == 'alert_status':
                    status = measure.get('value', 'NONE')
                    # Traduire en français
                    status_mapping = {
                        'OK': 'Réussi',
                        'ERROR': 'Échec', 
                        'WARN': 'Avertissement',
                        'NONE': 'Non défini'
                    }
                    return status_mapping.get(status, 'Non défini')
        
        return 'Non défini'
        
    except Exception as e:
        print(f"⚠️ Erreur Quality Gate {project_key}: {e}")
        return 'Non défini'


def _format_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Formate les colonnes de dates au format français Power BI"""
    try:
        date_columns = ['date_derniere_analyse']
        
        for col in date_columns:
            if col in df.columns:
                # Conversion vers datetime puis format français
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].dt.strftime('%d/%m/%Y %H:%M:%S')
                # Remplacer les valeurs NaT par chaîne vide
                df[col] = df[col].fillna('')
        
        return df
        
    except Exception as e:
        print(f"⚠️ Erreur formatage dates: {e}")
        return df


# ═══════════════════════════════════════════════════════════
# 📋 MAPPING COLONNES POWER BI
# ═══════════════════════════════════════════════════════════
SONAR_PROJECTS_COLUMN_MAPPING = {
    'cle_projet': 'Clé Projet',
    'nom_projet': 'Nom Projet', 
    'date_derniere_analyse': 'Date Dernière Analyse',
    'qualite_gate': 'Qualité Gate'
}

# Ordre des colonnes dans Excel
SONAR_PROJECTS_COLUMN_ORDER = [
    'Clé Projet', 'Nom Projet', 
    'Date Dernière Analyse', 'Qualité Gate'
]


# ═══════════════════════════════════════════════════════════
# 🚀 SECTIONS FUTURES (À IMPLÉMENTER)
# ═══════════════════════════════════════════════════════════

def _extract_security_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION SÉCURITÉ : Vulnérabilités, Security Rating, Security Hotspots
    À implémenter dans la prochaine itération
    """
    # TODO: Implémenter extraction métriques sécurité
    return {}


def _extract_maintainability_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION MAINTENABILITÉ : Code Smells, Tech Debt, Maintainability Rating
    À implémenter dans la prochaine itération  
    """
    # TODO: Implémenter extraction métriques maintenabilité
    return {}


def _extract_reliability_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION FIABILITÉ : Bugs, Reliability Rating
    À implémenter dans la prochaine itération
    """
    # TODO: Implémenter extraction métriques fiabilité
    return {}


def _extract_coverage_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION COUVERTURE : Coverage, Line Coverage, Branch Coverage
    À implémenter dans la prochaine itération
    """
    # TODO: Implémenter extraction métriques couverture
    return {}
