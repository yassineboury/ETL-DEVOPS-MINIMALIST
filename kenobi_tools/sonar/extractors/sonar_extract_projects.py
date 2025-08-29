"""
📁 Extracteur Projets SonarQube - VERSION DÉFINITIVE
Récupère tous les projets SonarQube avec 21 colonnes de métriques complètes
Architecture cohérente avec les extracteurs GitLab
"""
import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Import direct
from kenobi_tools.sonar.client.sonar_client import SonarClient
from kenobi_tools.sonar.exporters.sonar_excel_exporter import SonarExcelExporter

# 16 MÉTRIQUES MANAGERS VALIDÉES
METRICS = [
    'bugs', 'vulnerabilities', 'code_smells', 'security_hotspots',
    'coverage', 'duplicated_lines_density', 'ncloc', 'sqale_index',
    'reliability_rating', 'security_rating', 'sqale_rating',
    'alert_status', 'new_bugs', 'new_vulnerabilities', 
    'new_code_smells', 'new_coverage'
]

def enrich_project_with_metrics(session, base_url, project, metrics_string):
    """Enrichit UN projet avec toutes ses métriques"""
    project_key = project.get('key', '')
    # print(f"DEBUG: Enrichissement {project.get('name', 'N/A')}")  # Moins verbose
    
    # 21 colonnes initialisées
    data = {
        'cle_projet': project_key,
        'nom_projet': project.get('name', ''),
        'date_derniere_analyse': None,
        'date_analyse_iso': None,
        'quality_gate_statut': 'UNKNOWN',
        # 16 métriques
        'bugs': '0', 'vulnerabilities': '0', 'code_smells': '0', 'security_hotspots': '0',
        'coverage': '0.0', 'duplicated_lines_density': '0.0', 'ncloc': '0', 'sqale_index': '0',
        'reliability_rating': 'N/A', 'security_rating': 'N/A', 'sqale_rating': 'N/A',
        'alert_status': 'NONE', 'new_bugs': '0', 'new_vulnerabilities': '0',
        'new_code_smells': '0', 'new_coverage': '0.0'
    }
    
    # RÉCUPÉRATION DES MÉTRIQUES depuis /api/measures/component
    try:
        # print(f"DEBUG: Récupération métriques pour {project_key}")  # Moins verbose
        response = session.get(f"{base_url}/api/measures/component", params={
            'component': project_key,
            'metricKeys': metrics_string
        })
        
        if response.status_code == 200:
            json_data = response.json()
            measures = json_data.get('component', {}).get('measures', [])
            # print(f"DEBUG: {len(measures)} métriques reçues pour {project_key}")  # Moins verbose
            
            # Mise à jour des métriques
            for measure in measures:
                metric_key = measure.get('metric', '')
                metric_value = measure.get('value', '0')
                if metric_key in data:
                    data[metric_key] = metric_value
                    # print(f"DEBUG: {metric_key} = {metric_value}")  # Moins verbose
        else:
            # print(f"DEBUG: Erreur API métriques {response.status_code} pour {project_key}")  # Moins verbose
            pass
    except Exception as e:
        print(f"DEBUG: Exception métriques pour {project_key}: {e}")
    
    # RÉCUPÉRATION DU QUALITY GATE
    try:
        qg_response = session.get(f"{base_url}/api/qualitygates/project_status", params={
            'projectKey': project_key
        })
        if qg_response.status_code == 200:
            qg_data = qg_response.json()
            status = qg_data.get('projectStatus', {}).get('status', 'UNKNOWN')
            data['quality_gate_statut'] = status
            data['alert_status'] = status
    except Exception as e:
        print(f"DEBUG: Erreur Quality Gate pour {project_key}: {e}")
    
    # DATE D'ANALYSE
    analysis_date = project.get('lastAnalysisDate')
    if analysis_date:
        data['date_analyse_iso'] = analysis_date
        try:
            dt = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
            data['date_derniere_analyse'] = dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            data['date_derniere_analyse'] = analysis_date
    
    # print(f"DEBUG: Projet enrichi avec {len(data)} colonnes")  # Moins verbose
    return data


def extract_sonar_projects():
    """
    Fonction publique pour extraire tous les projets SonarQube
    
    Returns:
        pd.DataFrame: DataFrame avec 21 colonnes de métriques pour Power BI
    """
    print("📥 Extraction projets SonarQube...")
    
    # 1. CONNEXION
    client = SonarClient()
    session = client.connect()
    if not session:
        print("❌ Connexion SonarQube échouée")
        return pd.DataFrame()
    
    base_url = client.url or "https://sonar.oncf.net"
    metrics_string = ','.join(METRICS)
    
    # 2. RÉCUPÉRATION DES PROJETS
    try:
        response = session.get(f"{base_url}/api/projects/search", params={
            'ps': 500, 
            'qualifiers': 'TRK'
        })
        
        if response.status_code != 200:
            print(f"❌ Erreur API projets: {response.status_code}")
            return pd.DataFrame()
        
        projects = response.json().get('components', [])
        print(f"📊 {len(projects)} projets trouvés")
        
    except Exception as e:
        print(f"❌ Erreur récupération projets: {e}")
        return pd.DataFrame()
    
    # 3. ENRICHISSEMENT AVEC MÉTRIQUES
    enriched_projects = []
    total = len(projects)
    
    for i, project in enumerate(projects, 1):
        print(f"🔄 {i}/{total} - {project.get('name', 'N/A')}")
        enriched = enrich_project_with_metrics(session, base_url, project, metrics_string)
        enriched_projects.append(enriched)
    
    # 4. CRÉATION DATAFRAME
    df = pd.DataFrame(enriched_projects)
    
    if df.empty:
        print("⚠️ Aucune donnée extraite")
        return df
    
    print(f"✅ {len(df)} projets extraits avec {len(df.columns)} colonnes")
    
    return df


def main():
    print("=== EXTRACTEUR SONARQUBE SIMPLE ===")
    
    # 1. CONNEXION
    client = SonarClient()
    session = client.connect()
    if not session:
        print("ERREUR: Connexion échouée")
        return
    
    base_url = client.url or "https://sonar.oncf.net"
    metrics_string = ','.join(METRICS)
    print(f"MÉTRIQUES: {metrics_string}")
    
    # 2. RÉCUPÉRATION DES PROJETS
    print("Récupération des projets...")
    response = session.get(f"{base_url}/api/projects/search", params={'ps': 500, 'qualifiers': 'TRK'})
    
    if response.status_code != 200:
        print(f"ERREUR API projets: {response.status_code}")
        return
    
    projects = response.json().get('components', [])
    print(f"PROJETS TROUVÉS: {len(projects)}")
    
    # 3. ENRICHISSEMENT
    enriched_projects = []
    for i, project in enumerate(projects, 1):
        print(f"=== {i}/{len(projects)} ===")
        enriched = enrich_project_with_metrics(session, base_url, project, metrics_string)
        enriched_projects.append(enriched)
        
        # Extraction complète des 89 projets
        # if i >= 3:
        #     print("DEBUG: Arrêt après 3 projets pour test")
        #     break
    
    # 4. DATAFRAME
    df = pd.DataFrame(enriched_projects)
    print(f"DATAFRAME CRÉÉ: {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"COLONNES: {list(df.columns)}")
    
    # 5. EXPORT
    exporter = SonarExcelExporter()
    filename = exporter.export_projects_to_excel(df)
    print(f"EXPORT: {filename}")
    
    return filename

if __name__ == "__main__":
    main()
