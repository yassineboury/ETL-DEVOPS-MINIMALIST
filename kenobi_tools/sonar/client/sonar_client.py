"""
🎯 Client SonarQube - Gestionnaire de connexion
Responsable de l'authentification et de la validation des permissions
Architecture cohérente avec GitLab Client - Version requests pour SSL
"""

import os
import urllib3
import requests
from typing import Optional, Dict, Any

# Désactiver les warnings SSL pour l'environnement ONCF
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SonarClient:
    """
    Client SonarQube simplifié pour extraction ETL
    Utilise requests directement pour contrôler SSL
    """
    
    def __init__(self):
        self.url: Optional[str] = None
        self.token: Optional[str] = None
        self.session: Optional[requests.Session] = None
        
    def connect(self) -> Optional[requests.Session]:
        """
        Établit la connexion à SonarQube avec les credentials
        
        Returns:
            requests.Session ou None si échec
        """
        try:
            # Récupération des credentials
            self.url = os.getenv('SONAR_URL', 'https://sonar.oncf.net/').rstrip('/')
            self.token = os.getenv('SONAR_TOKEN')
            
            if not self.token:
                print("❌ SONAR_TOKEN non trouvé dans les variables d'environnement")
                return None
                
            print(f"🔗 Connexion à SonarQube: {self.url}")
            print("⚠️ Vérification SSL désactivée")
            
            # Création d'une session requests avec SSL désactivé
            self.session = requests.Session()
            self.session.verify = False  # Désactiver la vérification SSL
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            })
            
            # Test de connexion
            if self._validate_connection():
                print("✅ Connexion SonarQube établie")
                return self.session
            else:
                print("❌ Échec de validation de la connexion SonarQube")
                return None
                
        except Exception as e:
            print(f"❌ Erreur de connexion SonarQube: {e}")
            return None
    
    def _validate_connection(self) -> bool:
        """
        Valide la connexion en testant l'accès aux projets
        
        Returns:
            bool: True si connexion valide
        """
        try:
            if not self.session:
                return False
                
            # Test simple: récupérer la liste des projets (limité à 1)
            response = self.session.get(
                f"{self.url}/api/projects/search",
                params={'ps': 1, 'qualifiers': 'TRK'}
            )
            
            if response.status_code == 200:
                data = response.json()
                projects_count = len(data.get('components', []))
                print(f"🔍 Accès vérifié - {projects_count} projet(s) accessible(s)")
                return True
            else:
                print(f"❌ Validation échouée - Status: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Validation échouée: {e}")
            return False

    def get_projects(self, page_size: int = 100) -> Dict[str, Any]:
        """
        Récupère la liste des projets SonarQube
        
        Args:
            page_size: Nombre de projets par page
            
        Returns:
            dict: Réponse de l'API ou dict vide si erreur
        """
        try:
            if not self.session:
                return {}
                
            response = self.session.get(
                f"{self.url}/api/projects/search",
                params={'ps': page_size, 'qualifiers': 'TRK'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur récupération projets - Status: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erreur récupération projets: {e}")
            return {}

    def get_project_metrics(self, project_key: str, metrics: str) -> Dict[str, Any]:
        """
        Récupère les métriques d'un projet
        
        Args:
            project_key: Clé du projet
            metrics: Liste des métriques séparées par virgule
            
        Returns:
            dict: Métriques du projet ou dict vide si erreur
        """
        try:
            if not self.session:
                return {}
                
            response = self.session.get(
                f"{self.url}/api/measures/component",
                params={'component': project_key, 'metricKeys': metrics}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur métriques projet {project_key} - Status: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Erreur métriques projet {project_key}: {e}")
            return {}

    def get_server_info(self) -> Dict[str, Any]:
        """
        Récupère les informations du serveur SonarQube
        
        Returns:
            dict: Informations serveur ou dict vide si erreur
        """
        try:
            if not self.session:
                return {}
                
            return {
                'url': self.url,
                'status': 'connected',
                'client_version': 'requests-based'
            }
            
        except Exception as e:
            print(f"⚠️ Impossible de récupérer les infos serveur: {e}")
            return {'url': self.url, 'status': 'limited_access'}
