#!/usr/bin/env python3
"""
🔍 ANALYSE APPROFONDIE SONARQUBE COMMUNITY EDITION ONCF
=========================================================
Investigation complète des APIs disponibles, structure des projets,
et limitations Community Edition vs Enterprise

Objectif: Comprendre pourquoi 0 métriques malgré token global admin
"""

import requests
import urllib3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SONAR_URL = os.getenv('SONAR_URL', 'https://sonar.oncf.net')
SONAR_TOKEN = os.getenv('SONAR_TOKEN', 'sqa_630313507c6e8c0f2f742d0ca2ca9272b989a4c0')

class SonarQubeAPIInvestigator:
    """Investigateur approfondi des APIs SonarQube Community"""
    
    def __init__(self):
        self.headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
        self.base_url = SONAR_URL
        
    def log_section(self, title: str):
        """Log une section"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
    
    def test_api_endpoint(self, endpoint: str, params: Optional[dict] = None) -> Dict[str, Any]:
        """Test un endpoint API avec analyse complète"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=self.headers, 
                verify=False, 
                timeout=30
            )
            
            result = {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'url': url,
                'params': params or {}
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['data'] = data
                    result['data_type'] = type(data).__name__
                    if isinstance(data, dict):
                        result['keys'] = list(data.keys())
                        result['data_size'] = len(str(data))
                    elif isinstance(data, list):
                        result['array_length'] = len(data)
                        result['data_size'] = len(str(data))
                except:
                    result['raw_response'] = response.text[:500]
            else:
                result['error'] = response.text[:200]
                result['headers'] = dict(response.headers)
            
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'success': False,
                'error': f'Exception: {str(e)}',
                'url': url
            }
    
    def investigate_system_info(self):
        """Analyser les informations système SonarQube"""
        self.log_section("1. INFORMATIONS SYSTEME SONARQUBE")
        
        # Version et édition
        system_info = self.test_api_endpoint('/api/system/info')
        if system_info['success']:
            data = system_info['data']
            print(f"Version SonarQube: {data.get('version', 'Inconnue')}")
            print(f"Edition: {data.get('edition', 'Inconnue')}")
            print(f"Serveur ID: {data.get('serverId', 'Inconnu')}")
            
            # Plugins installés
            plugins = data.get('plugins', {})
            print(f"Plugins installes: {len(plugins)}")
            for plugin_key, plugin_info in plugins.items():
                print(f"  - {plugin_key}: {plugin_info.get('version', '?')}")
        
        # Status système
        status = self.test_api_endpoint('/api/system/status')
        if status['success']:
            print(f"Status: {status['data'].get('status', 'Inconnu')}")
        
        # Santé système
        health = self.test_api_endpoint('/api/system/health')
        if health['success']:
            print(f"Sante: {health['data'].get('health', 'Inconnu')}")
    
    def investigate_available_apis(self):
        """Analyser toutes les APIs disponibles"""
        self.log_section("2. APIS DISPONIBLES")
        
        # Liste des endpoints à tester
        endpoints = [
            # Projets
            ('/api/projects/search', {'ps': 5}),
            ('/api/components/search', {'qualifiers': 'TRK', 'ps': 5}),
            ('/api/components/search_projects', {'ps': 5}),
            
            # Métriques
            ('/api/metrics/search', {'ps': 20}),
            ('/api/measures/search', None),
            ('/api/measures/search_history', None),
            
            # Quality Gates
            ('/api/qualitygates/list', None),
            ('/api/qualitygates/get_by_project', None),
            
            # User et permissions
            ('/api/users/current', None),
            ('/api/permissions/groups', None),
            ('/api/permissions/users', None),
            
            # Navigation
            ('/api/navigation/component', None),
            ('/api/navigation/global', None),
            
            # Versions et branches
            ('/api/project_branches/list', None),
            ('/api/project_analyses/search', None)
        ]
        
        results = {}
        for endpoint, params in endpoints:
            result = self.test_api_endpoint(endpoint, params)
            results[endpoint] = result
            
            status = "OK" if result['success'] else f"ERROR {result.get('status_code', '?')}"
            print(f"{endpoint:<40} -> {status}")
            
            if result['success'] and 'keys' in result:
                print(f"    Cles disponibles: {result['keys']}")
        
        return results
    
    def investigate_project_structure(self):
        """Analyser la structure exacte des projets"""
        self.log_section("3. STRUCTURE PROJETS DETAILLEE")
        
        # Test différents endpoints projets
        project_apis = [
            ('/api/components/search', {'qualifiers': 'TRK', 'ps': 10}),
            ('/api/projects/search', {'ps': 10}),
            ('/api/components/search_projects', {'ps': 10})
        ]
        
        for endpoint, params in project_apis:
            print(f"\nTest: {endpoint}")
            result = self.test_api_endpoint(endpoint, params)
            
            if result['success']:
                data = result['data']
                
                if 'components' in data:
                    components = data['components'][:3]  # Premiers projets
                    print(f"  Projets trouves: {len(data['components'])}")
                    
                    for i, comp in enumerate(components):
                        print(f"    Projet {i+1}:")
                        for key, value in comp.items():
                            print(f"      {key}: {value}")
                        print()
                
                elif 'projects' in data:
                    projects = data['projects'][:3]
                    print(f"  Projets trouves: {len(data['projects'])}")
                    
                    for i, proj in enumerate(projects):
                        print(f"    Projet {i+1}:")
                        for key, value in proj.items():
                            print(f"      {key}: {value}")
                        print()
            else:
                print(f"  ERREUR: {result.get('error', 'Inconnue')}")
    
    def investigate_metrics_deep(self):
        """Analyse approfondie des métriques disponibles"""
        self.log_section("4. METRIQUES DISPONIBLES")
        
        # Récupérer toutes les métriques
        metrics_result = self.test_api_endpoint('/api/metrics/search', {'ps': 500})
        
        if not metrics_result['success']:
            print(f"ERREUR recuperation metriques: {metrics_result.get('error')}")
            return
        
        data = metrics_result['data']
        metrics = data.get('metrics', [])
        
        print(f"Total metriques disponibles: {len(metrics)}")
        print()
        
        # Catégoriser les métriques
        categories = {}
        basic_metrics = ['ncloc', 'bugs', 'vulnerabilities', 'code_smells', 'coverage', 'lines', 'files']
        
        for metric in metrics:
            domain = metric.get('domain', 'Unknown')
            if domain not in categories:
                categories[domain] = []
            categories[domain].append(metric)
        
        # Afficher par catégorie
        for domain, domain_metrics in categories.items():
            print(f"{domain}: {len(domain_metrics)} metriques")
            
            # Afficher les métriques de base si dans cette catégorie
            for metric in domain_metrics:
                key = metric.get('key', '')
                if key in basic_metrics:
                    print(f"  *** {key}: {metric.get('name', '')} (BASIQUE)")
                elif len(domain_metrics) <= 10:  # Afficher toutes si peu nombreuses
                    print(f"      {key}: {metric.get('name', '')}")
        
        return metrics
    
    def test_specific_project_metrics(self):
        """Test métriques sur projets spécifiques connus"""
        self.log_section("5. TEST METRIQUES PROJETS SPECIFIQUES")
        
        # Projets de test avec différentes clés possibles
        test_projects = [
            'DAT_BACKEND_GATEWAY_SIV',
            'DAT_BACKEND_GATEWAY_SIV_KEY', 
            'ALARMEGMV',
            'ALARMEGMV_KEY',
            'API_HORAIRE',
            'API_HORAIRE_KEY'
        ]
        
        # Métriques de base à tester
        basic_metrics = ['ncloc', 'bugs', 'coverage', 'lines']
        
        print("Test des metriques de base sur projets connus:")
        print()
        
        for project in test_projects:
            print(f"Projet: {project}")
            
            # Test métrique par métrique
            for metric in basic_metrics:
                result = self.test_api_endpoint(
                    '/api/measures/component',
                    {'component': project, 'metricKeys': metric}
                )
                
                if result['success']:
                    data = result['data']
                    measures = data.get('component', {}).get('measures', [])
                    if measures:
                        value = measures[0].get('value', 'N/A')
                        print(f"  {metric}: {value}")
                    else:
                        print(f"  {metric}: Pas de donnees")
                else:
                    error_code = result.get('status_code', '?')
                    print(f"  {metric}: ERREUR {error_code}")
            print()
    
    def investigate_quality_gates_deep(self):
        """Analyse approfondie des Quality Gates"""
        self.log_section("6. QUALITY GATES DETAILLES")
        
        # Liste des Quality Gates
        qg_list = self.test_api_endpoint('/api/qualitygates/list')
        if qg_list['success']:
            gates = qg_list['data'].get('qualitygates', [])
            print(f"Quality Gates disponibles: {len(gates)}")
            for gate in gates:
                print(f"  - {gate.get('name')}: {gate.get('id')} (default: {gate.get('isDefault', False)})")
        
        # Test sur projets spécifiques
        test_projects = ['DAT_BACKEND_GATEWAY_SIV', 'ALARMEGMV']
        
        for project in test_projects:
            print(f"\nQuality Gate pour {project}:")
            qg_result = self.test_api_endpoint(
                '/api/qualitygates/project_status',
                {'projectKey': project}
            )
            
            if qg_result['success']:
                status_data = qg_result['data']
                project_status = status_data.get('projectStatus', {})
                print(f"  Status: {project_status.get('status', 'Inconnu')}")
                
                conditions = project_status.get('conditions', [])
                print(f"  Conditions: {len(conditions)}")
                for cond in conditions:
                    metric_key = cond.get('metricKey', '')
                    status = cond.get('status', '')
                    actual_value = cond.get('actualValue', '')
                    print(f"    - {metric_key}: {status} (valeur: {actual_value})")
            else:
                print(f"  ERREUR: {qg_result.get('status_code', '?')}")
    
    def generate_comprehensive_report(self):
        """Générer un rapport complet"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"sonar_investigation_report_{timestamp}.txt"
        
        print(f"\nGENERATION RAPPORT COMPLET: {report_file}")
        
        # Exécuter toutes les investigations
        self.investigate_system_info()
        api_results = self.investigate_available_apis()
        self.investigate_project_structure()
        metrics = self.investigate_metrics_deep()
        self.test_specific_project_metrics()
        self.investigate_quality_gates_deep()
        
        self.log_section("CONCLUSIONS ET RECOMMANDATIONS")
        print("1. Verifiez la version SonarQube Community vs Enterprise")
        print("2. Confirmez la structure exacte des cles de projets")
        print("3. Validez les permissions du token sur les metriques")
        print("4. Testez les APIs alternatives pour les mesures")
        
        return {
            'api_results': api_results,
            'metrics': metrics,
            'report_file': report_file
        }

def main():
    """Point d'entrée principal"""
    print("INVESTIGATION SONARQUBE COMMUNITY EDITION ONCF")
    print("="*60)
    print(f"URL: {SONAR_URL}")
    print(f"Token: {SONAR_TOKEN[:20]}...")
    print()
    
    investigator = SonarQubeAPIInvestigator()
    results = investigator.generate_comprehensive_report()
    
    print(f"\nINVESTIGATION TERMINEE")
    print("Analysez les resultats pour identifier le probleme des metriques")

if __name__ == "__main__":
    main()
