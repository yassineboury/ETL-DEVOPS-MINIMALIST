"""
Client de connexion GitLab
Module principal pour établir et gérer la connexion à GitLab
"""
import os
import sys
import gitlab
import yaml
import warnings
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Supprimer les warnings SSL et de pagination
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="gitlab")


class GitLabClient:
    """Client GitLab avec gestion de la connexion et des erreurs"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le client GitLab
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.config = None
        self.client = None
        self.is_connected = False
        
        # Charger les variables d'environnement
        load_dotenv()
        
        # Charger la configuration
        if config_path:
            self.config = self._load_config(config_path)
        else:
            self.config = self._load_default_config()
    
    def _load_config(self, config_path: str) -> Dict[Any, Any]:
        """
        Charge la configuration depuis un fichier YAML
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Configuration sous forme de dictionnaire
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            print(f"✅ Configuration chargée depuis: {config_path}")
            return config
        except FileNotFoundError:
            print(f"❌ Fichier de configuration introuvable: {config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"❌ Erreur de format YAML: {e}")
            raise
    
    def _load_default_config(self) -> Dict[Any, Any]:
        """
        Charge la configuration par défaut depuis config/config.yaml
        
        Returns:
            Configuration par défaut
        """
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        
        if not config_path.exists():
            print("❌ Fichier config/config.yaml introuvable")
            print("💡 Copiez config/config.example.yaml vers config/config.yaml")
            raise FileNotFoundError(f"Configuration manquante: {config_path}")
        
        return self._load_config(str(config_path))
    
    def connect(self, url: Optional[str] = None, token: Optional[str] = None) -> gitlab.Gitlab:
        """
        Établit la connexion à GitLab
        
        Args:
            url: URL de l'instance GitLab (optionnel, lu depuis config si non fourni)
            token: Token d'accès GitLab (optionnel, lu depuis env/config si non fourni)
            
        Returns:
            Client GitLab authentifié
            
        Raises:
            Exception: En cas d'erreur de connexion
        """
        try:
            # Déterminer l'URL
            gitlab_url = url or self.config.get('gitlab', {}).get('url')
            if not gitlab_url:
                raise ValueError("URL GitLab manquante dans la configuration")
            
            # Déterminer le token
            gitlab_token = (token or 
                          os.getenv('GITLAB_TOKEN') or 
                          self.config.get('gitlab', {}).get('token'))
            
            if not gitlab_token or gitlab_token.startswith('${'):
                raise ValueError("Token GitLab manquant. Vérifiez votre fichier .env ou la configuration")
            
            # Créer le client GitLab
            print(f"🔗 Connexion à GitLab: {gitlab_url}")
            
            # Créer le client avec vérification SSL désactivée pour les instances internes
            if "oncf.net" in gitlab_url.lower() or "localhost" in gitlab_url.lower():
                print("⚠️ Désactivation de la vérification SSL pour instance interne")
                self.client = gitlab.Gitlab(gitlab_url, private_token=gitlab_token, ssl_verify=False)
            else:
                self.client = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
            
            # Tester la connexion en récupérant l'utilisateur actuel
            try:
                # Première méthode : via self.client.user
                if hasattr(self.client, 'user') and self.client.user:
                    current_user = self.client.users.get(self.client.user.id)
                else:
                    # Deuxième méthode : via l'API directement
                    current_user = self.client.user
                
                if current_user:
                    print(f"✅ Connexion GitLab réussie")
                    print(f"👤 Utilisateur connecté: {getattr(current_user, 'name', 'N/A')} (@{getattr(current_user, 'username', 'N/A')})")
                    print(f"🏢 Instance: {gitlab_url}")
                else:
                    # Test alternatif : essayer de lister les projets
                    projects = self.client.projects.list(per_page=1, get_all=False)
                    print(f"✅ Connexion GitLab réussie (test via projets)")
                    print(f"🏢 Instance: {gitlab_url}")
                    print(f"📊 Accès confirmé via API")
                    
            except Exception as auth_error:
                print(f"❌ Erreur lors de la vérification utilisateur: {auth_error}")
                # Test final : essayer une requête simple
                try:
                    version = self.client.version()
                    print(f"✅ Connexion GitLab réussie (test via version)")
                    print(f"🏢 Instance: {gitlab_url}")
                    print(f"📊 Version GitLab: {version}")
                except:
                    raise
            
            self.is_connected = True
            return self.client
            
        except gitlab.GitlabAuthenticationError as e:
            print(f"❌ Erreur d'authentification GitLab: {e}")
            print("💡 Vérifiez votre token d'accès")
            raise
        except gitlab.GitlabGetError as e:
            print(f"❌ Erreur d'accès GitLab: {e}")
            raise
        except Exception as e:
            print(f"❌ Erreur de connexion GitLab: {e}")
            raise
    
    def get_client(self) -> gitlab.Gitlab:
        """
        Retourne le client GitLab (se connecte automatiquement si nécessaire)
        
        Returns:
            Client GitLab authentifié
        """
        if not self.is_connected or not self.client:
            self.connect()
        return self.client
    
    def test_connection(self) -> bool:
        """
        Teste la connexion GitLab
        
        Returns:
            True si la connexion est OK, False sinon
        """
        try:
            client = self.get_client()
            
            # Essayer plusieurs méthodes de test
            try:
                if hasattr(client, 'user') and client.user:
                    client.users.get(client.user.id)
                    print("✅ Test de connexion GitLab: OK")
                    return True
                else:
                    # Test alternatif : lister les projets
                    client.projects.list(per_page=1, get_all=False)
                    print("✅ Test de connexion GitLab: OK (via projets)")
                    return True
            except:
                # Test final : version de l'API
                client.version()
                print("✅ Test de connexion GitLab: OK (via version)")
                return True
                
        except Exception as e:
            print(f"❌ Test de connexion GitLab: ÉCHEC - {e}")
            return False
    
    def get_instance_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur l'instance GitLab
        
        Returns:
            Dictionnaire avec les informations de l'instance
        """
        try:
            client = self.get_client()
            version = client.version()
            
            info: Dict[str, Any] = {
                'version': version,
            }
            
            # Essayer de récupérer les statistiques si disponibles (admin seulement)
            try:
                statistics = client.statistics.get()
                
                # Les vraies statistiques sont dans l'attribut 'attributes' ou directement accessibles
                if hasattr(statistics, 'attributes') and statistics.attributes:
                    # Format ONCF GitLab
                    attrs = statistics.attributes
                    info.update({
                        'total_projects': int(attrs.get('projects', 0).replace(',', '')),
                        'total_users': int(attrs.get('users', 0).replace(',', '')),
                        'active_users': int(attrs.get('active_users', 0).replace(',', '')),
                        'total_groups': int(attrs.get('groups', 0).replace(',', '')),
                        'total_issues': int(attrs.get('issues', 0).replace(',', '')),
                        'total_merge_requests': int(attrs.get('merge_requests', 0).replace(',', '')),
                        'total_notes': int(attrs.get('notes', 0).replace(',', '')),
                        'total_snippets': int(attrs.get('snippets', 0).replace(',', '')),
                        'total_ssh_keys': int(attrs.get('ssh_keys', 0).replace(',', '')),
                        'total_forks': int(attrs.get('forks', 0).replace(',', '')),
                        'total_milestones': int(attrs.get('milestones', 0).replace(',', '')),
                    })
                elif hasattr(statistics, 'projects'):
                    # Accès direct aux attributs
                    info.update({
                        'total_projects': getattr(statistics, 'projects', 0),
                        'total_users': getattr(statistics, 'users', 0),
                        'active_users': getattr(statistics, 'active_users', 0),
                        'total_groups': getattr(statistics, 'groups', 0),
                        'total_issues': getattr(statistics, 'issues', 0),
                        'total_merge_requests': getattr(statistics, 'merge_requests', 0),
                        'total_notes': getattr(statistics, 'notes', 0),
                    })
                else:
                    # Fallback vers format standard
                    info.update({
                        'projects_count': getattr(statistics, 'counts', {}).get('projects', 0),
                        'users_count': getattr(statistics, 'counts', {}).get('users', 0),
                        'groups_count': getattr(statistics, 'counts', {}).get('groups', 0),
                        'issues_count': getattr(statistics, 'counts', {}).get('issues', 0),
                        'merge_requests_count': getattr(statistics, 'counts', {}).get('merge_requests', 0),
                    })
                    
                print("📊 Statistiques globales disponibles")
                    
            except Exception as stats_error:
                print("⚠️ Statistiques administrateur non disponibles (permissions insuffisantes)")
                
                # Récupérer les statistiques basées sur l'accès utilisateur
                try:
                    # Compter les projets accessibles
                    projects_sample = client.projects.list(get_all=False, per_page=100)
                    total_projects = len(client.projects.list(all=True))
                    info['accessible_projects_count'] = total_projects
                    
                    # Compter les groupes accessibles
                    try:
                        groups_sample = client.groups.list(get_all=False, per_page=100)
                        total_groups = len(client.groups.list(all=True))
                        info['accessible_groups_count'] = total_groups
                    except:
                        info['accessible_groups_count'] = 0
                        
                    # Essayer de récupérer des infos sur l'utilisateur actuel
                    try:
                        current_user = client.user
                        if current_user:
                            info['current_user'] = {
                                'username': getattr(current_user, 'username', 'N/A'),
                                'name': getattr(current_user, 'name', 'N/A'),
                                'is_admin': getattr(current_user, 'is_admin', False)
                            }
                    except:
                        pass
                        
                    print(f"📊 Statistiques utilisateur (ce que vous pouvez voir)")
                    
                except Exception as user_stats_error:
                    print(f"❌ Impossible de récupérer les statistiques utilisateur: {user_stats_error}")
                    info['projects_accessible'] = False
            
            print("📊 Informations de l'instance GitLab:")
            for key, value in info.items():
                if isinstance(value, dict):
                    print(f"   {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"     {sub_key}: {sub_value}")
                else:
                    print(f"   {key}: {value}")
            
            return info
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des informations: {e}")
            return {}
    
    def get_accessible_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques basées sur ce qui est accessible à l'utilisateur
        
        Returns:
            Dictionnaire avec les statistiques accessibles
        """
        try:
            client = self.get_client()
            stats = {}
            
            print("🔍 Analyse des ressources accessibles...")
            
            # Projets accessibles
            try:
                all_projects = client.projects.list(all=True)
                stats['accessible_projects'] = len(all_projects)
                
                # Analyser les types de projets
                public_count = sum(1 for p in all_projects if getattr(p, 'visibility', '') == 'public')
                private_count = sum(1 for p in all_projects if getattr(p, 'visibility', '') == 'private')
                internal_count = sum(1 for p in all_projects if getattr(p, 'visibility', '') == 'internal')
                
                stats['projects_by_visibility'] = {
                    'public': public_count,
                    'internal': internal_count,
                    'private': private_count
                }
                
                # Projets récents (dernière activité)
                from datetime import datetime, timedelta
                thirty_days_ago = datetime.now() - timedelta(days=30)
                active_projects = []
                for p in all_projects[:50]:  # Limiter pour éviter trop d'appels API
                    try:
                        if hasattr(p, 'last_activity_at') and p.last_activity_at:
                            # Parser la date ISO
                            last_activity = datetime.fromisoformat(p.last_activity_at.replace('Z', '+00:00'))
                            if last_activity > thirty_days_ago.replace(tzinfo=last_activity.tzinfo):
                                active_projects.append(p)
                    except:
                        continue
                
                stats['active_projects_last_30_days'] = len(active_projects)
                
                print(f"   📁 {stats['accessible_projects']} projets accessibles")
                print(f"   📊 Publics: {public_count}, Internes: {internal_count}, Privés: {private_count}")
                print(f"   🔥 {len(active_projects)} projets actifs (30 derniers jours)")
                
            except Exception as proj_error:
                print(f"   ❌ Erreur projets: {proj_error}")
                stats['accessible_projects'] = 0
            
            # Groupes accessibles
            try:
                all_groups = client.groups.list(all=True)
                stats['accessible_groups'] = len(all_groups)
                print(f"   👥 {stats['accessible_groups']} groupes accessibles")
            except Exception as groups_error:
                print(f"   ⚠️ Groupes non accessibles: {groups_error}")
                stats['accessible_groups'] = 0
            
            # Informations utilisateur
            try:
                current_user = client.user
                if current_user:
                    stats['current_user_info'] = {
                        'username': getattr(current_user, 'username', 'N/A'),
                        'name': getattr(current_user, 'name', 'N/A'),
                        'is_admin': getattr(current_user, 'is_admin', False),
                        'can_create_group': getattr(current_user, 'can_create_group', False),
                        'can_create_project': getattr(current_user, 'can_create_project', False),
                    }
                    user_info = stats['current_user_info']
                    print(f"   👤 Utilisateur: {user_info['name']} (@{user_info['username']})")
                    print(f"   🔑 Admin: {user_info['is_admin']}, Créer projets: {user_info['can_create_project']}")
            except Exception as user_error:
                print(f"   ⚠️ Info utilisateur non disponible: {user_error}")
            
            return stats
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse des statistiques: {e}")
            return {}

    def disconnect(self):
        """Ferme la connexion GitLab"""
        if self.client:
            self.client = None
            self.is_connected = False
            print("🔌 Connexion GitLab fermée")


# Fonction utilitaire pour créer rapidement un client
def create_gitlab_client(config_path: Optional[str] = None) -> GitLabClient:
    """
    Crée et retourne un client GitLab configuré
    
    Args:
        config_path: Chemin vers le fichier de configuration (optionnel)
        
    Returns:
        Instance de GitLabClient
    """
    return GitLabClient(config_path)


# Fonction pour tester la connexion rapidement
def test_gitlab_connection(config_path: Optional[str] = None) -> bool:
    """
    Teste rapidement la connexion GitLab
    
    Args:
        config_path: Chemin vers le fichier de configuration (optionnel)
        
    Returns:
        True si la connexion fonctionne, False sinon
    """
    try:
        client = create_gitlab_client(config_path)
        return client.test_connection()
    except Exception as e:
        print(f"❌ Erreur lors du test de connexion: {e}")
        return False


if __name__ == "__main__":
    """Test du module de connexion GitLab"""
    print("🧪 Test du module de connexion GitLab")
    print("="*50)
    
    try:
        # Créer le client
        gitlab_client = create_gitlab_client()
        
        # Tester la connexion
        if gitlab_client.test_connection():
            # Afficher les infos de l'instance
            gitlab_client.get_instance_info()
        
        # Fermer la connexion
        gitlab_client.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        sys.exit(1)
