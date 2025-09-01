"""
Extracteur de métriques SonarQube - VERSION MODULAIRE COMPLÈTE
Module pour extraire toutes les métriques SonarQube : Projets + Sécurité + Maintenabilité
Pattern modulaire avec sections extensibles
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Union, Optional
from sonarqube import SonarQubeClient

# Constantes
NON_DEFINI = 'Non défini'


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
            # 🔒 SECTION : MÉTRIQUES SÉCURITÉ (existantes)
            # ═══════════════════════════════════════════════════════════
            security_metrics = _extract_security_metrics(sonar_client, project_key)
            project_metrics.update(security_metrics)
            
            # ═══════════════════════════════════════════════════════════
            # 🔧 SECTION : MÉTRIQUES MAINTENABILITÉ (nouvelles)
            # ═══════════════════════════════════════════════════════════
            maintainability_metrics = _extract_maintainability_metrics(sonar_client, project_key)
            project_metrics.update(maintainability_metrics)
            
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
    'hotspots_revises_pct': 'Hotspots Révisés (%)',
    
    # MÉTRIQUES MAINTENABILITÉ (6 colonnes)
    'code_smells_totaux': 'Code Smells Totaux',
    'code_smells_nouveaux': 'Nouveaux Code Smells',
    'dette_technique': 'Dette Technique',
    'dette_technique_nouvelle': 'Nouvelle Dette Technique',
    'note_maintenabilite': 'Note Maintenabilité',
    'note_maintenabilite_nouvelle': 'Nouvelle Note Maintenabilité'
}

# Ordre des colonnes dans Excel (16 colonnes total)
SONAR_METRICS_COLUMN_ORDER = [
    # Projet (4)
    'Clé Projet', 'Nom Projet', 'Date Dernière Analyse', 'Qualité Gate',
    # Sécurité (6)
    'Vulnérabilités Totales', 'Nouvelles Vulnérabilités',
    'Note Sécurité', 'Nouvelle Note Sécurité', 
    'Hotspots Sécurité', 'Hotspots Révisés (%)',
    # Maintenabilité (6)
    'Code Smells Totaux', 'Nouveaux Code Smells',
    'Dette Technique', 'Nouvelle Dette Technique',
    'Note Maintenabilité', 'Nouvelle Note Maintenabilité'
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
        'note_securite': NON_DEFINI,
        'note_securite_nouveau': NON_DEFINI,
        'hotspots_securite': 0,
        'hotspots_revises_pct': 0
    }
    
    try:
        # Récupérer toutes les métriques de sécurité en une fois
        security_metrics = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="vulnerabilities,new_vulnerabilities,security_rating,new_security_rating,security_hotspots,security_hotspots_reviewed"
        )
        
        if not security_metrics or not security_metrics.get('component', {}).get('measures'):
            return security_data
            
        measures: List[Dict[str, Any]] = security_metrics['component']['measures']
        if not isinstance(measures, list):
            return security_data
            
        # Traiter chaque métrique
        for measure in measures:
            if not isinstance(measure, dict):
                continue
                
            metric_key = measure.get('metric', '')
            
            # Gérer les nouvelles métriques avec structure period
            if metric_key.startswith('new_') and 'period' in measure:
                value = measure['period'].get('value', '0')
            else:
                value = measure.get('value', '0')
            
            # Déléguer le traitement à des fonctions spécialisées
            _process_single_security_metric(security_data, metric_key, value)
        
        return security_data
        
    except Exception as e:
        print(f"⚠️ Erreur sécurité {project_key}: {e}")
        return security_data


def _process_single_security_metric(security_data: Dict[str, Any], metric_key: str, value: str) -> None:
    """Traite une métrique de sécurité individuelle"""
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
        security_data['hotspots_revises_pct'] = float(value) if value.replace('.', '').replace(',', '').isdigit() else 0.0


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


def _format_technical_debt(debt_minutes: str) -> str:
    """Convertit la dette technique de minutes en format lisible (heures/jours)"""
    try:
        minutes = int(debt_minutes) if debt_minutes.isdigit() else 0
        if minutes == 0:
            return NON_DEFINI
        
        if minutes < 60:
            return f"{minutes}min"
        elif minutes < 1440:  # moins d'un jour
            hours = round(minutes / 60, 1)
            return f"{hours}h"
        else:  # plus d'un jour
            days = round(minutes / 1440, 1)
            return f"{days}j"
            
    except (ValueError, TypeError):
        return NON_DEFINI


# ═══════════════════════════════════════════════════════════
# 🚀 SECTIONS FUTURES (À IMPLÉMENTER)  
# ═══════════════════════════════════════════════════════════

def _extract_maintainability_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION MAINTENABILITÉ : Code Smells, Tech Debt, Maintainability Rating
    
    Métriques extraites:
    - Code Smells (Total/Nouveaux)
    - Dette technique (Total/Nouveau)
    - Note de maintenabilité (Global/Nouveau)
    """
    maintainability_data = {
        'code_smells_totaux': 0,
        'code_smells_nouveaux': 0,
        'dette_technique': NON_DEFINI,
        'dette_technique_nouvelle': NON_DEFINI,
        'note_maintenabilite': NON_DEFINI,
        'note_maintenabilite_nouvelle': NON_DEFINI
    }
    
    try:
        maintainability_metrics = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="code_smells,new_code_smells,sqale_index,new_technical_debt,sqale_rating,new_maintainability_rating"
        )
        
        if maintainability_metrics and maintainability_metrics.get('component', {}).get('measures'):
            measures_raw = maintainability_metrics['component']['measures']
            if not isinstance(measures_raw, list):
                return maintainability_data
            
            # Annotation explicite pour éviter l'erreur Pylance
            measures: List[Dict[str, Any]] = measures_raw
            
            for measure in measures:  # type: ignore
                if not isinstance(measure, dict):
                    continue
                    
                _process_maintainability_measure(maintainability_data, measure)
        
        return maintainability_data
        
    except Exception as e:
        print(f"⚠️ Erreur maintenabilité {project_key}: {e}")
        return maintainability_data


