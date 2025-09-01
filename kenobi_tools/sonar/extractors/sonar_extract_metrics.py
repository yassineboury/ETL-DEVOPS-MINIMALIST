"""
Extracteur de métriques SonarQube - VERSION OPTIMISÉE POWER BI
Module pour extraire les métriques SonarQube essentielles (9 champs)
Optimisé pour Power BI - Champs critiques uniquement
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from sonarqube import SonarQubeClient

# Constantes
NON_DEFINI = 'Non défini'


def extract_sonar_metrics(sonar_client: SonarQubeClient) -> pd.DataFrame:
    """
    Extrait les métriques SonarQube essentielles (9 champs Power BI optimisés)
    
    Args:
        sonar_client: Client SonarQube authentifié
    
    Returns:
        DataFrame avec 9 métriques essentielles ou DataFrame vide si erreur
    """
    try:
        print("📥 Extraction des métriques SonarQube essentielles...")
        
        # ═══════════════════════════════════════════════════════════
        # 📊 EXTRACTION MÉTRIQUES ESSENTIELLES (9 champs)
        # ═══════════════════════════════════════════════════════════
        metrics_data = _extract_essential_metrics_data(sonar_client)
        
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
        
        print(f"✅ {len(df)} projets avec métriques essentielles extraits")
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction métriques: {e}")
        return pd.DataFrame()


def _extract_essential_metrics_data(sonar_client: SonarQubeClient) -> List[Dict[str, Any]]:
    """
    MÉTRIQUES ESSENTIELLES : 9 champs Power BI critiques uniquement
    
    Champs extraits (9 essentiels):
    - PROJET: Clé, Nom, Date Analyse, Quality Gate (4)
    - SÉCURITÉ: Vulnérabilités Totales, Note Sécurité (2) 
    - MAINTENABILITÉ: Code Smells, Dette Technique, Note (3)
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
            # 📊 MÉTRIQUES PROJET (4 champs essentiels)
            # ═══════════════════════════════════════════════════════════
            project_metrics = {
                'cle_projet': project_key,
                'nom_projet': project.get('name', ''),
                'date_derniere_analyse': _get_last_analysis_date(sonar_client, project_key),
                'qualite_gate': _get_quality_gate_status(sonar_client, project_key)
            }
            
            # ═══════════════════════════════════════════════════════════
            # 🔒 MÉTRIQUES SÉCURITÉ ESSENTIELLES (2 champs)
            # ═══════════════════════════════════════════════════════════
            security_metrics = _extract_essential_security_metrics(sonar_client, project_key)
            project_metrics.update(security_metrics)
            
            # ═══════════════════════════════════════════════════════════
            # 🔧 MÉTRIQUES MAINTENABILITÉ ESSENTIELLES (3 champs)
            # ═══════════════════════════════════════════════════════════
            maintainability_metrics = _extract_essential_maintainability_metrics(sonar_client, project_key)
            project_metrics.update(maintainability_metrics)
            
            metrics_data.append(project_metrics)
            
    except Exception as e:
        print(f"⚠️ Erreur extraction métriques essentielles: {e}")
    
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
                    dt = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                    return dt.strftime('%d/%m/%Y %H:%M:%S')
                except (ValueError, TypeError):
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
                            'NONE': NON_DEFINI
                        }
                        return status_mapping.get(status, NON_DEFINI)
        
        return NON_DEFINI
        
    except Exception as e:
        print(f"⚠️ Erreur Quality Gate {project_key}: {e}")
        return NON_DEFINI


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
# 📋 MAPPING COLONNES POWER BI - MÉTRIQUES ESSENTIELLES (9 CHAMPS)
# ═══════════════════════════════════════════════════════════
SONAR_METRICS_COLUMN_MAPPING = {
    # DONNÉES PROJET (4 colonnes)
    'cle_projet': 'Clé Projet',
    'nom_projet': 'Nom Projet', 
    'date_derniere_analyse': 'Date Dernière Analyse',
    'qualite_gate': 'Qualité Gate',
    
    # MÉTRIQUES SÉCURITÉ ESSENTIELLES (2 colonnes) 
    'vulnerabilities_totales': 'Vulnérabilités Totales',
    'note_securite': 'Note Sécurité',
    
    # MÉTRIQUES MAINTENABILITÉ ESSENTIELLES (3 colonnes)
    'code_smells_totaux': 'Code Smells Totaux',
    'dette_technique': 'Dette Technique (min)',
    'note_maintenabilite': 'Note Maintenabilité'
}

