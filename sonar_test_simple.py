#!/usr/bin/env python3
"""
🎯 EXTRACTEUR SONARQUBE SIMPLE ET FIABLE
Test avec 10 premiers projets seulement
"""

import requests
import pandas as pd
import urllib3
import os
from datetime import datetime
from typing import Dict, List, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
SONAR_URL = os.getenv('SONAR_URL', 'https://sonar.oncf.net')
SONAR_TOKEN = os.getenv('SONAR_TOKEN', 'sqa_630313507c6e8c0f2f742d0ca2ca9272b989a4c0')

def get_first_10_projects() -> List[Dict[str, Any]]:
    """Récupère les 10 premiers projets"""
    print("📥 Récupération des projets SonarQube...")
    
    try:
        url = f"{SONAR_URL}/api/components/search"
        params = {
            'qualifiers': 'TRK',
            'p': 1,
            'ps': 10  # Seulement 10 projets
        }
        headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
        
        response = requests.get(url, params=params, headers=headers, verify=False, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            components = data.get('components', [])
            
            projects = []
            for comp in components:
                project_data = {
                    'key': comp.get('key'),
                    'name': comp.get('name'),
                    'visibility': comp.get('visibility', 'unknown')
                }
                projects.append(project_data)
            
            print(f"✅ {len(projects)} projets récupérés")
            return projects
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return []

def get_project_metrics(project_key: str) -> Dict[str, Any]:
    """Récupère les métriques d'un projet"""
    try:
        url = f"{SONAR_URL}/api/measures/component"
        params = {
            'component': project_key,
            'metricKeys': 'ncloc,bugs,coverage,lines,files,functions,classes,complexity'
        }
        headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
        
        response = requests.get(url, params=params, headers=headers, verify=False, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            measures = data.get('component', {}).get('measures', [])
            
            metrics = {}
            for measure in measures:
                metric_key = measure.get('metric')
                value = measure.get('value', '0')
                metrics[metric_key] = value
            
            return metrics
        else:
            print(f"    ❌ ERREUR {response.status_code} pour {project_key}")
            return {}
            
    except Exception as e:
        print(f"    ❌ Exception pour {project_key}: {e}")
        return {}

def extract_sonar_simple():
    """Extraction simple et fiable"""
    print("🎯 EXTRACTEUR SONARQUBE SIMPLE")
    print("=" * 40)
    
    # 1. Récupérer projets
    projects = get_first_10_projects()
    if not projects:
        print("❌ Aucun projet récupéré")
        return
    
    # 2. Extraire métriques
    data = []
    for i, project in enumerate(projects, 1):
        project_key = project['key']
        project_name = project['name']
        
        print(f"{i:2d}. {project_name} ({project_key})")
        
        # Récupérer métriques
        metrics = get_project_metrics(project_key)
        
        if metrics:
            row = {
                'Projet': project_name,
                'Clé Projet': project_key,
                'Visibilité': project['visibility'],
                'Lignes de Code': metrics.get('ncloc', '0'),
                'Lignes Totales': metrics.get('lines', '0'),
                'Fichiers': metrics.get('files', '0'),
                'Bugs': metrics.get('bugs', '0'),
                'Couverture': metrics.get('coverage', '0'),
                'Fonctions': metrics.get('functions', '0'),
                'Classes': metrics.get('classes', '0'),
                'Complexité': metrics.get('complexity', '0')
            }
            data.append(row)
            print(f"    ✅ {len(metrics)} métriques récupérées")
        else:
            print(f"    ❌ Aucune métrique")
    
    # 3. Créer DataFrame
    if data:
        df = pd.DataFrame(data)
        print(f"\n📊 {len(df)} projets avec métriques")
        
        # 4. Export Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/sonar/sonar_simple_test_{timestamp}.xlsx"
        
        os.makedirs("exports/sonar", exist_ok=True)
        df.to_excel(filename, sheet_name='SonarQube Projects', index=False)
        
        print(f"✅ Fichier créé: {filename}")
        print(f"📋 Colonnes: {list(df.columns)}")
        
        # Aperçu
        print(f"\n🔍 APERÇU (3 premiers projets):")
        for i, row in df.head(3).iterrows():
            print(f"  {i+1}. {row['Projet']} - {row['Lignes de Code']} lignes - {row['Bugs']} bugs")
            
    else:
        print("❌ Aucune donnée extraite")

if __name__ == "__main__":
    extract_sonar_simple()