def _process_maintainability_measure(maintainability_data: Dict[str, Any], measure: Dict[str, Any]) -> None:
    """Traite une métrique de maintenabilité individuelle"""
    metric_key = measure.get('metric', '')
    value = measure.get('value', '0')
    
    if metric_key == 'code_smells':
        maintainability_data['code_smells_totaux'] = int(value) if value.isdigit() else 0
    elif metric_key == 'new_code_smells':
        maintainability_data['code_smells_nouveaux'] = int(value) if value.isdigit() else 0
    elif metric_key == 'sqale_index':
        maintainability_data['dette_technique'] = _format_technical_debt(value)
    elif metric_key == 'new_technical_debt':
        maintainability_data['dette_technique_nouvelle'] = _format_technical_debt(value)
    elif metric_key == 'sqale_rating':
        maintainability_data['note_maintenabilite'] = _convert_rating_to_letter(value)
    elif metric_key == 'new_maintainability_rating':
        maintainability_data['note_maintenabilite_nouvelle'] = _convert_rating_to_letter(value)


def _extract_reliability_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION FIABILITÉ : Bugs, Reliability Rating
    
    Métriques extraites:
    - Bugs (Total/Nouveaux)
    - Note de fiabilité (Global/Nouveau)
    """
    reliability_data = {
        'bugs_totaux': 0,
        'bugs_nouveaux': 0,
        'note_fiabilite': NON_DEFINI,
        'note_fiabilite_nouvelle': NON_DEFINI
    }
    
    try:
        reliability_metrics = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="bugs,new_bugs,reliability_rating,new_reliability_rating"
        )
        
        if reliability_metrics and reliability_metrics.get('component', {}).get('measures'):
            measures_raw = reliability_metrics['component']['measures']
            if not isinstance(measures_raw, list):
                return reliability_data
            
            # Annotation explicite pour éviter l'erreur Pylance
            measures: List[Dict[str, Any]] = measures_raw
            
            for measure in measures:  # type: ignore
                if not isinstance(measure, dict):
                    continue
                    
                _process_reliability_measure(reliability_data, measure)
        
        return reliability_data
        
    except Exception as e:
        print(f"⚠️ Erreur fiabilité {project_key}: {e}")
        return reliability_data


def _process_reliability_measure(reliability_data: Dict[str, Any], measure: Dict[str, Any]) -> None:
    """Traite une métrique de fiabilité individuelle"""
    metric_key = measure.get('metric', '')
    value = measure.get('value', '0')
    
    if metric_key == 'bugs':
        reliability_data['bugs_totaux'] = int(value) if value.isdigit() else 0
    elif metric_key == 'new_bugs':
        reliability_data['bugs_nouveaux'] = int(value) if value.isdigit() else 0
    elif metric_key == 'reliability_rating':
        reliability_data['note_fiabilite'] = _convert_rating_to_letter(value)
    elif metric_key == 'new_reliability_rating':
        reliability_data['note_fiabilite_nouvelle'] = _convert_rating_to_letter(value)


def _extract_coverage_metrics(sonar_client: SonarQubeClient, project_key: str) -> Dict[str, Any]:
    """
    SECTION COUVERTURE : Coverage, Line Coverage, Branch Coverage
    
    Métriques extraites:
    - Couverture générale (Total/Nouveau)
    - Couverture de ligne (Total/Nouveau) 
    - Couverture de branche (Total/Nouveau)
    """
    coverage_data = {
        'couverture_generale': 0.0,
        'couverture_generale_nouvelle': 0.0,
        'couverture_ligne': 0.0,
        'couverture_ligne_nouvelle': 0.0,
        'couverture_branche': 0.0,
        'couverture_branche_nouvelle': 0.0
    }
    
    try:
        coverage_metrics = sonar_client.measures.get_component_with_specified_measures(
            component=project_key,
            metricKeys="coverage,new_coverage,line_coverage,new_line_coverage,branch_coverage,new_branch_coverage"
        )
        
        if coverage_metrics and coverage_metrics.get('component', {}).get('measures'):
            measures_raw = coverage_metrics['component']['measures']
            if not isinstance(measures_raw, list):
                return coverage_data
            
            # Annotation explicite pour éviter l'erreur Pylance
            measures: List[Dict[str, Any]] = measures_raw
            
            for measure in measures:  # type: ignore
                if not isinstance(measure, dict):
                    continue
                    
                _process_coverage_measure(coverage_data, measure)
        
        return coverage_data
        
    except Exception as e:
        print(f"⚠️ Erreur couverture {project_key}: {e}")
        return coverage_data


def _process_coverage_measure(coverage_data: Dict[str, Any], measure: Dict[str, Any]) -> None:
    """Traite une métrique de couverture individuelle"""
    metric_key = measure.get('metric', '')
    value = measure.get('value', '0.0')
    
    percentage_value = float(value) if value.replace('.', '').isdigit() else 0.0
    
    if metric_key == 'coverage':
        coverage_data['couverture_generale'] = percentage_value
    elif metric_key == 'new_coverage':
        coverage_data['couverture_generale_nouvelle'] = percentage_value
    elif metric_key == 'line_coverage':
        coverage_data['couverture_ligne'] = percentage_value
    elif metric_key == 'new_line_coverage':
        coverage_data['couverture_ligne_nouvelle'] = percentage_value
    elif metric_key == 'branch_coverage':
        coverage_data['couverture_branche'] = percentage_value
    elif metric_key == 'new_branch_coverage':
        coverage_data['couverture_branche_nouvelle'] = percentage_value