# Ordre des colonnes dans Excel (9 colonnes essentielles)
SONAR_METRICS_COLUMN_ORDER = [
    # Projet (4)
    'Clé Projet', 'Nom Projet', 'Date Dernière Analyse', 'Qualité Gate',
    # Sécurité essentielle (2)
    'Vulnérabilités Totales', 'Note Sécurité',
    # Maintenabilité essentielle (3)
    'Code Smells Totaux', 'Dette Technique (min)', 'Note Maintenabilité'
]


# ═══════════════════════════════════════════════════════════
# 🔒 MÉTRIQUES SÉCURITÉ ESSENTIELLES
# ═══════════════════════════════════════════════════════════

def _extract_essential_security_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SÉCURITÉ ESSENTIELLE : 2 champs critiques pour Power BI
    
    Métriques extraites:
    - Vulnérabilités Totales (nombre)
    - Note Sécurité (A-E)
    """
    security_data = {
        'vulnerabilities_totales': 0,
        'note_securite': NON_DEFINI
    }
    
    try:
        # Récupérer les métriques de sécurité essentielles
        security_metrics = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="vulnerabilities,security_rating"
        )
        
        if security_metrics and security_metrics.get('component', {}).get('measures'):
            raw_measures = security_metrics['component']['measures']
            if isinstance(raw_measures, list):
                _process_security_measures(raw_measures, security_data)
        
        return security_data
        
    except Exception as e:
        print(f"⚠️ Erreur sécurité essentielle {project_key}: {e}")
        return security_data


def _process_security_measures(measures: List[Dict[str, Any]], security_data: Dict[str, Any]) -> None:
    """Traite les métriques de sécurité - Fonction helper pour réduire la complexité cognitive"""
    for measure in measures:
        if not isinstance(measure, dict):
            continue
            
        metric_key = measure.get('metric', '')
        value = measure.get('value', '0')
        
        if metric_key == 'vulnerabilities':
            security_data['vulnerabilities_totales'] = int(value) if value.isdigit() else 0
        elif metric_key == 'security_rating':
            security_data['note_securite'] = _convert_rating_to_letter(value)


def _convert_rating_to_letter(rating_value: str) -> str:
    """Convertit les notes numériques SonarQube (1-5) en lettres (A-E)"""
    try:
        # Convertir en float puis en int pour gérer les décimales (ex: "1.0" -> 1)
        numeric_rating = int(float(rating_value))
        
        rating_map = {
            1: 'A',
            2: 'B', 
            3: 'C',
            4: 'D',
            5: 'E'
        }
        return rating_map.get(numeric_rating, NON_DEFINI)
    except (ValueError, TypeError):
        return NON_DEFINI


# ═══════════════════════════════════════════════════════════
# 🔧 MÉTRIQUES MAINTENABILITÉ ESSENTIELLES
# ═══════════════════════════════════════════════════════════

def _extract_essential_maintainability_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    MAINTENABILITÉ ESSENTIELLE : 3 champs critiques pour Power BI
    
    Métriques extraites:
    - Code Smells Totaux (nombre)
    - Dette Technique (minutes)
    - Note Maintenabilité (A-E)
    """
    maintainability_data = {
        'code_smells_totaux': 0,
        'dette_technique': 0,  # Minutes pour Power BI
        'note_maintenabilite': NON_DEFINI
    }
    
    try:
        maintainability_metrics = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="code_smells,sqale_index,sqale_rating"
        )
        
        if maintainability_metrics and maintainability_metrics.get('component', {}).get('measures'):
            raw_measures = maintainability_metrics['component']['measures']
            if isinstance(raw_measures, list):
                _process_maintainability_measures(raw_measures, maintainability_data)
        
        return maintainability_data
        
    except Exception as e:
        print(f"⚠️ Erreur maintenabilité essentielle {project_key}: {e}")
        return maintainability_data


def _process_maintainability_measures(measures: List[Dict[str, Any]], maintainability_data: Dict[str, Any]) -> None:
    """Traite les métriques de maintenabilité - Fonction helper pour réduire la complexité cognitive"""
    for measure in measures:
        if not isinstance(measure, dict):
            continue
            
        metric_key = measure.get('metric', '')
        value = measure.get('value', '0')
        
        if metric_key == 'code_smells':
            maintainability_data['code_smells_totaux'] = int(value) if value.isdigit() else 0
        elif metric_key == 'sqale_index':
            maintainability_data['dette_technique'] = _format_technical_debt(value)
        elif metric_key == 'sqale_rating':
            maintainability_data['note_maintenabilite'] = _convert_rating_to_letter(value)


def _format_technical_debt(debt_minutes: str) -> int:
    """Convertit la dette technique en minutes (nombre entier) - Power BI ready"""
    try:
        minutes = int(debt_minutes) if debt_minutes.isdigit() else 0
        return minutes  # Retourner directement les minutes pour Power BI
            
    except (ValueError, TypeError):
        return 0  # Retourner 0 au lieu de "Non défini" pour Power BI
