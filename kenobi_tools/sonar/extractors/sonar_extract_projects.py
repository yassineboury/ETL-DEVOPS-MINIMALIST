"""
📁 Extracteur Projets SonarQube
Récupère la liste complète des projets avec leurs informations principales
Architecture cohérente avec les extracteurs GitLab
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


def extract_sonar_projects(client_session) -> pd.DataFrame:
    """
    Extrait tous les projets SonarQube avec leurs informations principales
    
    Args:
        client_session: Session requests authentifiée SonarQube
        
    Returns:
        pd.DataFrame: DataFrame avec les projets ou DataFrame vide si erreur
    """
    try:
        print("📁 Extraction des projets SonarQube...")
        
        # Initialiser le client temporairement pour utiliser les méthodes
        temp_client = SonarClient()
        temp_client.session = client_session
        temp_client.url = client_session.headers.get('base_url', 'https://sonar.oncf.net')
        
        # Récupération de tous les projets (pagination si nécessaire)
        all_projects = []
        page = 1
        page_size = 100
        
        while True:
            print(f"📄 Récupération page {page}...")
            
            # Récupérer les projets avec pagination
            response = client_session.get(
                f"{temp_client.url}/api/projects/search",
                params={
                    'ps': page_size,
                    'p': page,
                    'qualifiers': 'TRK'
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Erreur API: {response.status_code}")
                break
                
            data = response.json()
            projects = data.get('components', [])
            
            if not projects:
                break
                
            print(f"📊 {len(projects)} projet(s) récupéré(s)")
            all_projects.extend(projects)
            
            # Vérifier si on a récupéré tous les projets
            total_projects = data.get('paging', {}).get('total', 0)
            if len(all_projects) >= total_projects:
                break
                
            page += 1
            
        if not all_projects:
            print("⚠️ Aucun projet trouvé")
            return pd.DataFrame()
            
        print(f"📁 {len(all_projects)} projet(s) au total extraits")
        
        # Enrichir chaque projet avec ses métriques Quality Gate
        enriched_projects = []
        for i, project in enumerate(all_projects, 1):
            print(f"🔍 Enrichissement {i}/{len(all_projects)}: {project.get('name', 'N/A')}")
            
            enriched_project = _enrich_project_data(client_session, temp_client.url, project)
            enriched_projects.append(enriched_project)
            
        # Conversion en DataFrame
        df = pd.DataFrame(enriched_projects)
        
        print(f"✅ {len(df)} projets extraits et enrichis")
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction projets: {e}")
        return pd.DataFrame()


def _enrich_project_data(session, base_url: str, project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrichit les données d'un projet avec Quality Gate et métriques de base
    
    Args:
        session: Session requests authentifiée
        base_url: URL de base SonarQube
        project: Données brutes du projet
        
    Returns:
        dict: Projet enrichi avec métriques
    """
    try:
        project_key = project.get('key', '')
        
        # Données de base du projet
        enriched = {
            'cle_projet': project_key,
            'nom_projet': project.get('name', ''),
            'date_derniere_analyse': None,
            'quality_gate_statut': 'UNKNOWN'
        }
        
        # Récupération du Quality Gate
        try:
            qg_response = session.get(
                f"{base_url}/api/qualitygates/project_status",
                params={'projectKey': project_key}
            )
            
            if qg_response.status_code == 200:
                qg_data = qg_response.json()
                project_status = qg_data.get('projectStatus', {})
                enriched['quality_gate_statut'] = project_status.get('status', 'UNKNOWN')
        except Exception:
            pass  # Garder la valeur par défaut
            
        # Récupération de la date de dernière analyse directement du projet
        try:
            # La date peut être disponible directement dans les données du projet
            analysis_date = project.get('lastAnalysisDate')
            if analysis_date:
                # Format ISO -> format français
                try:
                    dt = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
                    enriched['date_derniere_analyse'] = dt.strftime('%d/%m/%Y %H:%M:%S')
                except Exception:
                    enriched['date_derniere_analyse'] = analysis_date
        except Exception:
            pass  # Garder None si pas de date
            
        return enriched
        
    except Exception as e:
        print(f"⚠️ Erreur enrichissement projet {project.get('key', 'N/A')}: {e}")
        # Retourner au moins les données de base
        return {
            'cle_projet': project.get('key', ''),
            'nom_projet': project.get('name', ''),
            'date_derniere_analyse': None,
            'quality_gate_statut': 'ERROR'
        }


def extract_and_export_sonar_projects() -> str:
    """
    Point d'entrée principal pour l'extraction et export des projets
    
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
            
        # Enrichir la session avec l'URL de base pour l'extracteur
        if client.url:
            session.headers['base_url'] = client.url
        
        # Extraction des projets
        df = extract_sonar_projects(session)
        
        if df.empty:
            print("⚠️ Aucun projet à exporter")
            return ""
            
        # Export vers Excel
        from kenobi_tools.sonar.exporters.sonar_excel_exporter import export_projects_to_excel
        return export_projects_to_excel(df)
        
    except Exception as e:
        print(f"❌ Erreur extraction/export projets: {e}")
        return ""


if __name__ == "__main__":
    """Test direct de l'extracteur"""
    result = extract_and_export_sonar_projects()
    if result:
        print(f"✅ Export terminé: {result}")
    else:
        print("❌ Export échoué")
