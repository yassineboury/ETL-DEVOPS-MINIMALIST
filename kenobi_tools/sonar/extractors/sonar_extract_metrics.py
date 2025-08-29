"""
Extracteur de métriques SonarQube - VERSION MODULAIRE COMPLÈTE
Module pour extraire toutes les métriques SonarQube : Projets + Sécurité + Maintenabilité
Pattern modulaire avec sections extensibles
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Union, Optional
from sonarqube import SonarQubeClient


def extract_sonar_metrics(sonar_client: SonarQubeClient) -> pd.DataFrame:
    """
    Extrait toutes les métriques SonarQube : Projets + Sécurité + Maintenabilité
    
    Args:
        sonar_client: Client SonarQube authentifié
    
    Returns:
        DataFrame avec les métriques complètes ou DataFrame vide si erreur
    """
    try:
        print("📥 Extraction des métriques SonarQube complètes...")
        
        # ═══════════════════════════════════════════════════════════
        # 📊 SECTION : DONNÉES PROJETS + SÉCURITÉ
        # ═══════════════════════════════════════════════════════════
        metrics_data = _extract_complete_metrics_data(sonar_client)
        
        if not metrics_data:
            print("⚠️ Aucune métrique trouvée")
            return pd.DataFrame()
        
        # ═══════════════════════════════════════════════════════════
        # 🔄 CONVERSION DATAFRAME
        # ═══════════════════════════════════════════════════════════
        df = pd.DataFrame(metrics_data)
        
        # Format dates françaises
        if not df.empty and 'date_derniere_analyse' in df.columns:
            df = _format_date_columns(df)
        
        print(f"✅ {len(df)} projets avec métriques extraits")
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction métriques: {e}")
        return pd.DataFrame()


def _extract_complete_metrics_data(sonar_client: SonarQubeClient) -> List[Dict[str, Any]]:
    """
    SECTION MÉTRIQUES COMPLÈTES : Projets + Sécurité + Futures extensions
    
    Champs extraits:
    - PROJET: Clé, Nom, Date Analyse, Quality Gate
    - SÉCURITÉ: Vulnérabilités (Global + Nouveau), Note Sécurité, Hotspots
    """
    metrics_data = []
    
    try:
        # Récupération liste des projets
        projects: Optional[Dict[str, Any]] = sonar_client.projects.search_projects()
        
        if not projects or 'components' not in projects:
            return []
        
        components: List[Dict[str, Any]] = projects.get('components', [])
        if not components or not isinstance(components, list):
            return []
        
        for project in components:
            if not isinstance(project, dict):
                continue
            project_key = project.get('key', '')
            
            # ═══════════════════════════════════════════════════════════
            # 📊 SECTION : DONNÉES PROJET (existantes)
            # ═══════════════════════════════════════════════════════════
            project_metrics = {
                'cle_projet': project_key,
                'nom_projet': project.get('name', ''),
                'date_derniere_analyse': _get_last_analysis_date(sonar_client, project_key),
                'qualite_gate': _get_quality_gate_status(sonar_client, project_key)
            }
            
            # ═══════════════════════════════════════════════════════════
            # 🔒 SECTION : MÉTRIQUES SÉCURITÉ (nouvelles)
            # ═══════════════════════════════════════════════════════════
            security_metrics = _extract_security_metrics(sonar_client, project_key)
            project_metrics.update(security_metrics)
            
            metrics_data.append(project_metrics)
            
    except Exception as e:
        print(f"⚠️ Erreur extraction métriques complètes: {e}")
    
    return metrics_data


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
        measures: Optional[Dict[str, Any]] = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="alert_status"
        )
        
        if measures and measures.get('component', {}).get('measures'):
            component_measures: List[Dict[str, Any]] = measures['component'].get('measures', [])
            if isinstance(component_measures, list):
                for measure in component_measures:
                    if isinstance(measure, dict) and measure.get('metric') == 'alert_status':
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
# 📋 MAPPING COLONNES POWER BI - MÉTRIQUES COMPLÈTES
# ═══════════════════════════════════════════════════════════
SONAR_METRICS_COLUMN_MAPPING = {
    # DONNÉES PROJET (4 colonnes)
    'cle_projet': 'Clé Projet',
    'nom_projet': 'Nom Projet', 
    'date_derniere_analyse': 'Date Dernière Analyse',
    'qualite_gate': 'Qualité Gate',
    
    # MÉTRIQUES SÉCURITÉ (6 colonnes) 
    'vulnerabilities_totales': 'Vulnérabilités Totales',
    'vulnerabilities_nouvelles': 'Nouvelles Vulnérabilités',
    'note_securite': 'Note Sécurité',
    'note_securite_nouveau': 'Nouvelle Note Sécurité',
    'hotspots_securite': 'Hotspots Sécurité',
    'hotspots_revises_pct': 'Hotspots Révisés (%)'
}

# Ordre des colonnes dans Excel (10 colonnes total)
SONAR_METRICS_COLUMN_ORDER = [
    # Projet
    'Clé Projet', 'Nom Projet', 'Date Dernière Analyse', 'Qualité Gate',
    # Sécurité  
    'Vulnérabilités Totales', 'Nouvelles Vulnérabilités',
    'Note Sécurité', 'Nouvelle Note Sécurité', 
    'Hotspots Sécurité', 'Hotspots Révisés (%)'
]


# ═══════════════════════════════════════════════════════════
# 🚀 SECTIONS FUTURES (À IMPLÉMENTER)
# ═══════════════════════════════════════════════════════════

def _extract_security_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION SÉCURITÉ : Extraire les métriques de sécurité (Global + Nouveau Code)
    
    Métriques extraites:
    - Vulnérabilités Totales / Nouvelles
    - Note Sécurité Global / Nouveau  
    - Hotspots Sécurité + % Révisés
    """
    security_data = {
        'vulnerabilities_totales': 0,
        'vulnerabilities_nouvelles': 0,
        'note_securite': 'Non défini',
        'note_securite_nouveau': 'Non défini',
        'hotspots_securite': 0,
        'hotspots_revises_pct': 0
    }
    
    try:
        # Récupérer toutes les métriques de sécurité en une fois
        security_metrics: Optional[Dict[str, Any]] = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="vulnerabilities,new_vulnerabilities,security_rating,new_security_rating,security_hotspots,security_hotspots_reviewed"
        )
        
        if security_metrics and security_metrics.get('component', {}).get('measures'):
            measures: List[Dict[str, Any]] = security_metrics['component']['measures']
            
            if isinstance(measures, list):
                for measure in measures:
                    if not isinstance(measure, dict):
                        continue
                        
                    metric_key = measure.get('metric', '')
                    value = measure.get('value', '0')
                    
                    # Mapper chaque métrique
                    if metric_key == 'vulnerabilities':
                        security_data['vulnerabilities_totales'] = int(value) if value.isdigit() else 0
                        
                    elif metric_key == 'new_vulnerabilities':
                        security_data['vulnerabilities_nouvelles'] = int(value) if value.isdigit() else 0
                        
                    elif metric_key == 'security_rating':
                        security_data['note_securite'] = _convert_rating_to_letter(value)
                        
                    elif metric_key == 'new_security_rating':
                        security_data['note_securite_nouveau'] = _convert_rating_to_letter(value)
                        
                    elif metric_key == 'security_hotspots':
                        security_data['hotspots_securite'] = int(value) if value.isdigit() else 0
                        
                    elif metric_key == 'security_hotspots_reviewed':
                        security_data['hotspots_revises_pct'] = float(value) if value.replace('.', '').isdigit() else 0.0
        
        return security_data
        
    except Exception as e:
        print(f"⚠️ Erreur sécurité {project_key}: {e}")
        return security_data


def _convert_rating_to_letter(rating_value: str) -> str:
    """Convertit les notes numériques SonarQube (1-5) en lettres (A-E)"""
    try:
        rating_map = {
            '1': 'A',
            '2': 'B', 
            '3': 'C',
            '4': 'D',
            '5': 'E'
        }
        return rating_map.get(str(rating_value), 'Non défini')
    except:
        return 'Non défini'


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
