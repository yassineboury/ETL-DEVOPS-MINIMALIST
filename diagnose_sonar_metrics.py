#!/usr/bin/env python3
"""
🔍 Diagnostic SonarQube - Analyse des métriques
Identifie pourquoi les métriques sont vides
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kenobi_tools.sonar.client.sonar_client import SonarClient

def diagnose_sonar_metrics():
    """Diagnostic complet des métriques SonarQube"""
    print("🔍 DIAGNOSTIC MÉTRIQUES SONARQUBE")
    print("=" * 50)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Connexion
    client = SonarClient()
    session = client.connect()
    
    if not session:
        print("❌ Impossible de se connecter à SonarQube")
        return False
        
    # Récupérer un projet exemple
    try:
        print("\n1️⃣ Récupération d'un projet exemple...")
        projects_response = session.get(
            f"{client.url}/api/projects/search",
            params={'ps': 1, 'qualifiers': 'TRK'}
        )
        
        if projects_response.status_code != 200:
            print(f"❌ Erreur API projets: {projects_response.status_code}")
            return False
            
        projects_data = projects_response.json()
        projects = projects_data.get('components', [])
        
        if not projects:
            print("❌ Aucun projet trouvé")
            return False
            
        project = projects[0]
        project_key = project.get('key')
        project_name = project.get('name')
        
        print(f"✅ Projet exemple: {project_name} ({project_key})")
        
        # Test 2: Vérifier les métriques disponibles
        print(f"\n2️⃣ Test des métriques pour {project_key}...")
        
        # Liste des métriques essentielles à tester
        test_metrics = [
            'bugs', 'vulnerabilities', 'code_smells',
            'coverage', 'duplicated_lines_density',
            'ncloc', 'sqale_index',
            'reliability_rating', 'security_rating', 'sqale_rating'
        ]
        
        metrics_str = ','.join(test_metrics)
        metrics_response = session.get(
            f"{client.url}/api/measures/component",
            params={
                'component': project_key,
                'metricKeys': metrics_str
            }
        )
        
        print(f"📊 Status métriques API: {metrics_response.status_code}")
        
        if metrics_response.status_code == 200:
            metrics_data = metrics_response.json()
            component = metrics_data.get('component', {})
            measures = component.get('measures', [])
            
            print(f"📈 Métriques trouvées: {len(measures)}")
            
            if measures:
                print("\n✅ MÉTRIQUES DISPONIBLES:")
                for measure in measures:
                    metric_key = measure.get('metric', 'N/A')
                    value = measure.get('value', 'N/A')
                    print(f"   • {metric_key}: {value}")
            else:
                print("❌ Aucune métrique trouvée pour ce projet")
                
                # Test avec toutes les métriques disponibles
                print("\n3️⃣ Test avec toutes les métriques...")
                all_metrics_response = session.get(
                    f"{client.url}/api/measures/component",
                    params={'component': project_key}
                )
                
                if all_metrics_response.status_code == 200:
                    all_data = all_metrics_response.json()
                    all_measures = all_data.get('component', {}).get('measures', [])
                    print(f"📊 Total métriques disponibles: {len(all_measures)}")
                    
                    if all_measures:
                        print("\n📋 Toutes les métriques:")
                        for measure in all_measures[:10]:  # Limiter à 10
                            metric_key = measure.get('metric', 'N/A')
                            value = measure.get('value', 'N/A')
                            print(f"   • {metric_key}: {value}")
                        if len(all_measures) > 10:
                            print(f"   ... et {len(all_measures) - 10} autres métriques")
                
        else:
            print(f"❌ Erreur API métriques: {metrics_response.status_code}")
            print(f"Réponse: {metrics_response.text[:200]}...")
            
        # Test 3: Vérifier les métriques globales disponibles
        print(f"\n4️⃣ Récupération des métriques disponibles sur SonarQube...")
        metrics_list_response = session.get(f"{client.url}/api/metrics/search")
        
        if metrics_list_response.status_code == 200:
            metrics_list_data = metrics_list_response.json()
            available_metrics = metrics_list_data.get('metrics', [])
            print(f"📊 Métriques définies dans SonarQube: {len(available_metrics)}")
            
            # Afficher les métriques de qualité principales
            quality_metrics = [m for m in available_metrics 
                             if any(keyword in m.get('key', '').lower() 
                                   for keyword in ['bug', 'vulnerability', 'smell', 'coverage', 'rating'])]
            
            print(f"\n📈 Métriques de qualité disponibles ({len(quality_metrics)}):")
            for metric in quality_metrics[:15]:
                key = metric.get('key', 'N/A')
                name = metric.get('name', 'N/A')
                print(f"   • {key}: {name}")
                
        else:
            print(f"❌ Erreur récupération liste métriques: {metrics_list_response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")
        return False

if __name__ == "__main__":
    diagnose_sonar_metrics()
